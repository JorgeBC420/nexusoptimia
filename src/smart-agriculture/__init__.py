"""
Módulo de Agricultura Inteligente - NexusOptim IA
Sistema de monitoreo y optimización agrícola con IoT y AI

Funcionalidades:
- Monitoreo de cultivos con sensores IoT (café, banano, piña, palmito)
- Optimización de riego inteligente
- Predicción de rendimiento de cosechas
- Detección temprana de plagas y enfermedades
- Gestión de recursos hídricos agrícolas
- Integración con datos meteorológicos SENASA/IMN
"""

import asyncio
import logging
import numpy as np
from datetime import datetime, timedelta
from typing import Dict, List, Tuple, Optional
from dataclasses import dataclass
import json
from geopy.distance import geodesic

from ..core.config import settings

logger = logging.getLogger(__name__)

@dataclass
class CropSensor:
    """Sensor agrícola IoT"""
    sensor_id: str
    location: Tuple[float, float]  # (lat, lon)
    farm_name: str
    crop_type: str  # "coffee", "banana", "pineapple", "palmito", "vegetables"
    sensor_types: List[str]  # ["soil_moisture", "temperature", "humidity", "ph", "nutrients", "light"]
    installation_date: str
    farm_size_hectares: float
    irrigation_system: str  # "drip", "sprinkler", "flood", "manual"
    owner_contact: str
    municipality: str
    elevation: float  # metros sobre nivel del mar

@dataclass
class CropReading:
    """Lectura de sensores agrícolas"""
    sensor_id: str
    timestamp: datetime
    soil_moisture: float  # % humedad del suelo
    soil_temperature: float  # °C
    air_temperature: float  # °C
    air_humidity: float  # %
    soil_ph: float  # pH del suelo
    nitrogen: float  # ppm N
    phosphorus: float  # ppm P
    potassium: float  # ppm K
    light_intensity: float  # lux
    leaf_wetness: float  # % humedad foliar
    battery_level: float  # % batería del sensor

@dataclass
class IrrigationEvent:
    """Evento de riego automático"""
    event_id: str
    sensor_id: str
    trigger_time: datetime
    duration_minutes: int
    water_volume_liters: float
    trigger_reason: str  # "scheduled", "moisture_low", "temperature_high", "forecast_dry"
    efficiency_score: float  # 0-1 score de eficiencia
    crop_stage: str  # "seedling", "vegetative", "flowering", "fruiting", "harvest"

@dataclass
class CropAlert:
    """Alerta agrícola"""
    alert_id: str
    sensor_id: str
    farm_name: str
    alert_type: str  # "moisture_low", "disease_risk", "pest_detected", "nutrient_deficiency"
    severity: str  # "low", "medium", "high", "critical"
    description: str
    recommendations: List[str]
    estimated_yield_impact: float  # % impacto en rendimiento
    detection_time: datetime

