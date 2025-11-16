"""
Tests para Session Manager
"""

import pytest
from datetime import datetime, timedelta
from app.core.session_manager import SessionManager, Session, Message
from app.config import Settings


@pytest.fixture
def config():
    return Settings()


@pytest.fixture
def session_manager(config):
    return SessionManager(config)


class TestSession:
    """Tests para la clase Session"""
    
    def test_create_session(self):
        """Crea sesión nueva"""
        session = Session(session_id="test-123")
        
        assert session.session_id == "test-123"
        assert len(session.messages) == 0
        assert session.created_at <= datetime.now()
    
    def test_add_message(self):
        """Añade mensaje a sesión"""
        session = Session(session_id="test-123")
        session.add_message("user", "Hola")
        
        assert len(session.messages) == 1
        assert session.messages[0].role == "user"
        assert session.messages[0].content == "Hola"
    
    def test_context_window(self):
        """Obtiene ventana de contexto"""
        session = Session(session_id="test-123")
        
        # Añadir 15 mensajes
        for i in range(15):
            session.add_message("user", f"Mensaje {i}")
        
        # Obtener últimos 10
        window = session.get_context_window(max_messages=10)
        
        assert len(window) == 10
        assert window[0].content == "Mensaje 5"
        assert window[-1].content == "Mensaje 14"
    
    def test_session_expiration(self):
        """Verifica expiración de sesión"""
        session = Session(session_id="test-123")
        
        # No expirada
        assert not session.is_expired(timeout=3600)
        
        # Simular expiración
        session.last_activity = datetime.now() - timedelta(seconds=3601)
        assert session.is_expired(timeout=3600)
    
    def test_needs_summary(self):
        """Verifica si necesita resumen"""
        session = Session(session_id="test-123")
        
        # Añadir 5 mensajes
        for i in range(5):
            session.add_message("user", f"Mensaje {i}")
        
        assert not session.needs_summary(trigger=10)
        
        # Añadir 10 más
        for i in range(10):
            session.add_message("user", f"Mensaje {i}")
        
        assert session.needs_summary(trigger=10)


class TestSessionManager:
    """Tests para SessionManager"""
    
    def test_create_session(self, session_manager):
        """Crea nueva sesión"""
        session_id = session_manager.create_session()
        
        assert session_id is not None
        assert session_manager.get_session(session_id) is not None
    
    def test_get_nonexistent_session(self, session_manager):
        """Obtener sesión inexistente retorna None"""
        session = session_manager.get_session("nonexistent-id")
        
        assert session is None
    
    def test_add_message_to_session(self, session_manager):
        """Añade mensaje a sesión"""
        session_id = session_manager.create_session()
        session_manager.add_message(session_id, "user", "Hola")
        
        session = session_manager.get_session(session_id)
        
        # El sistema añade un mensaje de sistema al crear la sesión
        assert len(session.messages) >= 2
    
    def test_conversation_history(self, session_manager):
        """Obtiene historial de conversación"""
        session_id = session_manager.create_session()
        session_manager.add_message(session_id, "user", "Hola")
        session_manager.add_message(session_id, "assistant", "¡Hola! ¿Cómo estás?")
        
        history = session_manager.get_conversation_history(session_id)
        
        assert len(history) >= 3  # system + user + assistant
        assert isinstance(history, list)
        assert all("role" in msg and "content" in msg for msg in history)
    
    def test_format_for_model(self, session_manager):
        """Formatea conversación para el modelo"""
        session_id = session_manager.create_session()
        session_manager.add_message(session_id, "user", "Hola")
        
        formatted = session_manager.format_for_model(session_id)
        
        assert isinstance(formatted, str)
        assert "<|im_start|>" in formatted
        assert "<|im_end|>" in formatted
    
    def test_cleanup_expired_sessions(self, session_manager):
        """Limpia sesiones expiradas"""
        # Crear sesión
        session_id = session_manager.create_session()
        
        # Simular expiración
        session = session_manager.get_session(session_id)
        session.last_activity = datetime.now() - timedelta(seconds=3601)
        
        # Limpiar
        session_manager.cleanup_expired_sessions()
        
        # Verificar que fue eliminada
        assert session_manager.get_session(session_id) is None
    
    def test_system_prompt_included(self, session_manager):
        """Prompt de sistema se incluye al crear sesión"""
        session_id = session_manager.create_session()
        session = session_manager.get_session(session_id)
        
        assert len(session.messages) > 0
        assert session.messages[0].role == "system"
        assert "psicoeducación" in session.messages[0].content.lower()
