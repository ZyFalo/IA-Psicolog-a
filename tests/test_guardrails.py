"""
Tests para el sistema de Guardrails
"""

import pytest
from app.core.guardrails import CrisisDetector, ContentFilter, GuardrailsEngine, RiskLevel
from app.config import Settings


@pytest.fixture
def config():
    return Settings()


@pytest.fixture
def crisis_detector(config):
    return CrisisDetector(config)


@pytest.fixture
def content_filter(config):
    return ContentFilter(config)


@pytest.fixture
def guardrails_engine(config):
    return GuardrailsEngine(config)


class TestCrisisDetector:
    """Tests para detección de crisis"""
    
    def test_detect_suicidal_ideation(self, crisis_detector):
        """Detecta ideación suicida explícita"""
        text = "Quiero matarme, no puedo más"
        result = crisis_detector.detect_crisis(text)
        
        assert result.risk_level in [RiskLevel.HIGH, RiskLevel.CRITICAL]
        assert result.should_terminate or not result.is_safe
        assert result.emergency_response is not None
    
    def test_detect_self_harm(self, crisis_detector):
        """Detecta autolesión"""
        text = "Me corto cuando me siento mal"
        result = crisis_detector.detect_crisis(text)
        
        assert result.risk_level in [RiskLevel.MEDIUM, RiskLevel.HIGH, RiskLevel.CRITICAL]
        assert len(result.triggered_rules) > 0
    
    def test_normal_conversation_low_risk(self, crisis_detector):
        """Conversación normal debe ser bajo riesgo"""
        text = "Hola, estoy estresado con los exámenes"
        result = crisis_detector.detect_crisis(text)
        
        assert result.risk_level == RiskLevel.LOW
        assert result.is_safe
        assert not result.should_terminate
    
    def test_medium_stress_detected(self, crisis_detector):
        """Detecta estrés elevado sin crisis"""
        text = "No puedo dormir, estoy muy ansioso todo el tiempo"
        result = crisis_detector.detect_crisis(text)
        
        assert result.risk_level in [RiskLevel.LOW, RiskLevel.MEDIUM]
        assert result.is_safe


class TestContentFilter:
    """Tests para filtro de contenido"""
    
    def test_reject_diagnosis(self, content_filter):
        """Rechaza respuestas con diagnósticos"""
        response = "Creo que tienes depresión clínica"
        is_valid, violations = content_filter.validate_response(response)
        
        assert not is_valid
        assert len(violations) > 0
    
    def test_reject_prescription(self, content_filter):
        """Rechaza prescripciones"""
        response = "Te prescribo tomar este medicamento"
        is_valid, violations = content_filter.validate_response(response)
        
        assert not is_valid
    
    def test_accept_psychoeducation(self, content_filter):
        """Acepta contenido psicoeducativo apropiado"""
        response = "La técnica de respiración 4-7-8 puede ayudarte a calmarte"
        is_valid, violations = content_filter.validate_response(response)
        
        assert is_valid
        assert len(violations) == 0
    
    def test_accept_empathetic_response(self, content_filter):
        """Acepta respuestas empáticas"""
        response = "Entiendo que te sientes abrumado. Es normal sentir estrés ante los exámenes."
        is_valid, violations = content_filter.validate_response(response)
        
        assert is_valid


class TestGuardrailsEngine:
    """Tests para el motor completo de guardrails"""
    
    def test_crisis_input_triggers_emergency(self, guardrails_engine):
        """Input de crisis activa respuesta de emergencia"""
        text = "Voy a acabar con mi vida"
        result = guardrails_engine.check_input(text)
        
        assert result.risk_level == RiskLevel.CRITICAL
        assert result.should_terminate
        assert "988" in result.emergency_response
        assert "911" in result.emergency_response
    
    def test_normal_input_passes(self, guardrails_engine):
        """Input normal pasa el filtro"""
        text = "Hola, necesito ayuda con el estrés"
        result = guardrails_engine.check_input(text)
        
        assert result.is_safe
        assert not result.should_terminate
    
    def test_inappropriate_output_rejected(self, guardrails_engine):
        """Output inapropiado es rechazado"""
        response = "Creo que tienes un trastorno de ansiedad"
        is_valid, violations = guardrails_engine.check_output(response)
        
        assert not is_valid
    
    def test_appropriate_output_accepted(self, guardrails_engine):
        """Output apropiado es aceptado"""
        response = "Te comparto la técnica de grounding 5-4-3-2-1 que puede ayudarte"
        is_valid, violations = guardrails_engine.check_output(response)
        
        assert is_valid
    
    def test_fallback_response_available(self, guardrails_engine):
        """Respuesta de fallback está disponible"""
        fallback = guardrails_engine.get_fallback_response()
        
        assert fallback is not None
        assert len(fallback) > 0


# Tests de integración
class TestGuardrailsIntegration:
    """Tests de integración del sistema completo"""
    
    @pytest.mark.parametrize("crisis_text,expected_level", [
        ("quiero suicidarme", RiskLevel.CRITICAL),
        ("me voy a matar", RiskLevel.CRITICAL),
        ("no quiero vivir más", RiskLevel.CRITICAL),
        ("me corto los brazos", RiskLevel.HIGH),
    ])
    def test_various_crisis_scenarios(self, guardrails_engine, crisis_text, expected_level):
        """Prueba varios escenarios de crisis"""
        result = guardrails_engine.check_input(crisis_text)
        
        assert result.risk_level.value in ["high", "critical"]
        assert result.emergency_response is not None
    
    @pytest.mark.parametrize("safe_text", [
        "Hola, ¿cómo estás?",
        "Estoy estresado con los exámenes",
        "No puedo dormir bien últimamente",
        "Me siento triste hoy",
    ])
    def test_safe_conversations(self, guardrails_engine, safe_text):
        """Prueba conversaciones seguras"""
        result = guardrails_engine.check_input(safe_text)
        
        assert result.is_safe
        assert not result.should_terminate