class CostaRicaCropDatabase:
    """
    Base de datos de cultivos principales de Costa Rica
    Parámetros optimizados por región y altitud
    """
    
    CROP_PARAMETERS = {
        "coffee": {
            "optimal_moisture": {"min": 60, "max": 80},  # % humedad suelo
            "optimal_temp": {"min": 18, "max": 24},      # °C temperatura
            "optimal_ph": {"min": 6.0, "max": 6.8},     # pH suelo
            "water_needs_mm_day": 4.5,                   # mm agua por día
            "harvest_months": [11, 12, 1, 2],           # Nov-Feb
            "altitude_range": {"min": 600, "max": 1800}, # metros
            "main_regions": ["Tarrazú", "Naranjo", "Dota", "Pérez Zeledón"]
        },
        "banana": {
            "optimal_moisture": {"min": 70, "max": 85},
            "optimal_temp": {"min": 26, "max": 30},
            "optimal_ph": {"min": 5.5, "max": 7.0},
            "water_needs_mm_day": 6.0,
            "harvest_months": list(range(1, 13)),  # Todo el año
            "altitude_range": {"min": 0, "max": 600},
            "main_regions": ["Limón", "Puntarenas", "San Carlos"]
        },
        "pineapple": {
            "optimal_moisture": {"min": 65, "max": 75},
            "optimal_temp": {"min": 24, "max": 32},
            "optimal_ph": {"min": 4.5, "max": 6.5},
            "water_needs_mm_day": 3.8,
            "harvest_months": [3, 4, 5, 9, 10, 11],
            "altitude_range": {"min": 0, "max": 400},
            "main_regions": ["San Carlos", "Buenos Aires", "Osa"]
        },
        "palmito": {
            "optimal_moisture": {"min": 75, "max": 90},
            "optimal_temp": {"min": 22, "max": 28},
            "optimal_ph": {"min": 5.0, "max": 6.5},
            "water_needs_mm_day": 5.2,
            "harvest_months": list(range(1, 13)),
            "altitude_range": {"min": 0, "max": 800},
            "main_regions": ["Pérez Zeledón", "Osa", "Coto Brus"]
        }
    }
    
    @classmethod
    def get_optimal_ranges(cls, crop_type: str, elevation: float) -> Dict:
        """Obtener rangos óptimos ajustados por altitud"""
        
        if crop_type not in cls.CROP_PARAMETERS:
            return cls.CROP_PARAMETERS["coffee"]  # Default
        
        params = cls.CROP_PARAMETERS[crop_type].copy()
        
        # Ajustar por altitud
        if elevation > 1000:  # Altitud alta - temperaturas más bajas
            params["optimal_temp"]["min"] -= 2
            params["optimal_temp"]["max"] -= 2
            params["water_needs_mm_day"] *= 0.9  # Menos evapotranspiración
        elif elevation < 200:  # Altitud baja - más calor
            params["optimal_temp"]["min"] += 1
            params["optimal_temp"]["max"] += 1
            params["water_needs_mm_day"] *= 1.1  # Más evapotranspiración
        
        return params

