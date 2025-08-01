"""
API Server: Backend FastAPI para gestión de dispositivos Edge y comunicación
Sistema de comunicación entre dispositivos Edge y la plataforma en la nube

Funcionalidades:
- API REST para gestión de sensores y actuadores
- WebSocket para datos en tiempo real
- Integración MQTT para comunicación IoT
- Autenticación JWT y encriptación AES-256
"""

import asyncio
import logging
from datetime import datetime, timedelta
from typing import Dict, List, Optional
from fastapi import FastAPI, HTTPException, Depends, WebSocket, status
from fastapi.security import HTTPBearer, HTTPAuthorizationCredentials
from fastapi.middleware.cors import CORSMiddleware
import jwt
from pydantic import BaseModel
import json

from ..core.config import settings
from ..nexusoptim-core import EdgeAICore
from ..data-pipeline import DataPipeline

logger = logging.getLogger(__name__)

# Modelos Pydantic para API
class SensorReading(BaseModel):
    sensor_id: str
    voltage: float
    current: float
    temperature: Optional[float] = None
    humidity: Optional[float] = None
    timestamp: Optional[str] = None

class SensorRegistration(BaseModel):
    sensor_id: str
    sensor_type: str
    location: str
    coordinates: Optional[Dict[str, float]] = None
    calibration_params: Optional[Dict] = None

class OptimizationCommand(BaseModel):
    target_sensor: str
    command_type: str  # "adjust_voltage", "reduce_load", etc.
    parameters: Dict
    priority: int = 1

class PredictionRequest(BaseModel):
    sensor_ids: List[str]
    horizon_hours: int = 6
    include_confidence: bool = True

# Seguridad JWT
security = HTTPBearer()

