"""
Configuración simplificada para NexusOptim IA
"""
import os
from typing import Optional
from pydantic_settings import BaseSettings

class Settings(BaseSettings):
    """Configuración básica de NexusOptim IA"""
    
    # App básica
    APP_NAME: str = "NexusOptim IA"
    VERSION: str = "1.0.0-MVP"
    DEBUG: bool = True
    
    # Servidor
    HOST: str = "0.0.0.0"
    PORT: int = 8000
    
    # Seguridad básica
    SECRET_KEY: str = "nexusoptim_2025_costa_rica"
    
    # LoRa Costa Rica
    LORA_FREQUENCY: float = 915.0  # MHz SUTEL
    
    # Base datos simple
    DATABASE_URL: str = "sqlite:///nexusoptim.db"
    
    class Config:
        env_file = ".env"
        extra = "ignore"  # Ignorar campos extra

# Instancia global
settings = Settings()