class CropNetworkCR:
    """
    Simulador de red agrícola de Costa Rica
    Fincas representativas por región y cultivo
    """
    
    def __init__(self):
        self.sensors = {}
        self.setup_agricultural_network()
    
    def setup_agricultural_network(self):
        """Configurar red de sensores agrícolas"""
        
        # Fincas de café (regiones altas)
        coffee_farms = [
            CropSensor(
                "tarrazú_coffee_001", (9.6167, -83.7833),
                "Finca Los Tarrazos", "coffee",
                ["soil_moisture", "temperature", "humidity", "ph", "nutrients"],
                "2024-01-15", 12.5, "drip", "+506-8888-2001", "Tarrazú", 1450
            ),
            CropSensor(
                "naranjo_coffee_002", (10.0833, -84.3833),
                "Café Villa Naranjo", "coffee", 
                ["soil_moisture", "temperature", "humidity", "ph", "light"],
                "2024-02-01", 8.3, "sprinkler", "+506-8888-2002", "Naranjo", 1200
            ),
            CropSensor(
                "dota_coffee_003", (9.5500, -83.9500),
                "Cooperativa Coopedota", "coffee",
                ["soil_moisture", "temperature", "humidity", "nutrients", "light"],
                "2024-01-20", 25.0, "drip", "+506-8888-2003", "Dota", 1650
            ),
        ]
        
        # Plantaciones de banano (zonas bajas)
        banana_farms = [
            CropSensor(
                "limon_banana_001", (10.0000, -83.1667),
                "Bananera del Caribe", "banana",
                ["soil_moisture", "temperature", "humidity", "nutrients", "leaf_wetness"],
                "2024-01-25", 45.0, "flood", "+506-8888-3001", "Limón", 25
            ),
            CropSensor(
                "san_carlos_banana_002", (10.3833, -84.4333),
                "Bananos San Carlos", "banana",
                ["soil_moisture", "temperature", "humidity", "ph", "nutrients"],
                "2024-02-10", 38.5, "sprinkler", "+506-8888-3002", "San Carlos", 150
            ),
        ]
        
        # Piñeras (zonas norte)
        pineapple_farms = [
            CropSensor(
                "san_carlos_pineapple_001", (10.4667, -84.6167),
                "Piñas Oro Verde", "pineapple",
                ["soil_moisture", "temperature", "humidity", "ph", "nutrients", "light"],
                "2024-01-30", 120.0, "drip", "+506-8888-4001", "San Carlos", 200
            ),
            CropSensor(
                "osa_pineapple_002", (8.8000, -83.5500),
                "Pineapple Paradise", "pineapple",
                ["soil_moisture", "temperature", "humidity", "nutrients"],
                "2024-02-15", 85.0, "drip", "+506-8888-4002", "Osa", 100
            ),
        ]
        
        # Palmito (zona sur)
        palmito_farms = [
            CropSensor(
                "perez_zeledon_palmito_001", (9.3333, -83.7000),
                "Palmitos del General", "palmito",
                ["soil_moisture", "temperature", "humidity", "ph", "nutrients", "leaf_wetness"],
                "2024-02-05", 15.5, "drip", "+506-8888-5001", "Pérez Zeledón", 650
            ),
        ]
        
        # Agregar todos los sensores
        for farm_list in [coffee_farms, banana_farms, pineapple_farms, palmito_farms]:
            for sensor in farm_list:
                self.sensors[sensor.sensor_id] = sensor
    
    def simulate_crop_reading(self, sensor_id: str) -> CropReading:
        """Simular lectura de sensores agrícolas"""
        
        if sensor_id not in self.sensors:
            raise ValueError(f"Sensor {sensor_id} no encontrado")
        
        sensor = self.sensors[sensor_id]
        current_time = datetime.now()
        
        # Obtener parámetros óptimos para el cultivo
        optimal = CostaRicaCropDatabase.get_optimal_ranges(sensor.crop_type, sensor.elevation)
        
        # Simular condiciones base según cultivo y región
        base_moisture = (optimal["optimal_moisture"]["min"] + optimal["optimal_moisture"]["max"]) / 2
        base_temp = (optimal["optimal_temp"]["min"] + optimal["optimal_temp"]["max"]) / 2
        base_ph = (optimal["optimal_ph"]["min"] + optimal["optimal_ph"]["max"]) / 2
        
        # Variaciones por hora del día
        hour = current_time.hour
        if 6 <= hour <= 18:  # Día
            temp_variation = 5 * np.sin((hour - 6) * np.pi / 12)  # Pico al mediodía
            humidity_variation = -15 * np.sin((hour - 6) * np.pi / 12)  # Mínimo al mediodía
        else:  # Noche
            temp_variation = -3
            humidity_variation = 10
        
        # Simulación estacional (simplificada)
        month = current_time.month
        if month in [12, 1, 2]:  # Época seca
            moisture_factor = 0.8
            rainfall_effect = -5
        elif month in [9, 10, 11]:  # Lluvias intensas
            moisture_factor = 1.2
            rainfall_effect = 15
        else:  # Transición
            moisture_factor = 1.0
            rainfall_effect = 0
        
        # Generar lecturas con variación natural
        reading = CropReading(
            sensor_id=sensor_id,
            timestamp=current_time,
            soil_moisture=max(20, min(95, base_moisture * moisture_factor + rainfall_effect + np.random.normal(0, 5))),
            soil_temperature=max(15, base_temp + temp_variation + np.random.normal(0, 2)),
            air_temperature=max(18, base_temp + temp_variation + 2 + np.random.normal(0, 3)),
            air_humidity=max(40, min(95, 75 + humidity_variation + rainfall_effect + np.random.normal(0, 8))),
            soil_ph=max(4.0, min(8.0, base_ph + np.random.normal(0, 0.3))),
            nitrogen=max(10, 50 + np.random.normal(0, 15)),  # ppm
            phosphorus=max(5, 25 + np.random.normal(0, 8)),   # ppm
            potassium=max(20, 120 + np.random.normal(0, 30)), # ppm
            light_intensity=max(0, 30000 * max(0, np.sin((hour - 6) * np.pi / 12)) + np.random.normal(0, 5000)),
            leaf_wetness=max(0, min(100, rainfall_effect * 2 + 30 + np.random.normal(0, 10))),
            battery_level=max(5, 85 + np.random.normal(0, 10))
        )
        
        return reading

