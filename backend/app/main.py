"""
FastAPI Application - Main Entry Point
"""

from fastapi import FastAPI, WebSocket, WebSocketDisconnect
from fastapi.middleware.cors import CORSMiddleware
from contextlib import asynccontextmanager
import logging

from app.config import settings
from app.api import chat, voice, health
from app.core.model_manager_mlx import ModelManagerMLX
from app.core.session_manager import SessionManager

# Configurar logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
)
logger = logging.getLogger(__name__)

# Instancias globales
model_manager = None
session_manager = None


@asynccontextmanager
async def lifespan(app: FastAPI):
    """Lifecycle manager para inicializar/limpiar recursos"""
    global model_manager, session_manager
    
    logger.info("🚀 Iniciando aplicación...")
    
    # Inicializar componentes
    model_manager = ModelManagerMLX()
    model_manager.load_model()  # MLX es síncrono
    
    session_manager = SessionManager(settings)
    
    logger.info("✅ Aplicación lista")
    
    yield
    
    # Cleanup
    logger.info("🛑 Cerrando aplicación...")
    model_manager.cleanup()  # MLX es síncrono
    await session_manager.cleanup()


# Crear aplicación
app = FastAPI(
    title="Asistente Psicoeducativo IA",
    description="API para asistente de psicoeducación con IA local",
    version="0.1.0",
    lifespan=lifespan
)

# CORS
app.add_middleware(
    CORSMiddleware,
    allow_origins=settings.CORS_ORIGINS,
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Incluir routers
app.include_router(health.router, prefix="/api", tags=["health"])
app.include_router(chat.router, prefix="/api/chat", tags=["chat"])
app.include_router(voice.router, prefix="/api/voice", tags=["voice"])


@app.get("/")
async def root():
    """Endpoint raíz"""
    return {
        "name": "Asistente Psicoeducativo IA",
        "version": "0.1.0",
        "status": "running"
    }


if __name__ == "__main__":
    import uvicorn
    uvicorn.run(
        "app.main:app",
        host="0.0.0.0",
        port=8000,
        reload=True
    )
