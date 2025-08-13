"""
NexusOptim-Core: Edge AI Algorithms for Energy Optimization
Algoritmos de Inteligencia Artificial optimizados para hardware de bajo consumo

Este módulo contiene los algoritmos centrales de NexusOptim IA:
- Modelos LSTM para predicción de demanda energética
- Isolation Forest para detección de anomalías  
- Algoritmos de optimización con PuLP y SciPy
- Cuantización de modelos para Edge Computing
"""

import logging
import numpy as np
import tensorflow as tf
from sklearn.ensemble import IsolationForest
from typing import Dict, Tuple, Optional
import joblib
from pathlib import Path

from ..core.config import settings

logger = logging.getLogger(__name__)

class EdgeAIPredictor:
    """
    Predictor de demanda energética optimizado para Edge Computing
    Utiliza modelos LSTM cuantizados para predicción en tiempo real
    """
    
    def __init__(self, model_path: Optional[str] = None):
        self.model_path = model_path or settings.TENSORFLOW_MODEL_PATH
        self.interpreter = None
        self.scaler = None
        self.is_loaded = False
        
    async def load_model(self) -> bool:
        """Cargar modelo TensorFlow Lite optimizado"""
        try:
            logger.info(f"🧠 Cargando modelo Edge AI: {self.model_path}")
            
            # Cargar intérprete TensorFlow Lite
            self.interpreter = tf.lite.Interpreter(model_path=self.model_path)
            self.interpreter.allocate_tensors()
            
            # Cargar scaler para normalización
            scaler_path = Path(self.model_path).parent / "scaler.pkl"
            if scaler_path.exists():
                self.scaler = joblib.load(scaler_path)
                logger.info("📊 Scaler cargado correctamente")
            
            self.is_loaded = True
            logger.info("✅ Modelo Edge AI cargado exitosamente")
            return True
            
        except Exception as e:
            logger.error(f"❌ Error cargando modelo: {e}")
            return False
    
    def preprocess_data(self, sensor_data: Dict) -> np.ndarray:
        """Preprocesar datos de sensores para inferencia"""
        try:
            # Extraer features según configuración
            features = []
            for column in settings.FEATURE_COLUMNS:
                if column in sensor_data:
                    features.append(sensor_data[column])
                else:
                    logger.warning(f"⚠️ Feature faltante: {column}")
                    features.append(0.0)
            
            # Convertir a numpy array
            features_array = np.array([features], dtype=np.float32)
            
            # Normalizar si hay scaler disponible
            if self.scaler:
                features_array = self.scaler.transform(features_array)
            
            return features_array
            
        except Exception as e:
            logger.error(f"❌ Error en preprocesamiento: {e}")
            return np.array([[0.0] * len(settings.FEATURE_COLUMNS)], dtype=np.float32)
    
    def predict_demand(self, sensor_data: Dict) -> Dict:
        """Predecir demanda energética para las próximas horas"""
        if not self.is_loaded:
            logger.error("❌ Modelo no cargado")
            return {"error": "Modelo no inicializado"}
        
        try:
            # Preprocesar datos
            input_data = self.preprocess_data(sensor_data)
            
            # Obtener detalles de entrada y salida
            input_details = self.interpreter.get_input_details()
            output_details = self.interpreter.get_output_details()
            
            # Configurar tensor de entrada
            self.interpreter.set_tensor(input_details[0]['index'], input_data)
            
            # Ejecutar inferencia
            self.interpreter.invoke()
            
            # Obtener predicción
            prediction = self.interpreter.get_tensor(output_details[0]['index'])
            
            # Procesar resultado
            demand_forecast = prediction[0].tolist()
            
            logger.info(f"🔮 Predicción generada: {len(demand_forecast)} puntos")
            
            return {
                "demand_forecast": demand_forecast,
                "horizon_hours": settings.PREDICTION_HORIZON,
                "timestamp": sensor_data.get("timestamp"),
                "confidence": self._calculate_confidence(prediction)
            }
            
        except Exception as e:
            logger.error(f"❌ Error en predicción: {e}")
            return {"error": str(e)}
    
    def _calculate_confidence(self, prediction: np.ndarray) -> float:
        """Calcular confianza de la predicción"""
        # Implementar lógica de confianza basada en varianza
        variance = np.var(prediction)
        confidence = max(0.0, min(1.0, 1.0 - variance))
        return float(confidence)