class SmartIrrigationController:
    """
    Controlador inteligente de riego
    Optimiza uso de agua basado en condiciones del cultivo
    """
    
    def __init__(self):
        self.irrigation_enabled = True
        self.water_conservation_mode = False
        self.scheduling_algorithm = "ai_optimized"
    
    def evaluate_irrigation_need(self, reading: CropReading, sensor: CropSensor, weather_forecast: Dict = None) -> Optional[IrrigationEvent]:
        """Evaluar necesidad de riego y programar si es necesario"""
        
        try:
            # Obtener parámetros óptimos
            optimal = CostaRicaCropDatabase.get_optimal_ranges(sensor.crop_type, sensor.elevation)
            
            current_time = datetime.now()
            
            # Evaluar condiciones actuales
            moisture_deficit = optimal["optimal_moisture"]["min"] - reading.soil_moisture
            temp_stress = max(0, reading.air_temperature - optimal["optimal_temp"]["max"])
            
            # Determinar etapa del cultivo (simplificado)
            month = current_time.month
            if sensor.crop_type == "coffee":
                if month in [3, 4, 5]:
                    crop_stage = "flowering"
                elif month in [6, 7, 8]:
                    crop_stage = "fruiting"
                elif month in [11, 12, 1, 2]:
                    crop_stage = "harvest"
                else:
                    crop_stage = "vegetative"
            else:
                crop_stage = "vegetative"  # Simplificado
            
            # Factores de decisión
            needs_irrigation = False
            trigger_reason = ""
            priority_score = 0
            
            # 1. Humedad del suelo baja
            if moisture_deficit > 5:  # 5% por debajo del mínimo
                needs_irrigation = True
                trigger_reason = "moisture_low"
                priority_score += moisture_deficit * 0.1
            
            # 2. Estrés por temperatura
            if temp_stress > 3:  # >3°C sobre óptimo
                needs_irrigation = True
                trigger_reason += "_temperature_high" if trigger_reason else "temperature_high"
                priority_score += temp_stress * 0.05
            
            # 3. Etapa crítica del cultivo
            if crop_stage in ["flowering", "fruiting"]:
                if moisture_deficit > 2:  # Más sensible en etapas críticas
                    needs_irrigation = True
                    trigger_reason += "_critical_stage" if trigger_reason else "critical_stage"
                    priority_score += 0.3
            
            # 4. Pronóstico de sequía (si disponible)
            if weather_forecast and weather_forecast.get("rain_probability", 50) < 20:
                days_no_rain = weather_forecast.get("days_without_rain", 0)
                if days_no_rain > 3:
                    needs_irrigation = True
                    trigger_reason += "_forecast_dry" if trigger_reason else "forecast_dry"
                    priority_score += 0.2
            
            if not needs_irrigation:
                return None
            
            # Calcular duración y volumen de riego
            water_needed_mm = optimal["water_needs_mm_day"]
            
            # Ajustar por déficit de humedad
            if moisture_deficit > 10:
                water_multiplier = 1.3
            elif moisture_deficit > 5:
                water_multiplier = 1.1
            else:
                water_multiplier = 1.0
            
            # Ajustar por etapa del cultivo
            stage_multipliers = {
                "seedling": 0.7,
                "vegetative": 1.0,
                "flowering": 1.3,
                "fruiting": 1.4,
                "harvest": 0.8
            }
            water_multiplier *= stage_multipliers.get(crop_stage, 1.0)
            
            # Calcular volumen (L/m²/día a L totales)
            area_m2 = sensor.farm_size_hectares * 10000
            daily_water_liters = water_needed_mm * area_m2 / 1000  # mm a L
            irrigation_water_liters = daily_water_liters * water_multiplier * 0.3  # 30% de la necesidad diaria
            
            # Duración según sistema de riego
            if sensor.irrigation_system == "drip":
                duration_minutes = int(irrigation_water_liters / (area_m2 * 0.5))  # 0.5 L/min/m² aprox
            elif sensor.irrigation_system == "sprinkler":
                duration_minutes = int(irrigation_water_liters / (area_m2 * 1.0))  # 1.0 L/min/m² aprox
            else:  # flood
                duration_minutes = int(irrigation_water_liters / (area_m2 * 2.0))  # 2.0 L/min/m² aprox
            
            duration_minutes = max(10, min(120, duration_minutes))  # Entre 10 min y 2 horas
            
            # Calcular eficiencia
            efficiency_factors = {
                "drip": 0.9,
                "sprinkler": 0.7,
                "flood": 0.5,
                "manual": 0.6
            }
            base_efficiency = efficiency_factors.get(sensor.irrigation_system, 0.7)
            
            # Penalizar por horario (evitar horas de calor)
            if 11 <= current_time.hour <= 15:
                efficiency_penalty = 0.2
            else:
                efficiency_penalty = 0.0
            
            efficiency_score = base_efficiency - efficiency_penalty
            
            # Crear evento de riego
            event_id = f"IRR_{sensor.sensor_id}_{int(current_time.timestamp())}"
            
            irrigation_event = IrrigationEvent(
                event_id=event_id,
                sensor_id=sensor.sensor_id,
                trigger_time=current_time,
                duration_minutes=duration_minutes,
                water_volume_liters=round(irrigation_water_liters, 1),
                trigger_reason=trigger_reason,
                efficiency_score=round(efficiency_score, 2),
                crop_stage=crop_stage
            )
            
            logger.info(f"💧 RIEGO PROGRAMADO: {event_id}")
            logger.info(f"   🌱 Cultivo: {sensor.crop_type} ({crop_stage})")
            logger.info(f"   💦 Volumen: {irrigation_water_liters:.1f}L durante {duration_minutes}min")
            logger.info(f"   📊 Eficiencia: {efficiency_score:.1%}")
            logger.info(f"   🎯 Razón: {trigger_reason}")
            
            return irrigation_event
            
        except Exception as e:
            logger.error(f"❌ Error evaluando riego: {e}")
            return None