class APIServer:
    """
    Servidor API principal para NexusOptim IA
    """
    
    def __init__(self):
        self.app = FastAPI(
            title="NexusOptim IA API",  
            description="Edge AI para Optimización Energética",
            version="1.0.0"
        )
        
        # Servicios
        self.edge_ai_core = EdgeAICore()
        self.data_pipeline = DataPipeline()
        
        # Estado del sistema
        self.registered_sensors = {}
        self.active_websockets = []
        self.system_status = "initializing"
        
        # Configurar CORS
        self.app.add_middleware(
            CORSMiddleware,
            allow_origins=["*"],  # En producción usar dominios específicos
            allow_credentials=True,
            allow_methods=["*"],
            allow_headers=["*"],
        )
        
        # Configurar rutas
        self._setup_routes()
    
    def _setup_routes(self):
        """Configurar todas las rutas de la API"""
        
        # ============ RUTAS DE SISTEMA ============
        @self.app.get("/")
        async def root():
            return {
                "service": "NexusOptim IA API",
                "version": "1.0.0",
                "status": self.system_status,
                "timestamp": datetime.now().isoformat()
            }
        
        @self.app.get("/health")
        async def health_check():
            health_status = {
                "status": "healthy",
                "services": {
                    "edge_ai": self.edge_ai_core.is_initialized,
                    "data_pipeline": self.data_pipeline.is_running,
                    "registered_sensors": len(self.registered_sensors),
                    "active_websockets": len(self.active_websockets)
                },
                "timestamp": datetime.now().isoformat()
            }
            
            if not all(health_status["services"].values()):
                health_status["status"] = "degraded"
                raise HTTPException(status_code=503, detail=health_status)
            
            return health_status
        
        # ============ GESTIÓN DE SENSORES ============
        @self.app.post("/api/v1/sensors/register")
        async def register_sensor(
            sensor: SensorRegistration,
            credentials: HTTPAuthorizationCredentials = Depends(security)
        ):
            """Registrar nuevo sensor en el sistema"""
            try:
                # Validar token JWT
                await self._validate_jwt_token(credentials.credentials)
                
                # Registrar sensor
                self.registered_sensors[sensor.sensor_id] = {
                    "sensor_type": sensor.sensor_type,
                    "location": sensor.location,
                    "coordinates": sensor.coordinates,
                    "calibration_params": sensor.calibration_params,
                    "registered_at": datetime.now().isoformat(),
                    "last_seen": None,
                    "status": "registered"
                }
                
                logger.info(f"📡 Sensor registrado: {sensor.sensor_id}")
                
                return {
                    "message": "Sensor registrado exitosamente",
                    "sensor_id": sensor.sensor_id,
                    "status": "active"
                }
                
            except Exception as e:
                logger.error(f"❌ Error registrando sensor: {e}")
                raise HTTPException(status_code=400, detail=str(e))
        
        @self.app.get("/api/v1/sensors")
        async def list_sensors(
            credentials: HTTPAuthorizationCredentials = Depends(security)
        ):
            """Listar todos los sensores registrados"""
            await self._validate_jwt_token(credentials.credentials)
            return {
                "sensors": self.registered_sensors,
                "count": len(self.registered_sensors)
            }
        
        @self.app.get("/api/v1/sensors/{sensor_id}/status")
        async def get_sensor_status(
            sensor_id: str,
            credentials: HTTPAuthorizationCredentials = Depends(security)
        ):
            """Obtener estado de un sensor específico"""
            await self._validate_jwt_token(credentials.credentials)
            
            if sensor_id not in self.registered_sensors:
                raise HTTPException(status_code=404, detail="Sensor no encontrado")
            
            # Obtener datos recientes del sensor
            recent_data = self.data_pipeline.lora_ingestion.get_recent_data(
                sensor_id=sensor_id, minutes=10
            )
            
            sensor_info = self.registered_sensors[sensor_id].copy()
            sensor_info["recent_readings"] = len(recent_data)
            sensor_info["last_reading"] = recent_data[-1] if recent_data else None
            
            return sensor_info
        
        # ============ DATOS Y PREDICCIONES ============
        @self.app.post("/api/v1/sensors/data")
        async def submit_sensor_data(
            reading: SensorReading,
            credentials: HTTPAuthorizationCredentials = Depends(security)
        ):
            """Recibir datos de sensores"""
            try:
                await self._validate_jwt_token(credentials.credentials)
                
                # Validar sensor registrado
                if reading.sensor_id not in self.registered_sensors:
                    raise HTTPException(status_code=404, detail="Sensor no registrado")
                
                # Procesar datos
                sensor_data = reading.dict()
                if not sensor_data.get("timestamp"):
                    sensor_data["timestamp"] = datetime.now().isoformat()
                
                # Procesar con Edge AI
                ai_result = await self.edge_ai_core.process_sensor_data(sensor_data)
                
                # Actualizar estado del sensor
                self.registered_sensors[reading.sensor_id]["last_seen"] = sensor_data["timestamp"]
                self.registered_sensors[reading.sensor_id]["status"] = "active"
                
                # Enviar a WebSocket clients
                await self._broadcast_to_websockets({
                    "type": "sensor_data",
                    "data": ai_result
                })
                
                logger.debug(f"📊 Datos procesados para {reading.sensor_id}")
                
                return {
                    "message": "Datos procesados exitosamente",
                    "ai_analysis": ai_result,
                    "timestamp": sensor_data["timestamp"]
                }
                
            except Exception as e:
                logger.error(f"❌ Error procesando datos: {e}")
                raise HTTPException(status_code=400, detail=str(e))
        
        @self.app.post("/api/v1/predictions")
        async def get_predictions(
            request: PredictionRequest,
            credentials: HTTPAuthorizationCredentials = Depends(security)
        ):
            """Obtener predicciones de demanda energética"""
            try:
                await self._validate_jwt_token(credentials.credentials)
                
                predictions = {}
                
                for sensor_id in request.sensor_ids:
                    if sensor_id not in self.registered_sensors:
                        continue
                    
                    # Obtener datos recientes
                    recent_data = self.data_pipeline.lora_ingestion.get_recent_data(
                        sensor_id=sensor_id, minutes=60
                    )
                    
                    if recent_data:
                        # Generar predicción
                        latest_data = recent_data[-1]
                        prediction = self.edge_ai_core.predictor.predict_demand(latest_data)
                        predictions[sensor_id] = prediction
                
                return {
                    "predictions": predictions,
                    "horizon_hours": request.horizon_hours,
                    "generated_at": datetime.now().isoformat()
                }
                
            except Exception as e:
                logger.error(f"❌ Error generando predicciones: {e}")
                raise HTTPException(status_code=400, detail=str(e))
        
        # ============ OPTIMIZACIÓN ============
        @self.app.post("/api/v1/optimization/command")
        async def send_optimization_command(
            command: OptimizationCommand,
            credentials: HTTPAuthorizationCredentials = Depends(security)
        ):
            """Enviar comando de optimización a actuadores"""
            try:
                await self._validate_jwt_token(credentials.credentials)
                
                # Validar sensor objetivo
                if command.target_sensor not in self.registered_sensors:
                    raise HTTPException(status_code=404, detail="Sensor objetivo no encontrado")
                
                # TODO: Implementar envío real de comandos via MQTT/LoRa
                logger.info(f"🎯 Comando de optimización: {command.command_type} -> {command.target_sensor}")
                
                # Simular respuesta
                return {
                    "message": "Comando enviado exitosamente",
                    "command_id": f"cmd_{datetime.now().timestamp()}",
                    "target": command.target_sensor,
                    "status": "sent"
                }
                
            except Exception as e:
                logger.error(f"❌ Error enviando comando: {e}")
                raise HTTPException(status_code=400, detail=str(e))
        
        # ============ WEBSOCKET PARA TIEMPO REAL ============
        @self.app.websocket("/ws")
        async def websocket_endpoint(websocket: WebSocket):
            """WebSocket para datos en tiempo real"""
            await websocket.accept()
            self.active_websockets.append(websocket)
            
            try:
                logger.info(f"🔌 WebSocket conectado. Total: {len(self.active_websockets)}")
                
                # Enviar estado inicial
                await websocket.send_json({
                    "type": "connection_established",
                    "registered_sensors": len(self.registered_sensors),
                    "system_status": self.system_status
                })
                
                # Mantener conexión activa
                while True:
                    # Ping para mantener conexión
                    await websocket.send_json({
                        "type": "ping",
                        "timestamp": datetime.now().isoformat()
                    })
                    await asyncio.sleep(30)
                    
            except Exception as e:
                logger.info(f"🔌 WebSocket desconectado: {e}")
            finally:
                if websocket in self.active_websockets:
                    self.active_websockets.remove(websocket)
    
    async def _validate_jwt_token(self, token: str) -> Dict:
        """Validar token JWT"""
        try:
            payload = jwt.decode(
                token, 
                settings.JWT_SECRET_KEY, 
                algorithms=["HS256"]
            )
            return payload
        except jwt.ExpiredSignatureError:
            raise HTTPException(status_code=401, detail="Token expirado")
        except jwt.InvalidTokenError:
            raise HTTPException(status_code=401, detail="Token inválido")
    
    async def _broadcast_to_websockets(self, message: Dict):
        """Enviar mensaje a todos los WebSockets conectados"""
        if not self.active_websockets:
            return
        
        disconnected = []
        for websocket in self.active_websockets:
            try:
                await websocket.send_json(message)
            except:
                disconnected.append(websocket)
        
        # Remover WebSockets desconectados
        for ws in disconnected:
            self.active_websockets.remove(ws)
    
    async def initialize(self):
        """Inicializar servidor API"""
        try:
            logger.info("🌐 Inicializando API Server...")
            
            # Inicializar Edge AI Core
            await self.edge_ai_core.initialize()
            
            # Inicializar Data Pipeline
            asyncio.create_task(self.data_pipeline.start_pipeline())
            
            self.system_status = "running"
            logger.info("✅ API Server inicializado correctamente")
            
        except Exception as e:
            self.system_status = "error"
            logger.error(f"❌ Error inicializando API Server: {e}")
            raise

# Función para crear aplicación
def create_app() -> FastAPI:
    """Crear y configurar aplicación FastAPI"""
    api_server = APIServer()
    return api_server.app
