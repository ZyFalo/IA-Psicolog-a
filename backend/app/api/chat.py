"""
Chat API endpoints
"""

from fastapi import APIRouter, HTTPException, Depends
from pydantic import BaseModel
from typing import Optional, List, Dict
import logging

from app.core.model_manager_mlx import ModelManagerMLX
from app.core.session_manager import SessionManager
from app.core.guardrails import GuardrailsEngine, RiskLevel

logger = logging.getLogger(__name__)

router = APIRouter()

# Dependencias (se inyectarán desde main.py)
def get_model_manager() -> ModelManagerMLX:
    from app.main import model_manager
    return model_manager

def get_session_manager() -> SessionManager:
    from app.main import session_manager
    return session_manager


class ChatRequest(BaseModel):
    """Request para chat"""
    session_id: Optional[str] = None
    message: str
    metadata: Optional[Dict] = None


class ChatResponse(BaseModel):
    """Response del chat"""
    session_id: str
    response: str
    risk_level: str
    is_crisis: bool
    emergency_response: Optional[str] = None


@router.post("/message", response_model=ChatResponse)
async def send_message(
    request: ChatRequest,
    model_manager: ModelManagerMLX = Depends(get_model_manager),
    session_manager: SessionManager = Depends(get_session_manager)
):
    """
    Envía mensaje y obtiene respuesta del asistente
    """
    try:
        # Crear o recuperar sesión
        session_id = request.session_id
        if not session_id or not session_manager.get_session(session_id):
            session_id = session_manager.create_session()
            logger.info(f"🆕 Nueva sesión creada: {session_id}")
        
        # Inicializar guardrails
        from app.config import settings
        guardrails = GuardrailsEngine(settings)
        
        # PRE-FILTRO: Detectar crisis en input
        input_check = guardrails.check_input(request.message)
        
        # Si es crisis crítica, retornar respuesta de emergencia
        if input_check.should_terminate:
            logger.warning(
                f"🚨 CRISIS DETECTADA en sesión {session_id}: "
                f"{input_check.triggered_rules}"
            )
            
            # Guardar en sesión
            session_manager.add_message(
                session_id,
                "user",
                request.message,
                {"risk_level": input_check.risk_level.value}
            )
            session_manager.add_message(
                session_id,
                "assistant",
                input_check.emergency_response,
                {"is_emergency": True}
            )
            
            return ChatResponse(
                session_id=session_id,
                response=input_check.emergency_response,
                risk_level=input_check.risk_level.value,
                is_crisis=True,
                emergency_response=input_check.emergency_response
            )
        
        # Añadir mensaje del usuario
        session_manager.add_message(
            session_id,
            "user",
            request.message,
            request.metadata
        )
        
        # Obtener mensajes formateados
        messages = session_manager.get_conversation_history(session_id)
        
        # Generar respuesta
        logger.info(f"🤖 Generando respuesta para sesión {session_id}")
        response = model_manager.generate_chat(messages)
        
        # POST-FILTRO: Validar respuesta
        is_valid, violated_rules = guardrails.check_output(response)
        
        if not is_valid:
            logger.warning(
                f"⚠️  Respuesta inválida, usando fallback: {violated_rules}"
            )
            response = guardrails.get_fallback_response()
        
        # Guardar respuesta
        session_manager.add_message(
            session_id,
            "assistant",
            response
        )
        
        # Limpiar sesiones expiradas (background)
        session_manager.cleanup_expired_sessions()
        
        return ChatResponse(
            session_id=session_id,
            response=response,
            risk_level=input_check.risk_level.value,
            is_crisis=False
        )
        
    except Exception as e:
        logger.error(f"❌ Error en chat: {e}", exc_info=True)
        raise HTTPException(status_code=500, detail=str(e))


@router.get("/sessions/{session_id}/history")
async def get_history(
    session_id: str,
    session_manager: SessionManager = Depends(get_session_manager)
):
    """Obtiene historial de conversación"""
    history = session_manager.get_conversation_history(session_id)
    
    if not history:
        raise HTTPException(status_code=404, detail="Sesión no encontrada")
    
    return {"session_id": session_id, "messages": history}


@router.post("/sessions")
async def create_session(
    session_manager: SessionManager = Depends(get_session_manager)
):
    """Crea nueva sesión de chat"""
    session_id = session_manager.create_session()
    return {"session_id": session_id}
