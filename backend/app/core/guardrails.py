"""
Guardrails - Sistema de seguridad y detección de crisis
"""

import logging
import re
from typing import Dict, Tuple, Optional
from dataclasses import dataclass
from enum import Enum

logger = logging.getLogger(__name__)


class RiskLevel(Enum):
    """Niveles de riesgo"""
    LOW = "low"
    MEDIUM = "medium"
    HIGH = "high"
    CRITICAL = "critical"


@dataclass
class GuardrailResult:
    """Resultado de evaluación de guardrails"""
    is_safe: bool
    risk_level: RiskLevel
    triggered_rules: list
    should_terminate: bool
    emergency_response: Optional[str] = None


class CrisisDetector:
    """Detector de crisis y riesgo"""
    
    def __init__(self, config):
        self.config = config
        self.crisis_keywords = config.CRISIS_KEYWORDS
        self.risk_threshold = config.RISK_THRESHOLD
        
        # Patrones de crisis
        self.crisis_patterns = [
            r"quiero\s+(morir|morirme|suicidar|suicidarme)",
            r"voy\s+a\s+(matar|suicidar)",
            r"plan\s+para\s+(morir|suicidarme|matarme)",
            r"no\s+quiero\s+(vivir|seguir\s+viviendo)",
            r"(cortar|hacer\s+daño|lastimar)me",
            r"acabar\s+con\s+(mi\s+vida|todo)",
        ]
        
        self.compiled_patterns = [
            re.compile(pattern, re.IGNORECASE)
            for pattern in self.crisis_patterns
        ]
    
    def detect_crisis(self, text: str) -> GuardrailResult:
        """
        Detecta indicios de crisis en el texto
        
        Args:
            text: Texto a analizar
            
        Returns:
            GuardrailResult con nivel de riesgo y acción recomendada
        """
        triggered_rules = []
        risk_score = 0.0
        
        # 1. Búsqueda de keywords
        text_lower = text.lower()
        for keyword in self.crisis_keywords:
            if keyword in text_lower:
                triggered_rules.append(f"keyword: {keyword}")
                risk_score += 0.3
        
        # 2. Búsqueda de patrones
        for i, pattern in enumerate(self.compiled_patterns):
            if pattern.search(text):
                triggered_rules.append(f"pattern: crisis_{i}")
                risk_score += 0.5
        
        # 3. Determinar nivel de riesgo
        if risk_score >= 0.8:
            risk_level = RiskLevel.CRITICAL
        elif risk_score >= 0.5:
            risk_level = RiskLevel.HIGH
        elif risk_score >= 0.2:
            risk_level = RiskLevel.MEDIUM
        else:
            risk_level = RiskLevel.LOW
        
        # 4. Decidir acción
        is_safe = risk_level in [RiskLevel.LOW, RiskLevel.MEDIUM]
        should_terminate = risk_level == RiskLevel.CRITICAL
        
        emergency_response = None
        if risk_level in [RiskLevel.HIGH, RiskLevel.CRITICAL]:
            emergency_response = self._build_emergency_response()
        
        logger.info(
            f"🔍 Crisis detection: risk_level={risk_level.value}, "
            f"score={risk_score:.2f}, rules={len(triggered_rules)}"
        )
        
        return GuardrailResult(
            is_safe=is_safe,
            risk_level=risk_level,
            triggered_rules=triggered_rules,
            should_terminate=should_terminate,
            emergency_response=emergency_response
        )
    
    def _build_emergency_response(self) -> str:
        """Construye respuesta de emergencia"""
        return f"""🚨 **Detecto que estás pasando por un momento muy difícil**

Tu seguridad es lo más importante. Por favor, contacta **inmediatamente** con ayuda profesional:

📞 **Línea Nacional de Prevención del Suicidio:** {self.config.SUICIDE_HOTLINE}
💬 **Línea de Crisis por texto:** Envía "HOLA" al {self.config.CRISIS_TEXT}
🏥 **Emergencias:** {self.config.EMERGENCY}

**Estos servicios están disponibles 24/7 y hay profesionales esperando para ayudarte ahora mismo.**

No estás solo/a. La ayuda profesional está disponible y puede marcar la diferencia.

---

*Este asistente no puede proporcionar ayuda en crisis. Por favor, contacta los servicios listados arriba.*
"""


class ContentFilter:
    """Filtro de contenido inapropiado en respuestas"""
    
    def __init__(self, config):
        self.config = config
        
        # Patrones que NO deben aparecer en respuestas
        self.forbidden_patterns = [
            r"diagnóstico\s+de",
            r"tienes\s+(depresión|ansiedad|trastorno)",
            r"prescribo",
            r"toma\s+(medicamento|medicina)",
            r"dosis\s+de",
        ]
        
        self.compiled_forbidden = [
            re.compile(pattern, re.IGNORECASE)
            for pattern in self.forbidden_patterns
        ]
    
    def validate_response(self, response: str) -> Tuple[bool, list]:
        """
        Valida que la respuesta no contenga contenido prohibido
        
        Args:
            response: Respuesta del modelo
            
        Returns:
            (is_valid, violated_rules)
        """
        violated_rules = []
        
        # Buscar patrones prohibidos
        for i, pattern in enumerate(self.compiled_forbidden):
            if pattern.search(response):
                violated_rules.append(f"forbidden_pattern_{i}")
        
        is_valid = len(violated_rules) == 0
        
        if not is_valid:
            logger.warning(
                f"⚠️  Respuesta violó reglas de contenido: {violated_rules}"
            )
        
        return is_valid, violated_rules


class GuardrailsEngine:
    """Motor principal de guardrails"""
    
    def __init__(self, config):
        self.config = config
        self.crisis_detector = CrisisDetector(config)
        self.content_filter = ContentFilter(config)
    
    def check_input(self, text: str) -> GuardrailResult:
        """
        Verifica input del usuario (pre-filtro)
        
        Args:
            text: Texto del usuario
            
        Returns:
            GuardrailResult
        """
        if not self.config.ENABLE_CRISIS_DETECTION:
            return GuardrailResult(
                is_safe=True,
                risk_level=RiskLevel.LOW,
                triggered_rules=[],
                should_terminate=False
            )
        
        return self.crisis_detector.detect_crisis(text)
    
    def check_output(self, response: str) -> Tuple[bool, list]:
        """
        Verifica respuesta del modelo (post-filtro)
        
        Args:
            response: Respuesta generada
            
        Returns:
            (is_valid, violated_rules)
        """
        return self.content_filter.validate_response(response)
    
    def get_fallback_response(self) -> str:
        """Respuesta de fallback si el modelo genera algo inapropiado"""
        return (
            "Disculpa, no puedo responder eso de manera apropiada. "
            "¿Hay algo más en lo que pueda ayudarte con orientación psicoeducativa?"
        )
