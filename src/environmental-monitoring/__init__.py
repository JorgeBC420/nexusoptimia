"""
Módulo de Monitoreo Ambiental - NexusOptim IA
Sistema inteligente para monitoreo de calidad del aire y condiciones ambientales

Funcionalidades:
- Monitoreo de PM2.5, PM10, CO2, O3, NO2, SO2
- Predicción de calidad del aire con IA
- Alertas tempranas por contaminación
- Correlación con datos meteorológicos
- Cumplimiento normativo SENASA/MINAE
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
class AirQualitySensor:
    """Sensor de calidad del aire"""
    sensor_id: str
    location: Tuple[float, float]  # (lat, lon)
    sensor_types: List[str]  # ["pm25", "pm10", "co2", "o3", "no2", "so2", "temperature", "humidity"]
    installation_date: str
    zone_type: str  # "urban", "industrial", "rural", "coastal"
    municipality: str
    elevation: float  # metros sobre nivel del mar
    calibration_date: str

@dataclass
class AirQualityReading:
    """Lectura de calidad del aire"""
    sensor_id: str
    timestamp: datetime
    pm25: float  # μg/m³
    pm10: float  # μg/m³ 
    co2: float   # ppm
    o3: float    # ppb
    no2: float   # ppb
    so2: float   # ppb
    temperature: float  # °C
    humidity: float     # %
    pressure: float     # hPa
    wind_speed: float   # m/s
    wind_direction: float  # grados

@dataclass
class AirQualityAlert:
    """Alerta de calidad del aire"""
    alert_id: str
    sensor_id: str
    location: Tuple[float, float]
    alert_type: str  # "pm25_high", "co2_high", "ozone_warning", "pollution_spike"
    severity: str    # "moderate", "unhealthy", "hazardous"
    current_aqi: int  # Air Quality Index
    pollutant: str
    concentration: float
    health_message: str
    recommendations: List[str]
    detection_time: datetime

class CostaRicaAirQualityStandards:
    """
    Estándares de calidad del aire de Costa Rica
    Basado en MINAE y WHO guidelines
    """
    
    # Límites diarios (μg/m³)
    PM25_DAILY_LIMIT = 25.0    # WHO 2021
    PM10_DAILY_LIMIT = 50.0    # WHO 2021
    
    # Límites horarios (ppb)
    O3_HOURLY_LIMIT = 60.0     # Costa Rica MINAE
    NO2_HOURLY_LIMIT = 40.0    # WHO
    SO2_HOURLY_LIMIT = 20.0    # WHO 2021
    
    # CO2 (ppm) - para espacios cerrados principalmente
    CO2_NORMAL = 400.0
    CO2_ELEVATED = 800.0
    CO2_HIGH = 1200.0
    
    @staticmethod
    def calculate_aqi(pollutant: str, concentration: float) -> int:
        """Calcular Air Quality Index según estándares CR"""
        
        if pollutant == "pm25":
            if concentration <= 12:
                return int(50 * concentration / 12)
            elif concentration <= 35:
                return int(50 + 50 * (concentration - 12) / (35 - 12))
            elif concentration <= 55:
                return int(100 + 50 * (concentration - 35) / (55 - 35))
            elif concentration <= 150:
                return int(150 + 100 * (concentration - 55) / (150 - 55))
            else:
                return min(500, int(250 + 250 * (concentration - 150) / 150))
        
        elif pollutant == "pm10":
            if concentration <= 50:
                return int(50 * concentration / 50)
            elif concentration <= 100:
                return int(50 + 50 * (concentration - 50) / (100 - 50))
            elif concentration <= 250:
                return int(100 + 100 * (concentration - 100) / (250 - 100))
            else:
                return min(500, int(200 + 200 * (concentration - 250) / 250))
        
        elif pollutant == "o3":
            if concentration <= 60:
                return int(50 * concentration / 60)
            elif concentration <= 120:
                return int(50 + 50 * (concentration - 60) / (120 - 60))
            elif concentration <= 180:
                return int(100 + 100 * (concentration - 120) / (180 - 120))
            else:
                return min(500, int(200 + 200 * (concentration - 180) / 180))
        
        return 0  # Pollutant no reconocido

class AirQualityPredictor:
    """
    Sistema de IA para predicción de calidad del aire
    Usa datos meteorológicos y patrones históricos
    """
    
    def __init__(self):
        self.model_loaded = False
        self.feature_scaler = None
        self.pollution_patterns = {}
        
    def predict_air_quality(self, sensor_data: Dict, weather_data: Dict) -> Dict:
        """Predecir calidad del aire para próximas 24 horas"""
        
        try:
            current_time = datetime.now()
            predictions = []
            
            # Obtener datos actuales
            current_pm25 = sensor_data.get("pm25", 15.0)
            current_temp = weather_data.get("temperature", 25.0)
            current_humidity = weather_data.get("humidity", 70.0)
            current_wind = weather_data.get("wind_speed", 2.0)
            
            # Simular predicciones por hora (en producción: usar modelo real)
            for hour in range(24):
                future_time = current_time + timedelta(hours=hour)
                
                # Factores que afectan calidad del aire
                hour_of_day = future_time.hour
                day_of_week = future_time.weekday()
                
                # Patrón diario (tráfico matutino y vespertino)
                traffic_factor = 1.0
                if 7 <= hour_of_day <= 9 or 17 <= hour_of_day <= 19:
                    traffic_factor = 1.4  # Horas pico
                elif 22 <= hour_of_day or hour_of_day <= 5:
                    traffic_factor = 0.7  # Madrugada
                
                # Factor climático
                weather_factor = 1.0
                if current_wind < 1.0:  # Poco viento = acumulación
                    weather_factor *= 1.3
                if current_humidity > 80:  # Alta humedad = partículas
                    weather_factor *= 1.2
                if current_temp > 30:  # Alta temperatura = reacciones químicas
                    weather_factor *= 1.1
                
                # Factor semanal (menos contaminación fines de semana)
                weekly_factor = 0.8 if day_of_week >= 5 else 1.0
                
                # Predicción combinada
                predicted_pm25 = current_pm25 * traffic_factor * weather_factor * weekly_factor
                predicted_pm25 += np.random.normal(0, 2)  # Variación natural
                predicted_pm25 = max(5.0, predicted_pm25)  # Mínimo realista
                
                # Calcular AQI
                predicted_aqi = CostaRicaAirQualityStandards.calculate_aqi("pm25", predicted_pm25)
                
                # Categorizar calidad
                if predicted_aqi <= 50:
                    quality_category = "good"
                    health_message = "Calidad del aire satisfactoria"
                elif predicted_aqi <= 100:
                    quality_category = "moderate"
                    health_message = "Aceptable para la mayoría de personas"
                elif predicted_aqi <= 150:
                    quality_category = "unhealthy_sensitive"
                    health_message = "Grupos sensibles pueden experimentar síntomas"
                elif predicted_aqi <= 200:
                    quality_category = "unhealthy"
                    health_message = "Todos pueden experimentar efectos en la salud"
                else:
                    quality_category = "hazardous"
                    health_message = "Condiciones peligrosas para todos"
                
                prediction = {
                    "hour_offset": hour,
                    "datetime": future_time.isoformat(),
                    "predicted_pm25": round(predicted_pm25, 1),
                    "predicted_aqi": predicted_aqi,
                    "quality_category": quality_category,
                    "health_message": health_message,
                    "confidence": 0.75 - (hour * 0.02)  # Confianza disminuye con tiempo
                }
                
                predictions.append(prediction)
            
            return {
                "sensor_id": sensor_data.get("sensor_id"),
                "forecast_generated": current_time.isoformat(),
                "location": sensor_data.get("location"),
                "predictions": predictions,
                "model_version": "v1.0_simulation"
            }
            
        except Exception as e:
            logger.error(f"❌ Error prediciendo calidad del aire: {e}")
            return {"error": str(e)}

class AirQualityNetworkCR:
    """
    Simulador de red de monitoreo de calidad del aire en Costa Rica
    Basado en ubicaciones estratégicas del país
    """
    
    def __init__(self):
        self.sensors = {}
        self.setup_costa_rica_network()
    
    def setup_costa_rica_network(self):
        """Configurar red de sensores para Costa Rica"""
        
        # Estaciones urbanas principales
        urban_stations = [
            AirQualitySensor(
                "san_jose_centro", (9.9333, -84.0833), 
                ["pm25", "pm10", "co2", "o3", "no2", "temperature", "humidity"],
                "2024-01-15", "urban", "San José", 1150, "2024-07-01"
            ),
            AirQualitySensor(
                "cartago_centro", (9.8667, -83.9167),
                ["pm25", "pm10", "o3", "temperature", "humidity"], 
                "2024-02-01", "urban", "Cartago", 1435, "2024-07-01"
            ),
            AirQualitySensor(
                "alajuela_aeropuerto", (10.0167, -84.2167),
                ["pm25", "pm10", "co2", "no2", "so2", "temperature", "humidity"],
                "2024-01-20", "urban", "Alajuela", 955, "2024-07-01"
            ),
            AirQualitySensor(
                "heredia_universidad", (9.9833, -84.1167),
                ["pm25", "pm10", "o3", "temperature", "humidity"],
                "2024-02-10", "urban", "Heredia", 1180, "2024-07-01"
            ),
        ]
        
        # Estaciones industriales
        industrial_stations = [
            AirQualitySensor(
                "moín_refinería", (10.0000, -83.0833),
                ["pm25", "pm10", "so2", "no2", "co2", "temperature", "humidity"],
                "2024-01-25", "industrial", "Limón", 5, "2024-07-01"
            ),
            AirQualitySensor(
                "barranca_zona_franca", (10.0167, -84.7333),
                ["pm25", "pm10", "no2", "so2", "temperature", "humidity"],
                "2024-02-15", "industrial", "Puntarenas", 15, "2024-07-01"
            ),
        ]
        
        # Estaciones rurales/parques nacionales
        rural_stations = [
            AirQualitySensor(
                "monteverde_reserva", (10.3167, -84.8000),
                ["pm25", "co2", "o3", "temperature", "humidity"],
                "2024-01-30", "rural", "Puntarenas", 1400, "2024-07-01"
            ),
            AirQualitySensor(
                "manuel_antonio", (9.3833, -84.1500),
                ["pm25", "pm10", "temperature", "humidity"],
                "2024-02-20", "coastal", "Puntarenas", 50, "2024-07-01"
            ),
            AirQualitySensor(
                "irazú_volcán", (9.9792, -83.8519),
                ["pm25", "so2", "co2", "temperature", "humidity"],
                "2024-01-10", "rural", "Cartago", 3432, "2024-07-01"
            ),
        ]
        
        # Agregar todos los sensores
        for station_list in [urban_stations, industrial_stations, rural_stations]:
            for sensor in station_list:
                self.sensors[sensor.sensor_id] = sensor
    
    def simulate_air_quality_reading(self, sensor_id: str) -> AirQualityReading:
        """Simular lectura de calidad del aire"""
        
        if sensor_id not in self.sensors:
            raise ValueError(f"Sensor {sensor_id} no encontrado")
        
        sensor = self.sensors[sensor_id]
        current_time = datetime.now()
        
        # Valores base según tipo de zona
        base_values = {
            "urban": {"pm25": 18, "pm10": 35, "co2": 450, "o3": 45, "no2": 25, "so2": 5},
            "industrial": {"pm25": 25, "pm10": 50, "co2": 420, "o3": 60, "no2": 35, "so2": 15},
            "rural": {"pm25": 8, "pm10": 15, "co2": 380, "o3": 30, "no2": 8, "so2": 2},
            "coastal": {"pm25": 12, "pm10": 20, "co2": 400, "o3": 40, "no2": 15, "so2": 8}
        }
        
        base = base_values.get(sensor.zone_type, base_values["urban"])
        
        # Factores de variación
        hour = current_time.hour
        
        # Factor por hora del día
        if 7 <= hour <= 9 or 17 <= hour <= 19:  # Horas pico
            traffic_multiplier = 1.4
        elif 22 <= hour or hour <= 5:  # Madrugada
            traffic_multiplier = 0.7
        else:
            traffic_multiplier = 1.0
        
        # Simulación meteorológica simple
        temp = 25 + np.random.normal(0, 5)  # 20-30°C típico
        humidity = 70 + np.random.normal(0, 15)  # 55-85% típico CR
        pressure = 1013 + np.random.normal(0, 10)
        wind_speed = 2 + np.random.exponential(1.5)  # 0-5 m/s típico
        wind_direction = np.random.uniform(0, 360)
        
        # Ajustar contaminantes por condiciones meteorológicas
        wind_factor = max(0.5, 2.0 - wind_speed * 0.3)  # Menos viento = más contaminantes
        
        # Generar lecturas con variación natural
        reading = AirQualityReading(
            sensor_id=sensor_id,
            timestamp=current_time,
            pm25=max(2, base["pm25"] * traffic_multiplier * wind_factor + np.random.normal(0, 3)),
            pm10=max(5, base["pm10"] * traffic_multiplier * wind_factor + np.random.normal(0, 5)),
            co2=max(350, base["co2"] + np.random.normal(0, 30)),
            o3=max(10, base["o3"] + np.random.normal(0, 10)),
            no2=max(5, base["no2"] * traffic_multiplier + np.random.normal(0, 5)),
            so2=max(1, base["so2"] + np.random.normal(0, 2)),
            temperature=temp,
            humidity=max(30, min(95, humidity)),
            pressure=pressure,
            wind_speed=max(0, wind_speed),
            wind_direction=wind_direction
        )
        
        return reading

class AirQualityAlertSystem:
    """
    Sistema de alertas para calidad del aire
    Notificaciones automáticas por niveles peligrosos
    """
    
    def __init__(self):
        self.active_alerts = {}
        self.notification_thresholds = {
            "moderate": {"aqi": 51, "notify": ["health_sensitive"]},
            "unhealthy": {"aqi": 101, "notify": ["general_public", "health_dept"]},
            "hazardous": {"aqi": 201, "notify": ["emergency_services", "media", "government"]}
        }
    
    def evaluate_air_quality(self, reading: AirQualityReading) -> Optional[AirQualityAlert]:
        """Evaluar lectura y generar alerta si es necesario"""
        
        try:
            # Calcular AQI para cada contaminante
            pm25_aqi = CostaRicaAirQualityStandards.calculate_aqi("pm25", reading.pm25)
            pm10_aqi = CostaRicaAirQualityStandards.calculate_aqi("pm10", reading.pm10)
            o3_aqi = CostaRicaAirQualityStandards.calculate_aqi("o3", reading.o3)
            
            # Tomar el peor AQI
            max_aqi = max(pm25_aqi, pm10_aqi, o3_aqi)
            
            # Determinar contaminante dominante
            if pm25_aqi == max_aqi:
                dominant_pollutant = "pm25"
                concentration = reading.pm25
            elif pm10_aqi == max_aqi:
                dominant_pollutant = "pm10"
                concentration = reading.pm10
            else:
                dominant_pollutant = "o3"
                concentration = reading.o3
            
            # Evaluar si requiere alerta
            if max_aqi <= 50:
                return None  # Calidad buena, no alerta
            
            # Determinar severidad
            if max_aqi <= 100:
                severity = "moderate"
                health_message = "Personas sensibles deben considerar reducir actividades al aire libre prolongadas"
                alert_type = f"{dominant_pollutant}_moderate"
            elif max_aqi <= 150:
                severity = "unhealthy_sensitive"
                health_message = "Grupos sensibles deben evitar actividades al aire libre prolongadas"
                alert_type = f"{dominant_pollutant}_unhealthy_sensitive"
            elif max_aqi <= 200:
                severity = "unhealthy"
                health_message = "Todos deben evitar actividades al aire libre prolongadas"
                alert_type = f"{dominant_pollutant}_unhealthy"
            else:
                severity = "hazardous"
                health_message = "Condiciones peligrosas. Permanecer en interiores con ventanas cerradas"
                alert_type = f"{dominant_pollutant}_hazardous"
            
            # Generar recomendaciones
            recommendations = self._generate_recommendations(severity, dominant_pollutant)
            
            # Crear alerta
            alert_id = f"AQI_{reading.sensor_id}_{int(reading.timestamp.timestamp())}"
            
            alert = AirQualityAlert(
                alert_id=alert_id,
                sensor_id=reading.sensor_id,
                location=(0, 0),  # TODO: Obtener de sensor
                alert_type=alert_type,
                severity=severity,
                current_aqi=max_aqi,
                pollutant=dominant_pollutant,
                concentration=concentration,
                health_message=health_message,
                recommendations=recommendations,
                detection_time=reading.timestamp
            )
            
            logger.warning(f"🌬️ ALERTA CALIDAD AIRE: {alert_id} | AQI: {max_aqi} | {severity.upper()}")
            
            return alert
            
        except Exception as e:
            logger.error(f"❌ Error evaluando calidad del aire: {e}")
            return None
    
    def _generate_recommendations(self, severity: str, pollutant: str) -> List[str]:
        """Generar recomendaciones según severidad y contaminante"""
        
        base_recommendations = {
            "moderate": [
                "Grupos sensibles (niños, adultos mayores, personas con asma) deben limitar actividades al aire libre",
                "Use mascarilla si debe estar al aire libre por períodos prolongados",
                "Mantenga ventanas cerradas y use purificador de aire si es posible"
            ],
            "unhealthy_sensitive": [
                "Grupos sensibles deben evitar completamente actividades al aire libre",
                "Use mascarilla N95 si debe salir",
                "Mantenga espacios interiores bien ventilados con filtros HEPA",
                "Considere posponer actividades deportivas al aire libre"
            ],
            "unhealthy": [
                "Todos deben evitar actividades al aire libre prolongadas e intensas",
                "Use mascarilla N95 al salir",
                "Mantenga ventanas cerradas",
                "Use purificador de aire en interiores",
                "Consulte médico si experimenta síntomas respiratorios"
            ],
            "hazardous": [
                "PERMANEZCA EN INTERIORES CON VENTANAS Y PUERTAS CERRADAS",
                "Use mascarilla N95 incluso en interiores si es necesario",
                "Evite toda actividad física al aire libre",
                "Busque atención médica si tiene dificultades respiratorias",
                "Considere evacuar el área si es posible"
            ]
        }
        
        recommendations = base_recommendations.get(severity, [])
        
        # Recomendaciones específicas por contaminante
        if pollutant == "pm25" or pollutant == "pm10":
            recommendations.append("Las partículas finas pueden penetrar profundamente en los pulmones")
        elif pollutant == "o3":
            recommendations.append("El ozono es especialmente peligroso durante ejercicio físico")
        elif pollutant == "no2":
            recommendations.append("El dióxido de nitrógeno puede agravar el asma y reducir la inmunidad")
        
        return recommendations

class EnvironmentalMonitoringCore:
    """
    Núcleo principal del sistema de monitoreo ambiental
    Integra sensores, predicción y alertas
    """
    
    def __init__(self):
        self.network = AirQualityNetworkCR()
        self.predictor = AirQualityPredictor()
        self.alert_system = AirQualityAlertSystem()
        self.is_monitoring = False
        self.active_alerts = {}
    
    async def start_monitoring(self) -> None:
        """Iniciar monitoreo continuo de calidad del aire"""
        
        logger.info("🌿 Iniciando monitoreo de calidad del aire...")
        self.is_monitoring = True
        
        # Monitoreo continuo
        while self.is_monitoring:
            try:
                await self._monitor_all_sensors()
                await asyncio.sleep(300)  # Cada 5 minutos
                
            except Exception as e:
                logger.error(f"❌ Error en monitoreo ambiental: {e}")
                await asyncio.sleep(60)
    
    async def _monitor_all_sensors(self) -> None:
        """Monitorear todos los sensores de calidad del aire"""
        
        for sensor_id in self.network.sensors.keys():
            try:
                # Generar lectura simulada
                reading = self.network.simulate_air_quality_reading(sensor_id)
                
                # Evaluar para alertas
                alert = self.alert_system.evaluate_air_quality(reading)
                
                if alert:
                    self.active_alerts[alert.alert_id] = alert
                    await self._process_air_quality_alert(alert)
                
                # Log datos importantes
                if reading.pm25 > 25 or reading.o3 > 60:
                    logger.warning(
                        f"⚠️ {sensor_id}: PM2.5={reading.pm25:.1f}μg/m³, "
                        f"O3={reading.o3:.1f}ppb, AQI≈{CostaRicaAirQualityStandards.calculate_aqi('pm25', reading.pm25)}"
                    )
                
            except Exception as e:
                logger.error(f"❌ Error monitoreando sensor {sensor_id}: {e}")
    
    async def _process_air_quality_alert(self, alert: AirQualityAlert) -> None:
        """Procesar alerta de calidad del aire"""
        
        try:
            logger.warning(f"🚨 ALERTA CALIDAD AIRE: {alert.alert_id}")
            logger.warning(f"   📍 Sensor: {alert.sensor_id}")
            logger.warning(f"   🌬️ AQI: {alert.current_aqi} ({alert.severity})")
            logger.warning(f"   🔬 Contaminante: {alert.pollutant} = {alert.concentration:.1f}")
            logger.warning(f"   ⚕️ {alert.health_message}")
            
            # TODO: Enviar notificaciones reales
            # - SMS/WhatsApp a autoridades de salud
            # - Actualizar sitio web público
            # - Notificar aplicaciones móviles
            # - Integrar con sistema de emergencias 911
            
        except Exception as e:
            logger.error(f"❌ Error procesando alerta: {e}")
    
    async def get_system_status(self) -> Dict:
        """Obtener estado del sistema de monitoreo ambiental"""
        
        try:
            total_sensors = len(self.network.sensors)
            active_alerts = len(self.active_alerts)
            
            # Estadísticas por zona
            zone_stats = {"urban": 0, "industrial": 0, "rural": 0, "coastal": 0}
            for sensor in self.network.sensors.values():
                zone_stats[sensor.zone_type] = zone_stats.get(sensor.zone_type, 0) + 1
            
            # Estadísticas de alertas por severidad
            severity_stats = {"moderate": 0, "unhealthy_sensitive": 0, "unhealthy": 0, "hazardous": 0}
            for alert in self.active_alerts.values():
                severity_stats[alert.severity] = severity_stats.get(alert.severity, 0) + 1
            
            # Estimar población expuesta a mala calidad del aire
            exposed_population = sum(
                {"urban": 50000, "industrial": 15000, "rural": 5000, "coastal": 20000}[alert.severity] 
                for alert in self.active_alerts.values() 
                if alert.severity in ["unhealthy", "hazardous"]
            )
            
            return {
                "system_status": "monitoring" if self.is_monitoring else "stopped",
                "total_sensors": total_sensors,
                "zone_distribution": zone_stats,
                "active_alerts": active_alerts,
                "severity_breakdown": severity_stats,
                "estimated_exposed_population": exposed_population,
                "last_update": datetime.now().isoformat(),
                "coverage_municipalities": len(set(s.municipality for s in self.network.sensors.values())),
                "environmental_impact": {
                    "areas_monitored": ["GAM", "Zona Industrial Limón", "Parques Nacionales", "Zonas Costeras"],
                    "compliance_standards": ["MINAE Costa Rica", "WHO 2021", "EPA Guidelines"],
                    "data_frequency": "5 minutos",
                    "prediction_horizon": "24 horas"
                }
            }
            
        except Exception as e:
            logger.error(f"❌ Error obteniendo estado del sistema: {e}")
            return {"error": str(e)}