class CropHealthAnalyzer:
    """
    Analizador de salud de cultivos con IA
    Detecta problemas nutricionales, plagas y enfermedades
    """
    
    def __init__(self):
        self.disease_patterns = {}
        self.nutritional_thresholds = {}
        self.pest_indicators = {}
    
    def analyze_crop_health(self, reading: CropReading, sensor: CropSensor) -> List[CropAlert]:
        """Analizar salud del cultivo y generar alertas"""
        
        alerts = []
        current_time = reading.timestamp
        
        try:
            # Obtener parámetros óptimos
            optimal = CostaRicaCropDatabase.get_optimal_ranges(sensor.crop_type, sensor.elevation)
            
            # 1. Análisis de humedad del suelo
            if reading.soil_moisture < optimal["optimal_moisture"]["min"] - 10:
                alert = CropAlert(
                    alert_id=f"MOIST_{sensor.sensor_id}_{int(current_time.timestamp())}",
                    sensor_id=sensor.sensor_id,
                    farm_name=sensor.farm_name,
                    alert_type="moisture_low",
                    severity="high" if reading.soil_moisture < 30 else "medium",
                    description=f"Humedad del suelo crítica: {reading.soil_moisture:.1f}% (óptimo: {optimal['optimal_moisture']['min']}-{optimal['optimal_moisture']['max']}%)",
                    recommendations=[
                        "Activar sistema de riego inmediatamente",
                        "Verificar funcionamiento del sistema de riego",
                        "Considerar mulching para conservar humedad",
                        "Monitorear más frecuentemente por próximos 3 días"
                    ],
                    estimated_yield_impact=15.0 if reading.soil_moisture < 30 else 8.0,
                    detection_time=current_time
                )
                alerts.append(alert)
            
            # 2. Análisis de pH del suelo
            ph_optimal_range = optimal["optimal_ph"]
            if reading.soil_ph < ph_optimal_range["min"] - 0.5 or reading.soil_ph > ph_optimal_range["max"] + 0.5:
                severity = "high" if abs(reading.soil_ph - ((ph_optimal_range["min"] + ph_optimal_range["max"]) / 2)) > 1.0 else "medium"
                
                if reading.soil_ph < ph_optimal_range["min"]:
                    condition = "ácido"
                    recommendations = [
                        "Aplicar cal agrícola para elevar pH",
                        "Usar fertilizantes básicos",
                        "Incorporar materia orgánica (compost)",
                        "Realizar análisis de suelo completo"
                    ]
                else:
                    condition = "alcalino"
                    recommendations = [
                        "Aplicar azufre elemental para reducir pH",
                        "Usar fertilizantes acidificantes",
                        "Mejorar drenaje del suelo",
                        "Considerar cultivos tolerantes a pH alto"
                    ]
                
                alert = CropAlert(
                    alert_id=f"PH_{sensor.sensor_id}_{int(current_time.timestamp())}",
                    sensor_id=sensor.sensor_id,
                    farm_name=sensor.farm_name,
                    alert_type="ph_imbalance",
                    severity=severity,
                    description=f"pH del suelo {condition}: {reading.soil_ph:.1f} (óptimo: {ph_optimal_range['min']:.1f}-{ph_optimal_range['max']:.1f})",
                    recommendations=recommendations,
                    estimated_yield_impact=12.0 if severity == "high" else 6.0,
                    detection_time=current_time
                )
                alerts.append(alert)
            
            # 3. Análisis nutricional
            if reading.nitrogen < 30:  # ppm muy bajo
                alert = CropAlert(
                    alert_id=f"NUTR_N_{sensor.sensor_id}_{int(current_time.timestamp())}",
                    sensor_id=sensor.sensor_id,
                    farm_name=sensor.farm_name,
                    alert_type="nutrient_deficiency",
                    severity="high" if reading.nitrogen < 20 else "medium",
                    description=f"Deficiencia de nitrógeno: {reading.nitrogen:.1f} ppm",
                    recommendations=[
                        "Aplicar fertilizante nitrogenado inmediatamente",
                        "Usar abono orgánico rico en nitrógeno",
                        "Implementar rotación con leguminosas",
                        "Dividir aplicación en dosis menores frecuentes"
                    ],
                    estimated_yield_impact=20.0 if reading.nitrogen < 20 else 12.0,
                    detection_time=current_time
                )
                alerts.append(alert)
            
            # 4. Análisis de estrés térmico
            temp_stress = reading.air_temperature - optimal["optimal_temp"]["max"]
            if temp_stress > 5:  # >5°C sobre óptimo
                alert = CropAlert(
                    alert_id=f"TEMP_{sensor.sensor_id}_{int(current_time.timestamp())}",
                    sensor_id=sensor.sensor_id,
                    farm_name=sensor.farm_name,
                    alert_type="temperature_stress",
                    severity="critical" if temp_stress > 10 else "high",
                    description=f"Estrés térmico severo: {reading.air_temperature:.1f}°C (máx. óptimo: {optimal['optimal_temp']['max']}°C)",
                    recommendations=[
                        "Aumentar frecuencia de riego para enfriamiento",
                        "Implementar sombreado temporal",
                        "Aplicar riego por aspersión foliar",
                        "Monitorear signos de marchitez",
                        "Evitar aplicaciones de fertilizante hasta que baje temperatura"
                    ],
                    estimated_yield_impact=25.0 if temp_stress > 10 else 15.0,
                    detection_time=current_time
                )
                alerts.append(alert)
            
            # 5. Riesgo de enfermedades fúngicas (humedad foliar alta + temperatura cálida)
            if reading.leaf_wetness > 80 and reading.air_temperature > 25 and reading.air_humidity > 85:
                alert = CropAlert(
                    alert_id=f"DISEASE_{sensor.sensor_id}_{int(current_time.timestamp())}",
                    sensor_id=sensor.sensor_id,
                    farm_name=sensor.farm_name,
                    alert_type="disease_risk",
                    severity="high",
                    description=f"Alto riesgo de enfermedades fúngicas - Humedad foliar: {reading.leaf_wetness:.1f}%, Temp: {reading.air_temperature:.1f}°C",
                    recommendations=[
                        "Mejorar ventilación del cultivo",
                        "Aplicar fungicida preventivo si es necesario",
                        "Reducir riego por aspersión foliar",
                        "Inspeccionar plantas en busca de síntomas",
                        "Aumentar distancia entre plantas si es posible"
                    ],
                    estimated_yield_impact=30.0,
                    detection_time=current_time
                )
                alerts.append(alert)
            
            # 6. Batería baja del sensor
            if reading.battery_level < 20:
                alert = CropAlert(
                    alert_id=f"BATT_{sensor.sensor_id}_{int(current_time.timestamp())}",
                    sensor_id=sensor.sensor_id,
                    farm_name=sensor.farm_name,
                    alert_type="sensor_maintenance",
                    severity="medium" if reading.battery_level > 10 else "high",
                    description=f"Batería del sensor baja: {reading.battery_level:.1f}%",
                    recommendations=[
                        "Programar mantenimiento del sensor",
                        "Reemplazar o recargar batería",
                        "Verificar panel solar si aplica",
                        "Limpiar sensores de polvo/suciedad"
                    ],
                    estimated_yield_impact=0.0,  # No afecta rendimiento directamente
                    detection_time=current_time
                )
                alerts.append(alert)
            
            return alerts
            
        except Exception as e:
            logger.error(f"❌ Error analizando salud del cultivo: {e}")
            return []