class AnomalyDetector:
    """
    Detector de anomalías para identificar fallos en la red eléctrica
    Utiliza Isolation Forest optimizado para Edge Computing
    """
    
    def __init__(self):
        self.model = IsolationForest(
            contamination=0.1,  # 10% de datos anómalos esperados
            random_state=42,
            n_jobs=1  # Optimizado para Edge
        )
        self.is_trained = False
        
    def train(self, historical_data: np.ndarray) -> bool:
        """Entrenar detector con datos históricos"""
        try:
            logger.info(f"🔍 Entrenando detector de anomalías con {len(historical_data)} muestras")
            
            self.model.fit(historical_data)
            self.is_trained = True
            
            logger.info("✅ Detector de anomalías entrenado")
            return True
            
        except Exception as e:
            logger.error(f"❌ Error entrenando detector: {e}")
            return False
    
    def detect_anomaly(self, sensor_data: Dict) -> Dict:
        """Detectar anomalías en datos de sensores"""
        if not self.is_trained:
            logger.warning("⚠️ Detector no entrenado")
            return {"anomaly": False, "score": 0.0}
        
        try:
            # Preparar datos
            features = [sensor_data.get(col, 0.0) for col in settings.FEATURE_COLUMNS]
            data_point = np.array([features])
            
            # Detectar anomalía
            anomaly_label = self.model.predict(data_point)[0]
            anomaly_score = self.model.decision_function(data_point)[0]
            
            is_anomaly = anomaly_label == -1
            
            if is_anomaly:
                logger.warning(f"🚨 Anomalía detectada! Score: {anomaly_score:.3f}")
            
            return {
                "anomaly": is_anomaly,
                "score": float(anomaly_score),
                "severity": self._classify_severity(anomaly_score),
                "timestamp": sensor_data.get("timestamp")
            }
            
        except Exception as e:
            logger.error(f"❌ Error detectando anomalía: {e}")
            return {"anomaly": False, "score": 0.0, "error": str(e)}
    
    def _classify_severity(self, score: float) -> str:
        """Clasificar severidad de la anomalía"""
        if score < -0.5:
            return "CRITICAL"
        elif score < -0.3:
            return "HIGH"
        elif score < -0.1:
            return "MEDIUM"
        else:
            return "LOW"

class EdgeAICore:
    """
    Clase principal que integra todos los algoritmos Edge AI
    """
    
    def __init__(self):
        self.predictor = EdgeAIPredictor()
        self.anomaly_detector = AnomalyDetector()
        self.is_initialized = False
        
    async def initialize(self) -> bool:
        """Inicializar todos los componentes"""
        try:
            logger.info("🚀 Inicializando NexusOptim Core...")
            
            # Cargar predictor
            predictor_loaded = await self.predictor.load_model()
            
            # TODO: Cargar datos históricos para entrenar detector de anomalías
            # historical_data = load_historical_data()
            # anomaly_trained = self.anomaly_detector.train(historical_data)
            
            self.is_initialized = predictor_loaded
            
            if self.is_initialized:
                logger.info("✅ NexusOptim Core inicializado correctamente")
            else:
                logger.error("❌ Error inicializando NexusOptim Core")
            
            return self.is_initialized
            
        except Exception as e:
            logger.error(f"❌ Error fatal en inicialización: {e}")
            return False
    
    async def process_sensor_data(self, sensor_data: Dict) -> Dict:
        """Procesar datos de sensores con todos los algoritmos"""
        if not self.is_initialized:
            return {"error": "Core no inicializado"}
        
        try:
            # Generar predicciones
            prediction = self.predictor.predict_demand(sensor_data)
            
            # Detectar anomalías
            anomaly = self.anomaly_detector.detect_anomaly(sensor_data)
            
            # Combinar resultados
            result = {
                "sensor_id": sensor_data.get("sensor_id"),
                "timestamp": sensor_data.get("timestamp"),
                "prediction": prediction,
                "anomaly_detection": anomaly,
                "processing_time_ms": 0  # TODO: Implementar timing
            }
            
            return result
            
        except Exception as e:
            logger.error(f"❌ Error procesando datos: {e}")
            return {"error": str(e)}
