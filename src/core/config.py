"""
NexusOptim IA - Configuration Settings
Configuración centralizada para toda la aplicación
"""

import os
from typing import List, Optional
from pydantic_settings import BaseSettings
from pydantic import validator

class Settings(BaseSettings):
    """Configuración de la aplicación usando Pydantic"""
    
    # ============ APPLICATION ============
    ENVIRONMENT: str = "development"
    DEBUG: bool = True
    LOG_LEVEL: str = "DEBUG"
    SECRET_KEY: str = "nexusoptim_change_me"
    
    # ============ DATABASE ============
    DATABASE_URL: str = "postgresql://nexusoptim:password@localhost:5432/nexusoptim"
    REDIS_URL: str = "redis://localhost:6379/0"
    
    # ============ MQTT ============
    MQTT_BROKER_HOST: str = "localhost"
    MQTT_BROKER_PORT: int = 1883
    MQTT_USERNAME: Optional[str] = None
    MQTT_PASSWORD: Optional[str] = None
    
    # ============ LORA ============
    LORA_FREQUENCY: int = 915000000  # 915 MHz para Costa Rica
    LORA_TX_POWER: int = 14          # 14dBm máximo
    LORA_SPREADING_FACTOR: int = 9
    LORA_BANDWIDTH: int = 125000
    LORA_CODING_RATE: int = 5
    
    # ============ AI MODELS ============
    MODEL_PATH: str = "./models"
    TENSORFLOW_MODEL_PATH: str = "./models/nexusoptim_v1.tflite"
    SCALER_PATH: str = "./models/scaler.pkl"
    FEATURE_COLUMNS: str = "voltage,current,temperature,humidity,power_factor"
    
    # ============ SENSORS ============
    ADS1115_I2C_ADDRESS: str = "0x48"
    SCT013_CALIBRATION_FACTOR: float = 0.066
    VOLTAGE_DIVIDER_RATIO: int = 30
    
    # ============ OPTIMIZATION ============
    PREDICTION_HORIZON: int = 6
    OPTIMIZATION_INTERVAL: int = 300
    LOSS_THRESHOLD: float = 0.05
    
    # ============ SECURITY ============
    AES_ENCRYPTION_KEY: str = "change_this_encryption_key_32_chars"
    JWT_SECRET_KEY: str = "change_this_jwt_secret"
    JWT_EXPIRATION_HOURS: int = 24
    
    # ============ COSTA RICA ============
    TIMEZONE: str = "America/Costa_Rica"
    SUTEL_CERTIFICATION_ID: str = "pending"
    ICE_API_ENDPOINT: str = "https://api.grupoice.com/v1"
    COOPESANTOS_ENDPOINT: str = "http://192.168.1.100:8080"
    
    # ============ MONITORING ============
    HEALTH_CHECK_INTERVAL: int = 30
    ALERT_EMAIL: str = "alerts@opennexus.cr"
    
    @validator("FEATURE_COLUMNS")
    def parse_feature_columns(cls, v):
        """Convertir string de columnas a lista"""
        if isinstance(v, str):
            return [col.strip() for col in v.split(",")]
        return v
    
    @validator("ADS1115_I2C_ADDRESS")
    def parse_i2c_address(cls, v):
        """Convertir dirección I2C string a int"""
        if isinstance(v, str):
            return int(v, 16)  # Convertir hex string a int
        return v
    
    @validator("LORA_FREQUENCY")
    def validate_lora_frequency(cls, v):
        """Validar que la frecuencia esté en la banda ISM de Costa Rica"""
        if not (902000000 <= v <= 928000000):
            raise ValueError("Frecuencia LoRa debe estar entre 902-928 MHz (banda ISM CR)")
        return v
    
    @validator("ENVIRONMENT")
    def validate_environment(cls, v):
        """Validar entorno"""
        if v not in ["development", "testing", "production"]:
            raise ValueError("Environment debe ser: development, testing, o production")
        return v
    
    class Config:
        env_file = ".env"
        case_sensitive = True

# Instancia global de configuración
settings = Settings()
