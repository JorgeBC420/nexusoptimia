"""
NexusOptim IA - Main Application Entry Point
Edge AI para Optimización de Redes Eléctricas - Costa Rica

Desarrollado por: OpenNexus
Fecha: Agosto 2025
"""

import asyncio
import logging
import os
from datetime import datetime
from pathlib import Path

import uvicorn
from fastapi import FastAPI, HTTPException
from fastapi.middleware.cors import CORSMiddleware
from dotenv import load_dotenv

from core.config import settings
from core.logging_config import setup_logging
from api.routes import router as api_router
from services.sensor_service import SensorService
from services.ai_service import AIService
from services.optimization_service import OptimizationService
from services.mqtt_service import MQTTService

# Cargar variables de entorno
load_dotenv()

# Configurar logging
setup_logging()
logger = logging.getLogger(__name__)

# Crear aplicación FastAPI
app = FastAPI(
    title="NexusOptim IA",
    description="Edge AI para Optimización de Redes Eléctricas",
    version="1.0.0",
    docs_url="/docs",
    redoc_url="/redoc"
)

# Configurar CORS
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],  # En producción, especificar dominios exactos
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Servicios globales
sensor_service = None
ai_service = None
optimization_service = None
mqtt_service = None

@app.on_event("startup")
async def startup_event():
    """Inicializar servicios al arrancar la aplicación"""
    global sensor_service, ai_service, optimization_service, mqtt_service
    
    logger.info("🚀 Iniciando NexusOptim IA...")
    logger.info(f"⚙️ Entorno: {settings.ENVIRONMENT}")
    logger.info(f"🌍 Zona horaria: {settings.TIMEZONE}")
    logger.info(f"📡 Frecuencia LoRa: {settings.LORA_FREQUENCY} Hz")
    
    try:
        # Inicializar servicios
        sensor_service = SensorService()
        ai_service = AIService()
        optimization_service = OptimizationService()
        mqtt_service = MQTTService()
        
        # Cargar modelos AI
        await ai_service.load_models()
        logger.info("🧠 Modelos AI cargados correctamente")
        
        # Conectar MQTT
        await mqtt_service.connect()
        logger.info("📡 Conectado a broker MQTT")
        
        # Inicializar sensores
        await sensor_service.initialize()
        logger.info("🔌 Sensores inicializados")
        
        logger.info("✅ NexusOptim IA iniciado correctamente")
        
    except Exception as e:
        logger.error(f"❌ Error durante el startup: {e}")
        raise

@app.on_event("shutdown")
async def shutdown_event():
    """Limpiar recursos al cerrar la aplicación"""
    logger.info("🛑 Cerrando NexusOptim IA...")
    
    try:
        if mqtt_service:
            await mqtt_service.disconnect()
        if sensor_service:
            await sensor_service.cleanup()
        logger.info("✅ Recursos liberados correctamente")
    except Exception as e:
        logger.error(f"❌ Error durante el shutdown: {e}")

# Incluir rutas de la API
app.include_router(api_router, prefix="/api/v1")

@app.get("/")
async def root():
    """Endpoint raíz con información del sistema"""
    return {
        "message": "NexusOptim IA - Edge AI para Optimización Eléctrica",
        "version": "1.0.0",
        "status": "running",
        "timestamp": datetime.now().isoformat(),
        "environment": settings.ENVIRONMENT,
        "lora_frequency": f"{settings.LORA_FREQUENCY} Hz",
        "timezone": settings.TIMEZONE
    }

@app.get("/health")
async def health_check():
    """Health check para Docker y monitoring"""
    try:
        # Verificar servicios críticos
        services_status = {
            "sensor_service": sensor_service.is_healthy() if sensor_service else False,
            "ai_service": ai_service.is_healthy() if ai_service else False,
            "mqtt_service": mqtt_service.is_connected() if mqtt_service else False,
        }
        
        all_healthy = all(services_status.values())
        
        return {
            "status": "healthy" if all_healthy else "degraded",
            "timestamp": datetime.now().isoformat(),
            "services": services_status,
            "uptime": f"{(datetime.now() - startup_time).total_seconds():.1f}s"
        }
    except Exception as e:
        logger.error(f"Health check failed: {e}")
        raise HTTPException(status_code=503, detail="Service unhealthy")

# Variable global para tracking de uptime
startup_time = datetime.now()

async def main():
    """Función principal para ejecutar la aplicación"""
    logger.info("🌟 Iniciando NexusOptim IA Edge Computing Platform")
    
    # Configuración del servidor
    config = uvicorn.Config(
        app,
        host="0.0.0.0",
        port=int(os.getenv("PORT", 8000)),
        log_level=settings.LOG_LEVEL.lower(),
        reload=settings.DEBUG,
        workers=1 if settings.DEBUG else 2
    )
    
    server = uvicorn.Server(config)
    await server.serve()

if __name__ == "__main__":
    asyncio.run(main())
