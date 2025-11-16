"""
Session Manager - Gestión de sesiones y contexto conversacional
"""

import logging
from typing import Dict, List, Optional
from datetime import datetime, timedelta
from dataclasses import dataclass, field
import uuid

logger = logging.getLogger(__name__)


@dataclass
class Message:
    """Mensaje individual en la conversación"""
    role: str  # system, user, assistant
    content: str
    timestamp: datetime = field(default_factory=datetime.now)
    metadata: Dict = field(default_factory=dict)


@dataclass
class Session:
    """Sesión de conversación"""
    session_id: str
    messages: List[Message] = field(default_factory=list)
    created_at: datetime = field(default_factory=datetime.now)
    last_activity: datetime = field(default_factory=datetime.now)
    metadata: Dict = field(default_factory=dict)
    
    def add_message(self, role: str, content: str, metadata: Dict = None):
        """Añade mensaje a la sesión"""
        msg = Message(role=role, content=content, metadata=metadata or {})
        self.messages.append(msg)
        self.last_activity = datetime.now()
    
    def get_context_window(self, max_messages: int = 10) -> List[Message]:
        """Obtiene ventana de contexto reciente"""
        return self.messages[-max_messages:]
    
    def is_expired(self, timeout: int) -> bool:
        """Verifica si la sesión ha expirado"""
        return (datetime.now() - self.last_activity) > timedelta(seconds=timeout)
    
    def needs_summary(self, trigger: int) -> bool:
        """Verifica si necesita resumen"""
        return len(self.messages) >= trigger


