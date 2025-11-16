"""
Health check endpoints
"""

from fastapi import APIRouter
from pydantic import BaseModel
from datetime import datetime
import logging

logger = logging.getLogger(__name__)

router = APIRouter()


class HealthResponse(BaseModel):
    """Response de health check"""
    status: str
    timestamp: str
    model_loaded: bool
    version: str


@router.get("/health", response_model=HealthResponse)
async def health_check():
    """Health check endpoint"""
    from app.main import model_manager
    
    return HealthResponse(
        status="healthy",
        timestamp=datetime.now().isoformat(),
        model_loaded=model_manager.model is not None if model_manager else False,
        version="0.1.0"
    )


@router.get("/metrics")
async def metrics():
    """Métricas básicas (sin PII)"""
    from app.main import session_manager
    
    if not session_manager:
        return {"error": "Session manager no inicializado"}
    
    return {
        "active_sessions": len(session_manager.sessions),
        "timestamp": datetime.now().isoformat()
    }
