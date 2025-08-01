"""
NexusOptim IA - Logging Configuration
Sistema de logging centralizado con rotación y formateo
"""

import logging
import logging.handlers
import os
import sys
from datetime import datetime
from pathlib import Path

from core.config_simple import settings

def setup_logging():
    """Configurar sistema de logging para NexusOptim IA"""
    
    # Crear directorio de logs si no existe
    log_dir = Path("logs")
    log_dir.mkdir(exist_ok=True)
    
    # Configurar formato
    log_format = (
        "%(asctime)s | %(levelname)8s | %(name)20s | "
        "%(funcName)15s:%(lineno)3d | %(message)s"
    )
    
    date_format = "%Y-%m-%d %H:%M:%S"
    
    # Configurar nivel de logging
    log_level = getattr(logging, settings.LOG_LEVEL.upper(), logging.INFO)
    
    # Configurar root logger
    root_logger = logging.getLogger()
    root_logger.setLevel(log_level)
    
    # Limpiar handlers existentes
    root_logger.handlers.clear()
    
    # ============ CONSOLE HANDLER ============
    console_handler = logging.StreamHandler(sys.stdout)
    console_handler.setLevel(log_level)
    
    # Formato con colores para desarrollo
    if settings.ENVIRONMENT == "development":
        console_format = (
            "\033[36m%(asctime)s\033[0m | "
            "\033[%(levelcolor)sm%(levelname)8s\033[0m | "
            "\033[35m%(name)20s\033[0m | "
            "\033[33m%(funcName)15s:%(lineno)3d\033[0m | "
            "%(message)s"
        )
        
        class ColoredFormatter(logging.Formatter):
            """Formatter con colores para consola"""
            
            COLORS = {
                'DEBUG': '37',    # Blanco
                'INFO': '32',     # Verde
                'WARNING': '33',  # Amarillo
                'ERROR': '31',    # Rojo
                'CRITICAL': '41', # Rojo con fondo
            }
            
            def format(self, record):
                record.levelcolor = self.COLORS.get(record.levelname, '37')
                return super().format(record)
        
        console_formatter = ColoredFormatter(console_format, date_format)
    else:
        console_formatter = logging.Formatter(log_format, date_format)
    
    console_handler.setFormatter(console_formatter)
    root_logger.addHandler(console_handler)
    
    # ============ FILE HANDLER (ROTATING) ============
    file_handler = logging.handlers.RotatingFileHandler(
        filename=log_dir / "nexusoptim.log",
        maxBytes=10 * 1024 * 1024,  # 10 MB
        backupCount=5,
        encoding='utf-8'
    )
    file_handler.setLevel(logging.INFO)
    file_formatter = logging.Formatter(log_format, date_format)
    file_handler.setFormatter(file_formatter)
    root_logger.addHandler(file_handler)
    
    # ============ ERROR FILE HANDLER ============
    error_handler = logging.handlers.RotatingFileHandler(
        filename=log_dir / "nexusoptim_errors.log",
        maxBytes=5 * 1024 * 1024,  # 5 MB
        backupCount=3,
        encoding='utf-8'
    )
    error_handler.setLevel(logging.ERROR)
    error_formatter = logging.Formatter(
        "%(asctime)s | %(levelname)s | %(name)s | %(funcName)s:%(lineno)d | "
        "%(message)s | %(pathname)s", 
        date_format
    )
    error_handler.setFormatter(error_formatter)
    root_logger.addHandler(error_handler)
    
    # ============ JSON HANDLER (PRODUCCIÓN) ============
    if settings.ENVIRONMENT == "production":
        import json
        
        class JSONFormatter(logging.Formatter):
            """Formatter JSON para producción"""
            
            def format(self, record):
                log_entry = {
                    "timestamp": datetime.fromtimestamp(record.created).isoformat(),
                    "level": record.levelname,
                    "logger": record.name,
                    "function": record.funcName,
                    "line": record.lineno,
                    "message": record.getMessage(),
                    "module": record.module,
                }
                
                # Agregar información de excepción si existe
                if record.exc_info:
                    log_entry["exception"] = self.formatException(record.exc_info)
                
                return json.dumps(log_entry, ensure_ascii=False)
        
        json_handler = logging.handlers.RotatingFileHandler(
            filename=log_dir / "nexusoptim.json",
            maxBytes=20 * 1024 * 1024,  # 20 MB
            backupCount=10,
            encoding='utf-8'
        )
        json_handler.setLevel(logging.INFO)
        json_handler.setFormatter(JSONFormatter())
        root_logger.addHandler(json_handler)
    
    # ============ CONFIGURAR LOGGERS ESPECÍFICOS ============
    
    # Reducir verbosidad de librerías externas
    logging.getLogger("urllib3").setLevel(logging.WARNING)
    logging.getLogger("requests").setLevel(logging.WARNING)
    logging.getLogger("asyncio").setLevel(logging.WARNING)
    logging.getLogger("paho.mqtt").setLevel(logging.INFO)
    
    # Logger específico para sensores
    sensor_logger = logging.getLogger("sensors")
    sensor_logger.setLevel(logging.DEBUG if settings.DEBUG else logging.INFO)
    
    # Logger específico para IA
    ai_logger = logging.getLogger("ai")
    ai_logger.setLevel(logging.DEBUG if settings.DEBUG else logging.INFO)
    
    # Logger específico para LoRa
    lora_logger = logging.getLogger("lora")
    lora_logger.setLevel(logging.DEBUG if settings.DEBUG else logging.INFO)
    
    # Log inicial
    logger = logging.getLogger(__name__)
    logger.info("=" * 60)
    logger.info("🚀 NexusOptim IA - Sistema de Logging Inicializado")
    logger.info(f"📊 Nivel de logging: {settings.LOG_LEVEL}")
    logger.info(f"🌍 Entorno: {settings.ENVIRONMENT}")
    logger.info(f"📁 Directorio de logs: {log_dir.absolute()}")
    logger.info("=" * 60)

def get_logger(name: str) -> logging.Logger:
    """Obtener logger con nombre específico"""
    return logging.getLogger(name)
