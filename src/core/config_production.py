"""
Configuración de producción para countercorehazardav.com
NexusOptim IA - Optimizada para hosting web
"""
import os
from pydantic_settings import BaseSettings

class ProductionSettings(BaseSettings):
    """Configuración optimizada para producción web"""
    
    # App básica
    APP_NAME: str = "NexusOptim IA"
    VERSION: str = "1.0.0-MVP"
    DEBUG: bool = False  # IMPORTANTE: False en producción
    
    # Servidor (ajustar según hosting)
    HOST: str = "0.0.0.0"
    PORT: int = int(os.getenv("PORT", "8000"))  # Heroku/Railway compatible
    
    # URLs públicas
    PUBLIC_URL: str = "https://countercorehazardav.com"
    
    # Seguridad mejorada
    SECRET_KEY: str = os.getenv("SECRET_KEY", "nexusoptim_production_secure_2025")
    
    # LoRa Costa Rica
    LORA_FREQUENCY: float = 915.0  # MHz SUTEL
    
    # Base datos (SQLite simple, cambiar a PostgreSQL si necesario)
    DATABASE_URL: str = os.getenv("DATABASE_URL", "sqlite:///nexusoptim_prod.db")
    
    # Costa Rica específico
    COSTA_RICA_TIMEZONE: str = "America/Costa_Rica"
    ICE_INTEGRATION: bool = True
    AYA_INTEGRATION: bool = True
    SUTEL_COMPLIANCE: bool = True
    
    # Contacto
    CONTACT_EMAIL: str = "jorge@nexusoptim.ai"
    CONTACT_PHONE: str = "+506-xxxx-xxxx"
    
    # Logging
    LOG_LEVEL: str = "INFO"
    
    class Config:
        env_file = ".env"
        extra = "ignore"

# Instancia para producción
settings = ProductionSettings()
