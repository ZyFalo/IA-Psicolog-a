"""
Configuración de la aplicación
"""

from pydantic_settings import BaseSettings
from pydantic import Field
from typing import List
import os


class Settings(BaseSettings):
    """Configuración global de la aplicación"""
    
    # API
    API_VERSION: str = "v1"
    DEBUG: bool = False
    CORS_ORIGINS: List[str] = ["http://localhost:3000", "http://localhost:5173"]
    
    # Modelo
    MODEL_NAME: str = "Qwen/Qwen2.5-7B-Instruct"
    MODEL_PATH: str = "./models/qwen2.5-7b"
    LORA_PATH: str = "./models/lora_adapters"
    QUANTIZATION: str = "4bit"  # 4bit, 8bit, none
    MAX_TOKENS: int = 256
    TEMPERATURE: float = 0.7
    TOP_P: float = 0.9
    USE_MLX: bool = True  # Usar MLX en Apple Silicon
    
    # Sesión
    MAX_CONTEXT_LENGTH: int = 4096
    SUMMARY_TRIGGER: int = 10  # Mensajes antes de resumir
    SESSION_TIMEOUT: int = 3600  # Segundos
    
    # Guardrails
    ENABLE_CRISIS_DETECTION: bool = True
    RISK_THRESHOLD: float = 0.75
    CRISIS_KEYWORDS: List[str] = [
        "suicidio", "suicidar", "matarme", "matar me",
        "acabar con mi vida", "no quiero vivir",
        "autolesión", "cortarme", "hacerme daño",
        "morir", "muerte", "desaparecer"
    ]
    
    # Voz
    ASR_MODEL: str = "medium"  # tiny, base, small, medium
    TTS_MODEL: str = "es_ES-medium"
    ENABLE_EMOTION_DETECTION: bool = True
    
    # Recursos de Crisis
    SUICIDE_HOTLINE: str = "988"
    CRISIS_TEXT: str = "741741"
    EMERGENCY: str = "911"
    
    # Logs y Métricas (sin PII)
    LOG_LEVEL: str = "INFO"
    ENABLE_METRICS: bool = True
    METRICS_PORT: int = 9090
    
    class Config:
        env_file = ".env"
        case_sensitive = True


settings = Settings()