class SmartAgricultureCore:
    """
    Núcleo principal del sistema de agricultura inteligente
    Integra sensores, riego inteligente y análisis de cultivos
    """
    
    def __init__(self):
        self.crop_network = CropNetworkCR()
        self.irrigation_controller = SmartIrrigationController()
        self.health_analyzer = CropHealthAnalyzer()
        self.is_monitoring = False
        self.current_readings = {}
        self.active_alerts = {}
        self.irrigation_events = {}
    
    async def start_monitoring(self) -> None:
        """Iniciar monitoreo continuo agrícola"""
        
        logger.info("🌱 Iniciando monitoreo agrícola inteligente...")
        self.is_monitoring = True
        
        # Monitoreo continuo
        while self.is_monitoring:
            try:
                # Monitorear sensores agrícolas
                await self._monitor_all_sensors()
                
                # Evaluar riego cada 30 minutos
                if datetime.now().minute % 30 == 0:
                    await self._evaluate_irrigation_needs()
                
                await asyncio.sleep(900)  # Cada 15 minutos
                
            except Exception as e:
                logger.error(f"❌ Error en monitoreo agrícola: {e}")
                await asyncio.sleep(300)
    
    async def _monitor_all_sensors(self) -> None:
        """Monitorear todos los sensores agrícolas"""
        
        for sensor_id in self.crop_network.sensors.keys():
            try:
                # Generar lectura simulada
                reading = self.crop_network.simulate_crop_reading(sensor_id)
                self.current_readings[sensor_id] = reading
                
                # Analizar salud del cultivo
                sensor = self.crop_network.sensors[sensor_id]
                alerts = self.health_analyzer.analyze_crop_health(reading, sensor)
                
                # Procesar alertas
                for alert in alerts:
                    self.active_alerts[alert.alert_id] = alert
                    await self._process_crop_alert(alert)
                
                # Log condiciones críticas
                if reading.soil_moisture < 40 or reading.battery_level < 15:
                    logger.warning(
                        f"⚠️ {sensor_id}: Humedad={reading.soil_moisture:.1f}%, "
                        f"Temp={reading.air_temperature:.1f}°C, "
                        f"Batería={reading.battery_level:.1f}%"
                    )
                
            except Exception as e:
                logger.error(f"❌ Error monitoreando sensor agrícola {sensor_id}: {e}")
    
    async def _evaluate_irrigation_needs(self) -> None:
        """Evaluar necesidades de riego para todas las fincas"""
        
        for sensor_id, reading in self.current_readings.items():
            try:
                sensor = self.crop_network.sensors[sensor_id]
                
                # Evaluar necesidad de riego
                irrigation_event = self.irrigation_controller.evaluate_irrigation_need(
                    reading, sensor, weather_forecast=None  # TODO: Integrar pronóstico
                )
                
                if irrigation_event:
                    self.irrigation_events[irrigation_event.event_id] = irrigation_event
                    await self._execute_irrigation(irrigation_event)
                
            except Exception as e:
                logger.error(f"❌ Error evaluando riego para {sensor_id}: {e}")
    
    async def _process_crop_alert(self, alert: CropAlert) -> None:
        """Procesar alerta de cultivo"""
        
        try:
            logger.warning(f"🚨 ALERTA AGRÍCOLA: {alert.alert_id}")
            logger.warning(f"   🏡 Finca: {alert.farm_name}")
            logger.warning(f"   🌾 Tipo: {alert.alert_type} ({alert.severity})")
            logger.warning(f"   📄 {alert.description}")
            
            if alert.estimated_yield_impact > 10:
                logger.warning(f"   📉 Impacto estimado en rendimiento: {alert.estimated_yield_impact:.1f}%")
            
            # TODO: Enviar notificaciones reales
            # - WhatsApp al agricultor
            # - Email con recomendaciones detalladas
            # - Integrar con SENASA para reportes fitosanitarios
            # - Dashboard web para técnicos agrónomos
            
        except Exception as e:
            logger.error(f"❌ Error procesando alerta: {e}")
    
    async def _execute_irrigation(self, event: IrrigationEvent) -> None:
        """Ejecutar evento de riego (simulado)"""
        
        try:
            logger.info(f"💧 EJECUTANDO RIEGO: {event.event_id}")
            logger.info(f"   ⏱️ Duración: {event.duration_minutes} minutos")
            logger.info(f"   💧 Volumen: {event.water_volume_liters:.1f} litros")
            logger.info(f"   🎯 Razón: {event.trigger_reason}")
            
            # TODO: Integración real con sistemas de riego
            # - Activar válvulas solenoides via LoRa
            # - Monitorear presión de agua
            # - Confirmar ejecución exitosa
            # - Medir volumen real dispensado
            
        except Exception as e:
            logger.error(f"❌ Error ejecutando riego: {e}")
    
    async def get_system_status(self) -> Dict:
        """Obtener estado del sistema agrícola"""
        
        try:
            total_sensors = len(self.crop_network.sensors)
            active_alerts = len(self.active_alerts)
            recent_irrigations = len([e for e in self.irrigation_events.values() 
                                   if (datetime.now() - e.trigger_time).days < 1])
            
            # Estadísticas por cultivo
            crop_stats = {}
            for sensor in self.crop_network.sensors.values():
                crop_stats[sensor.crop_type] = crop_stats.get(sensor.crop_type, 0) + 1
            
            # Estadísticas de alertas por tipo
            alert_stats = {}
            for alert in self.active_alerts.values():
                alert_stats[alert.alert_type] = alert_stats.get(alert.alert_type, 0) + 1
            
            # Calcular área total monitoreada
            total_hectares = sum(sensor.farm_size_hectares for sensor in self.crop_network.sensors.values())
            
            # Estimaciones de producción (simplificado)
            if self.current_readings:
                avg_moisture = np.mean([r.soil_moisture for r in self.current_readings.values()])
                avg_temp = np.mean([r.air_temperature for r in self.current_readings.values()])
                health_score = max(0, min(100, 100 - (active_alerts * 10)))  # Simplificado
            else:
                avg_moisture = 0
                avg_temp = 0
                health_score = 100
            
            # Eficiencia hídrica
            if self.irrigation_events:
                avg_efficiency = np.mean([e.efficiency_score for e in self.irrigation_events.values()])
                total_water_used = sum([e.water_volume_liters for e in self.irrigation_events.values()])
            else:
                avg_efficiency = 0
                total_water_used = 0
            
            return {
                "system_status": "monitoring" if self.is_monitoring else "stopped",
                "agricultural_infrastructure": {
                    "total_sensors": total_sensors,
                    "monitored_area_hectares": round(total_hectares, 1),
                    "crop_distribution": crop_stats,
                    "irrigation_systems": ["drip", "sprinkler", "flood", "manual"]
                },
                "current_conditions": {
                    "average_soil_moisture": round(avg_moisture, 1),
                    "average_temperature": round(avg_temp, 1),
                    "overall_health_score": round(health_score, 1),
                    "active_alerts": active_alerts
                },
                "alert_breakdown": alert_stats,
                "irrigation_efficiency": {
                    "recent_irrigation_events": recent_irrigations,
                    "average_efficiency_score": round(avg_efficiency, 2),
                    "total_water_used_liters_24h": round(total_water_used, 1),
                    "water_saved_vs_traditional": f"{(avg_efficiency - 0.5) * 100:.1f}%" if avg_efficiency > 0 else "0%"
                },
                "coverage_regions": {
                    "coffee_regions": ["Tarrazú", "Naranjo", "Dota"],
                    "banana_regions": ["Limón", "San Carlos"],
                    "pineapple_regions": ["San Carlos", "Osa"],
                    "palmito_regions": ["Pérez Zeledón"]
                },
                "economic_impact": {
                    "estimated_yield_protection": f"{max(0, 100 - sum(a.estimated_yield_impact for a in self.active_alerts.values())):.1f}%",
                    "water_cost_savings_annual": f"${avg_efficiency * total_hectares * 120:.0f}" if avg_efficiency > 0 else "$0",
                    "crop_value_protected": f"${total_hectares * 8500:.0f}",  # $8,500/ha promedio
                    "sustainability_score": min(100, health_score + avg_efficiency * 50)
                },
                "last_update": datetime.now().isoformat()
            }
            
        except Exception as e:
            logger.error(f"❌ Error obteniendo estado del sistema: {e}")
            return {"error": str(e)}