class SessionManager:
    """Gestiona múltiples sesiones de usuario"""
    
    def __init__(self, config):
        self.config = config
        self.sessions: Dict[str, Session] = {}
        self.system_prompt = self._build_system_prompt()
    
    def _build_system_prompt(self) -> str:
        """Construye el prompt de sistema base"""
        return """Eres un asistente de psicoeducación empático y profesional. 

DIRECTRICES:
1. Siempre comienza con un breve check-in empático
2. Detecta señales emocionales en lo que la persona dice
3. Ofrece orientaciones prácticas y breves (respiración 4-7-8, grounding 5-4-3-2-1, higiene del sueño, metas SMART)
4. NO diagnostiques ni prescribas
5. Mantén respuestas claras, respetuosas y motivantes
6. Si detectas riesgo de crisis (autolesión, suicidio), activa protocolo de derivación

TÉCNICAS QUE PUEDES ENSEÑAR:
- Respiración 4-7-8: Inhala 4 seg, retén 7 seg, exhala 8 seg
- Grounding 5-4-3-2-1: 5 cosas que ves, 4 que tocas, 3 que oyes, 2 que hueles, 1 que saboreas
- Higiene del sueño: Rutinas, horarios, ambiente
- Metas SMART: Específicas, Medibles, Alcanzables, Relevantes, Temporales
- Regulación emocional básica

LÍMITES:
- No eres terapeuta ni psicólogo
- No puedes diagnosticar condiciones
- No puedes prescribir tratamientos
- Ante crisis, deriva inmediatamente a profesionales
"""
    
    def create_session(self) -> str:
        """Crea nueva sesión"""
        session_id = str(uuid.uuid4())
        session = Session(session_id=session_id)
        
        # Añadir prompt de sistema
        session.add_message("system", self.system_prompt)
        
        self.sessions[session_id] = session
        logger.info(f"✅ Sesión creada: {session_id}")
        
        return session_id
    
    def get_session(self, session_id: str) -> Optional[Session]:
        """Obtiene sesión por ID"""
        return self.sessions.get(session_id)
    
    def add_message(
        self,
        session_id: str,
        role: str,
        content: str,
        metadata: Dict = None
    ):
        """Añade mensaje a sesión existente"""
        session = self.get_session(session_id)
        if not session:
            raise ValueError(f"Sesión no encontrada: {session_id}")
        
        session.add_message(role, content, metadata)
    
    def get_conversation_history(
        self,
        session_id: str,
        max_messages: int = None
    ) -> List[Dict]:
        """Obtiene historial de conversación formateado"""
        session = self.get_session(session_id)
        if not session:
            return []
        
        messages = session.messages
        if max_messages:
            messages = session.get_context_window(max_messages)
        
        return [
            {
                "role": msg.role,
                "content": msg.content,
                "timestamp": msg.timestamp.isoformat()
            }
            for msg in messages
        ]
    
    def _generate_summary(self, messages: List[Message]) -> str:
        """
        Genera resumen de mensajes antiguos
        En producción, usarías el modelo para esto
        """
        topics = []
        emotions = []
        
        for msg in messages:
            if msg.role == "user":
                content_lower = msg.content.lower()
                # Detectar emociones mencionadas
                if any(word in content_lower for word in ['ansiedad', 'ansioso', 'nervioso']):
                    emotions.append('ansiedad')
                if any(word in content_lower for word in ['triste', 'depresión', 'deprimido']):
                    emotions.append('tristeza')
                if any(word in content_lower for word in ['estrés', 'estresado', 'agobiado']):
                    emotions.append('estrés')
        
        # Construir resumen
        summary = "RESUMEN DE CONVERSACIÓN PREVIA:\n"
        if emotions:
            unique_emotions = list(set(emotions))
            summary += f"- Emociones discutidas: {', '.join(unique_emotions)}\n"
        summary += f"- Número de intercambios previos: {len([m for m in messages if m.role == 'user'])}\n"
        summary += "- El usuario ha compartido información personal y emocional que debe ser recordada.\n"
        
        return summary
    
    def format_for_model(self, session_id: str, max_context: int = 20, summary_threshold: int = 40) -> str:
        """
        Formatea conversación para el modelo con resúmenes automáticos
        
        Args:
            session_id: ID de la sesión
            max_context: Máximo de mensajes recientes a incluir completos
            summary_threshold: Cuando se supera, se genera resumen de mensajes antiguos
        """
        session = self.get_session(session_id)
        if not session:
            return ""
        
        messages = session.messages
        system_msg = messages[0] if messages and messages[0].role == "system" else None
        conversation_msgs = [m for m in messages if m.role != "system"]
        
        # Determinar si necesita resumen
        if len(conversation_msgs) > summary_threshold:
            # Resumir primeros N mensajes
            messages_to_summarize = conversation_msgs[:summary_threshold - max_context]
            recent_messages = conversation_msgs[-(max_context):]
            
            summary = self._generate_summary(messages_to_summarize)
            
            # Construir prompt con resumen
            formatted = ""
            if system_msg:
                formatted += f"<|im_start|>system\n{system_msg.content}\n\n{summary}<|im_end|>\n"
            
            for msg in recent_messages:
                if msg.role == "user":
                    formatted += f"<|im_start|>user\n{msg.content}<|im_end|>\n"
                elif msg.role == "assistant":
                    formatted += f"<|im_start|>assistant\n{msg.content}<|im_end|>\n"
        else:
            # Conversación corta, incluir todo
            recent_messages = conversation_msgs[-max_context:] if len(conversation_msgs) > max_context else conversation_msgs
            
            formatted = ""
            if system_msg:
                formatted += f"<|im_start|>system\n{system_msg.content}<|im_end|>\n"
            
            for msg in recent_messages:
                if msg.role == "user":
                    formatted += f"<|im_start|>user\n{msg.content}<|im_end|>\n"
                elif msg.role == "assistant":
                    formatted += f"<|im_start|>assistant\n{msg.content}<|im_end|>\n"
        
        # Preparar para siguiente respuesta
        formatted += "<|im_start|>assistant\n"
        
        return formatted
    
    def cleanup_expired_sessions(self):
        """Limpia sesiones expiradas"""
        timeout = self.config.SESSION_TIMEOUT
        expired = [
            sid for sid, session in self.sessions.items()
            if session.is_expired(timeout)
        ]
        
        for sid in expired:
            del self.sessions[sid]
            logger.info(f"🗑️  Sesión expirada eliminada: {sid}")
        
        if expired:
            logger.info(f"🧹 {len(expired)} sesiones eliminadas")
    
    async def cleanup(self):
        """Limpieza al cerrar"""
        logger.info("🧹 Limpiando sesiones...")
        self.sessions.clear()
