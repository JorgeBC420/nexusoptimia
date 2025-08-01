"""
Módulo de Transporte Inteligente - NexusOptim IA
Sistema de gestión inteligente de tráfico y transporte público

Funcionalidades:
- Optimización de semáforos con IA
- Monitoreo de flujo vehicular en tiempo real
- Predicción de congestión vial
- Integración con transporte público (autobuses, tren)
- Gestión de rutas dinámicas para emergencias
- Correlación con consumo energético del transporte
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
class TrafficSensor:
    """Sensor de tráfico vehicular"""
    sensor_id: str
    location: Tuple[float, float]  # (lat, lon)
    sensor_type: str  # "loop_detector", "camera", "radar", "bluetooth"
    road_name: str
    direction: str  # "north", "south", "east", "west", "both"
    lanes_monitored: int
    speed_limit: int  # km/h
    installation_date: str
    municipality: str

@dataclass
class TrafficReading:
    """Lectura de datos de tráfico"""
    sensor_id: str
    timestamp: datetime
    vehicle_count: int  # vehículos por minuto
    average_speed: float  # km/h
    occupancy_rate: float  # % tiempo ocupado
    heavy_vehicles_pct: float  # % vehículos pesados
    queue_length: int  # metros de cola
    travel_time: float  # segundos para cruzar sensor

@dataclass
class SmartTrafficLight:
    """Semáforo inteligente"""
    light_id: str
    location: Tuple[float, float]
    intersection_name: str
    phases: List[Dict]  # Fases del semáforo
    current_phase: int
    sensors_linked: List[str]  # IDs de sensores asociados
    ai_controlled: bool
    last_optimization: datetime

@dataclass
class TrafficIncident:
    """Incidente de tráfico"""
    incident_id: str
    location: Tuple[float, float]
    incident_type: str  # "accident", "construction", "event", "weather"
    severity: str  # "low", "medium", "high", "critical"
    description: str
    affected_routes: List[str]
    estimated_duration: int  # minutos
    alternative_routes: List[str]
    detection_time: datetime

class SanJoseTrafficNetwork:
    """
    Simulador de red de tráfico del Gran Área Metropolitana
    Basado en intersecciones y vías principales de San José
    """
    
    def __init__(self):
        self.traffic_sensors = {}
        self.smart_lights = {}
        self.setup_gam_network()
    
    def setup_gam_network(self):
        """Configurar red de tráfico del GAM"""
        
        # Sensores en vías principales
        main_sensors = [
            TrafficSensor(
                "autopista_general_canas_a", (9.9358, -84.1041),
                "loop_detector", "Autopista General Cañas", "both", 6, 80,
                "2024-01-15", "San José"
            ),
            TrafficSensor(
                "circunvalacion_norte", (9.9500, -84.0800),
                "camera", "Circunvalación Norte", "both", 4, 60,
                "2024-01-20", "San José"
            ),
            TrafficSensor(
                "paseo_colon_sabana", (9.9333, -84.0900),
                "radar", "Paseo Colón", "both", 4, 50,
                "2024-02-01", "San José"
            ),
            TrafficSensor(
                "avenida_central_centro", (9.9333, -84.0833),
                "bluetooth", "Avenida Central", "both", 2, 25,
                "2024-02-10", "San José"
            ),
            TrafficSensor(
                "radial_cartago", (9.9167, -84.0500),
                "loop_detector", "Radial a Cartago", "both", 4, 60,
                "2024-01-25", "San José"
            ),
            TrafficSensor(
                "ruta_san_ramon", (9.9667, -84.1333),
                "camera", "Ruta a San Ramón", "both", 4, 80,
                "2024-02-05", "Alajuela"
            ),
        ]
        
        # Sensores en intersecciones críticas
        intersection_sensors = [
            TrafficSensor(
                "sabana_sur_interseccion", (9.9278, -84.0931),
                "camera", "Intersección Sabana Sur", "both", 2, 40,
                "2024-01-30", "San José"
            ),
            TrafficSensor(
                "rotonda_betania", (9.9194, -84.1139),
                "radar", "Rotonda Betania", "both", 3, 50,
                "2024-02-15", "San José"
            ),
            TrafficSensor(
                "hospital_mexico", (9.9517, -84.1258),
                "loop_detector", "Hospital México", "both", 4, 50,
                "2024-01-18", "San José"
            ),
        ]
        
        # Agregar sensores
        for sensor_list in [main_sensors, intersection_sensors]:
            for sensor in sensor_list:
                self.traffic_sensors[sensor.sensor_id] = sensor
        
        # Configurar semáforos inteligentes
        self.setup_smart_traffic_lights()
    
    def setup_smart_traffic_lights(self):
        """Configurar semáforos inteligentes"""
        
        smart_lights = [
            SmartTrafficLight(
                "semaforo_sabana_sur", (9.9278, -84.0931),
                "Intersección Sabana Sur",
                [
                    {"phase": "north_south", "duration": 45, "yellow": 3},
                    {"phase": "east_west", "duration": 35, "yellow": 3},
                    {"phase": "left_turns", "duration": 20, "yellow": 3}
                ],
                0, ["sabana_sur_interseccion"], True, datetime.now()
            ),
            SmartTrafficLight(
                "semaforo_hospital_mexico", (9.9517, -84.1258),
                "Hospital México",
                [
                    {"phase": "main_road", "duration": 50, "yellow": 3},
                    {"phase": "hospital_access", "duration": 25, "yellow": 3},
                    {"phase": "pedestrian", "duration": 15, "yellow": 0}
                ],
                0, ["hospital_mexico"], True, datetime.now()
            ),
        ]
        
        for light in smart_lights:
            self.smart_lights[light.light_id] = light
    
    def simulate_traffic_reading(self, sensor_id: str) -> TrafficReading:
        """Simular lectura de tráfico"""
        
        if sensor_id not in self.traffic_sensors:
            raise ValueError(f"Sensor {sensor_id} no encontrado")
        
        sensor = self.traffic_sensors[sensor_id]
        current_time = datetime.now()
        hour = current_time.hour
        day_of_week = current_time.weekday()
        
        # Patrones de tráfico por hora
        if 6 <= hour <= 9:  # Hora pico matutina
            traffic_multiplier = 1.8
            speed_factor = 0.6  # Más lento por congestión
        elif 17 <= hour <= 19:  # Hora pico vespertina
            traffic_multiplier = 2.0
            speed_factor = 0.5
        elif 12 <= hour <= 14:  # Hora almuerzo
            traffic_multiplier = 1.3
            speed_factor = 0.8
        elif 20 <= hour <= 23:  # Noche activa
            traffic_multiplier = 1.1
            speed_factor = 1.2
        elif 0 <= hour <= 5:  # Madrugada
            traffic_multiplier = 0.2
            speed_factor = 1.5
        else:  # Horas normales
            traffic_multiplier = 1.0
            speed_factor = 1.0
        
        # Factor de día de semana
        if day_of_week >= 5:  # Fin de semana
            traffic_multiplier *= 0.7
            speed_factor *= 1.2
        
        # Valores base según tipo de vía
        base_values = {
            "Autopista General Cañas": {"vehicles": 60, "speed": 70},
            "Circunvalación Norte": {"vehicles": 45, "speed": 50},
            "Paseo Colón": {"vehicles": 35, "speed": 35},
            "Avenida Central": {"vehicles": 25, "speed": 20},
            "Radial a Cartago": {"vehicles": 40, "speed": 55},
            "Ruta a San Ramón": {"vehicles": 50, "speed": 65}
        }
        
        base = base_values.get(sensor.road_name, {"vehicles": 30, "speed": 40})
        
        # Simular lecturas con variación natural
        vehicle_count = max(0, int(base["vehicles"] * traffic_multiplier * sensor.lanes_monitored / 2 + np.random.normal(0, 5)))
        avg_speed = max(5, base["speed"] * speed_factor + np.random.normal(0, 10))
        avg_speed = min(avg_speed, sensor.speed_limit * 1.1)  # No exceder mucho el límite
        
        # Calcular métricas derivadas
        occupancy_rate = min(95, (vehicle_count / (sensor.lanes_monitored * 15)) * 100)  # % ocupación
        heavy_vehicles_pct = max(5, 15 + np.random.normal(0, 5))  # % vehículos pesados
        
        # Cola de tráfico (inversamente proporcional a velocidad)
        queue_length = max(0, int((sensor.speed_limit - avg_speed) * 3 + np.random.normal(0, 20)))
        
        # Tiempo de viaje
        distance_meters = 100  # Distancia promedio monitoreada
        travel_time = (distance_meters / 1000) / (avg_speed / 3600)  # segundos
        
        return TrafficReading(
            sensor_id=sensor_id,
            timestamp=current_time,
            vehicle_count=vehicle_count,
            average_speed=round(avg_speed, 1),
            occupancy_rate=round(occupancy_rate, 1),
            heavy_vehicles_pct=round(heavy_vehicles_pct, 1),
            queue_length=queue_length,
            travel_time=round(travel_time, 1)
        )

class TrafficFlowPredictor:
    """
    Sistema de IA para predicción de flujo de tráfico
    Usa patrones históricos y eventos especiales
    """
    
    def __init__(self):
        self.model_loaded = False
        self.historical_patterns = {}
    
    def predict_traffic_flow(self, sensor_data: Dict, special_events: List[str] = None) -> Dict:
        """Predecir flujo de tráfico para próximas 2 horas"""
        
        try:
            current_time = datetime.now()
            predictions = []
            
            current_vehicles = sensor_data.get("vehicle_count", 30)
            current_speed = sensor_data.get("average_speed", 40)
            sensor_id = sensor_data.get("sensor_id", "unknown")
            
            for minute_offset in range(0, 120, 10):  # Cada 10 minutos por 2 horas
                future_time = current_time + timedelta(minutes=minute_offset)
                future_hour = future_time.hour
                future_day = future_time.weekday()
                
                # Predicción basada en patrones horarios
                if 6 <= future_hour <= 9 or 17 <= future_hour <= 19:
                    traffic_factor = 1.8
                    speed_factor = 0.6
                    congestion_level = "high"
                elif 12 <= future_hour <= 14:
                    traffic_factor = 1.3
                    speed_factor = 0.8
                    congestion_level = "medium"
                elif 0 <= future_hour <= 5:
                    traffic_factor = 0.3
                    speed_factor = 1.4
                    congestion_level = "low"
                else:
                    traffic_factor = 1.0
                    speed_factor = 1.0
                    congestion_level = "normal"
                
                # Factor fin de semana
                if future_day >= 5:
                    traffic_factor *= 0.7
                    speed_factor *= 1.2
                
                # Eventos especiales
                event_factor = 1.0
                if special_events:
                    for event in special_events:
                        if "futbol" in event.lower():
                            event_factor *= 1.5
                        elif "concierto" in event.lower():
                            event_factor *= 1.3
                        elif "lluvia" in event.lower():
                            traffic_factor *= 0.8
                            speed_factor *= 0.7
                
                # Calcular predicciones
                predicted_vehicles = int(current_vehicles * traffic_factor * event_factor)
                predicted_speed = round(current_speed * speed_factor, 1)
                
                # Añadir variación natural
                predicted_vehicles += int(np.random.normal(0, 3))
                predicted_speed += np.random.normal(0, 2)
                
                # Calcular tiempo de viaje estimado
                if predicted_speed > 0:
                    travel_time_factor = 40 / max(predicted_speed, 10)  # Tiempo base vs velocidad
                else:
                    travel_time_factor = 5.0
                
                prediction = {
                    "time_offset_minutes": minute_offset,
                    "datetime": future_time.isoformat(),
                    "predicted_vehicles": max(0, predicted_vehicles),
                    "predicted_speed": max(5, predicted_speed),
                    "congestion_level": congestion_level,
                    "travel_time_factor": round(travel_time_factor, 2),
                    "confidence": max(0.4, 0.9 - (minute_offset * 0.004))  # Confianza decrece con tiempo
                }
                
                predictions.append(prediction)
            
            return {
                "sensor_id": sensor_id,
                "forecast_generated": current_time.isoformat(),
                "predictions": predictions,
                "special_events_considered": special_events or [],
                "model_version": "v1.0_pattern_based"
            }
            
        except Exception as e:
            logger.error(f"❌ Error prediciendo tráfico: {e}")
            return {"error": str(e)}

class SmartTrafficLightController:
    """
    Controlador inteligente de semáforos
    Optimiza tiempos según flujo de tráfico en tiempo real
    """
    
    def __init__(self):
        self.optimization_enabled = True
        self.learning_rate = 0.1
        self.min_phase_duration = 15  # segundos mínimos por fase
        self.max_phase_duration = 120  # segundos máximos por fase
    
    def optimize_traffic_light(self, light: SmartTrafficLight, traffic_data: Dict) -> Dict:
        """Optimizar tiempos de semáforo basado en tráfico actual"""
        
        try:
            if not light.ai_controlled:
                return {"message": "Semáforo no habilitado para control IA"}
            
            current_time = datetime.now()
            
            # Obtener datos de tráfico de sensores asociados
            total_vehicles = 0
            average_speed = 0
            sensor_count = 0
            
            for sensor_id in light.sensors_linked:
                if sensor_id in traffic_data:
                    sensor_reading = traffic_data[sensor_id]
                    total_vehicles += sensor_reading.get("vehicle_count", 0)
                    average_speed += sensor_reading.get("average_speed", 40)
                    sensor_count += 1
            
            if sensor_count > 0:
                average_speed /= sensor_count
            else:
                average_speed = 40  # Default
            
            # Calcular nueva duración de fases
            new_phases = []
            
            for i, phase in enumerate(light.phases):
                current_duration = phase["duration"]
                
                # Factor de ajuste basado en tráfico
                if total_vehicles > 80:  # Tráfico alto
                    if i == 0:  # Fase principal - extender
                        adjustment_factor = 1.3
                    else:
                        adjustment_factor = 0.9  # Fases secundarias - reducir
                elif total_vehicles < 20:  # Tráfico bajo
                    if i == 0:
                        adjustment_factor = 0.8  # Reducir fase principal
                    else:
                        adjustment_factor = 1.1  # Permitir más tiempo para peatones
                else:  # Tráfico normal
                    adjustment_factor = 1.0
                
                # Factor de velocidad (tráfico lento necesita más tiempo)
                if average_speed < 20:
                    adjustment_factor *= 1.2
                elif average_speed > 50:
                    adjustment_factor *= 0.9
                
                # Calcular nueva duración
                new_duration = int(current_duration * adjustment_factor)
                new_duration = max(self.min_phase_duration, min(self.max_phase_duration, new_duration))
                
                new_phase = phase.copy()
                new_phase["duration"] = new_duration
                new_phases.append(new_phase)
            
            # Actualizar semáforo
            light.phases = new_phases
            light.last_optimization = current_time
            
            # Calcular tiempo total del ciclo
            total_cycle_time = sum(p["duration"] + p.get("yellow", 0) for p in new_phases)
            
            optimization_result = {
                "light_id": light.light_id,
                "optimization_time": current_time.isoformat(),
                "traffic_conditions": {
                    "total_vehicles": total_vehicles,
                    "average_speed": round(average_speed, 1),
                    "congestion_level": "high" if total_vehicles > 80 else "low" if total_vehicles < 20 else "normal"
                },
                "phase_adjustments": [
                    {
                        "phase": i,
                        "old_duration": light.phases[i]["duration"] if i < len(light.phases) else 0,
                        "new_duration": phase["duration"],
                        "change_seconds": phase["duration"] - (light.phases[i]["duration"] if i < len(light.phases) else 0)
                    }
                    for i, phase in enumerate(new_phases)
                ],
                "total_cycle_time": total_cycle_time,
                "estimated_throughput_improvement": self._estimate_throughput_improvement(total_vehicles, new_phases)
            }
            
            logger.info(f"🚦 Semáforo {light.light_id} optimizado - Ciclo: {total_cycle_time}s")
            
            return optimization_result
            
        except Exception as e:
            logger.error(f"❌ Error optimizando semáforo: {e}")
            return {"error": str(e)}
    
    def _estimate_throughput_improvement(self, vehicle_count: int, phases: List[Dict]) -> float:
        """Estimar mejora en throughput de vehículos"""
        
        if vehicle_count < 20:
            return 0.05  # 5% mejora en tráfico bajo
        elif vehicle_count < 50:
            return 0.12  # 12% mejora en tráfico medio
        elif vehicle_count < 80:
            return 0.18  # 18% mejora en tráfico alto
        else:
            return 0.25  # 25% mejora en tráfico muy alto

class IncidentDetectionSystem:
    """
    Sistema de detección automática de incidentes de tráfico
    Usa anomalías en patrones de flujo para detectar problemas
    """
    
    def __init__(self):
        self.incident_threshold = 0.7  # Umbral de anomalía
        self.active_incidents = {}
    
    def detect_traffic_incident(self, current_reading: TrafficReading, historical_avg: Dict) -> Optional[TrafficIncident]:
        """Detectar incidentes basado en anomalías de tráfico"""
        
        try:
            current_time = current_reading.timestamp
            sensor_id = current_reading.sensor_id
            
            # Obtener valores históricos esperados para esta hora
            expected_speed = historical_avg.get("speed", 40)
            expected_vehicles = historical_avg.get("vehicles", 30)
            expected_occupancy = historical_avg.get("occupancy", 40)
            
            # Calcular desviaciones
            speed_deviation = (expected_speed - current_reading.average_speed) / expected_speed
            vehicle_deviation = (current_reading.vehicle_count - expected_vehicles) / expected_vehicles
            occupancy_deviation = (current_reading.occupancy_rate - expected_occupancy) / expected_occupancy
            
            # Detectar tipos de incidentes
            incident_detected = None
            
            # Accidente - velocidad muy baja, alta ocupación
            if (speed_deviation > 0.6 and  # 60% menos velocidad
                occupancy_deviation > 0.5 and  # 50% más ocupación
                current_reading.queue_length > 100):  # Cola > 100m
                
                incident_detected = TrafficIncident(
                    incident_id=f"ACC_{sensor_id}_{int(current_time.timestamp())}",
                    location=(0, 0),  # TODO: Obtener de sensor
                    incident_type="accident",
                    severity="high" if speed_deviation > 0.8 else "medium",
                    description=f"Posible accidente detectado por velocidad baja ({current_reading.average_speed:.1f} km/h) y alta congestión",
                    affected_routes=[sensor_id],
                    estimated_duration=45 if speed_deviation > 0.8 else 25,
                    alternative_routes=[],  # TODO: Calcular rutas alternativas
                    detection_time=current_time
                )
            
            # Congestión inusual - muchos vehículos, velocidad baja
            elif (vehicle_deviation > 0.8 and  # 80% más vehículos
                  speed_deviation > 0.4):  # 40% menos velocidad
                
                incident_detected = TrafficIncident(
                    incident_id=f"CON_{sensor_id}_{int(current_time.timestamp())}",
                    location=(0, 0),
                    incident_type="construction",  # Podría ser construcción u evento
                    severity="medium",
                    description=f"Congestión inusual detectada - {current_reading.vehicle_count} vehículos/min (normal: {expected_vehicles})",
                    affected_routes=[sensor_id],
                    estimated_duration=30,
                    alternative_routes=[],
                    detection_time=current_time
                )
            
            # Flujo anormalmente bajo - posible cierre de vía
            elif (vehicle_deviation < -0.7 and  # 70% menos vehículos
                  current_reading.vehicle_count < 5):  # Muy pocos vehículos
                
                incident_detected = TrafficIncident(
                    incident_id=f"CLO_{sensor_id}_{int(current_time.timestamp())}",
                    location=(0, 0),
                    incident_type="event",  # Posible cierre o evento
                    severity="high",
                    description=f"Flujo vehicular anormalmente bajo - posible cierre de vía",
                    affected_routes=[sensor_id],
                    estimated_duration=60,
                    alternative_routes=[],
                    detection_time=current_time
                )
            
            if incident_detected:
                self.active_incidents[incident_detected.incident_id] = incident_detected
                logger.warning(f"🚨 INCIDENTE DETECTADO: {incident_detected.incident_id} - {incident_detected.incident_type}")
            
            return incident_detected
            
        except Exception as e:
            logger.error(f"❌ Error detectando incidente: {e}")
            return None

class SmartTransportationCore:
    """
    Núcleo principal del sistema de transporte inteligente
    Integra sensores, predicción, optimización y detección de incidentes
    """
    
    def __init__(self):
        self.traffic_network = SanJoseTrafficNetwork()
        self.flow_predictor = TrafficFlowPredictor()
        self.light_controller = SmartTrafficLightController()
        self.incident_detector = IncidentDetectionSystem()
        self.is_monitoring = False
        self.current_readings = {}
        self.active_incidents = {}
    
    async def start_monitoring(self) -> None:
        """Iniciar monitoreo continuo del tráfico"""
        
        logger.info("🚗 Iniciando monitoreo de tráfico inteligente...")
        self.is_monitoring = True
        
        # Monitoreo continuo
        while self.is_monitoring:
            try:
                # Monitorear sensores de tráfico
                await self._monitor_all_sensors()
                
                # Optimizar semáforos cada 5 minutos
                if datetime.now().minute % 5 == 0:
                    await self._optimize_all_traffic_lights()
                
                await asyncio.sleep(60)  # Cada minuto
                
            except Exception as e:
                logger.error(f"❌ Error en monitoreo de tráfico: {e}")
                await asyncio.sleep(30)
    
    async def _monitor_all_sensors(self) -> None:
        """Monitorear todos los sensores de tráfico"""
        
        for sensor_id in self.traffic_network.traffic_sensors.keys():
            try:
                # Generar lectura simulada
                reading = self.traffic_network.simulate_traffic_reading(sensor_id)
                self.current_readings[sensor_id] = reading
                
                # Detectar incidentes
                # TODO: Usar datos históricos reales
                historical_avg = {"speed": 40, "vehicles": 30, "occupancy": 40}
                incident = self.incident_detector.detect_traffic_incident(reading, historical_avg)
                
                if incident:
                    self.active_incidents[incident.incident_id] = incident
                    await self._process_traffic_incident(incident)
                
                # Log condiciones críticas
                if reading.average_speed < 15 or reading.occupancy_rate > 85:
                    logger.warning(
                        f"⚠️ {sensor_id}: Velocidad={reading.average_speed:.1f}km/h, "
                        f"Ocupación={reading.occupancy_rate:.1f}%, "
                        f"Cola={reading.queue_length}m"
                    )
                
            except Exception as e:
                logger.error(f"❌ Error monitoreando sensor de tráfico {sensor_id}: {e}")
    
    async def _optimize_all_traffic_lights(self) -> None:
        """Optimizar todos los semáforos inteligentes"""
        
        for light_id, light in self.traffic_network.smart_lights.items():
            try:
                # Preparar datos de tráfico para este semáforo
                traffic_data = {}
                for sensor_id in light.sensors_linked:
                    if sensor_id in self.current_readings:
                        reading = self.current_readings[sensor_id]
                        traffic_data[sensor_id] = {
                            "vehicle_count": reading.vehicle_count,
                            "average_speed": reading.average_speed,
                            "occupancy_rate": reading.occupancy_rate
                        }
                
                # Optimizar semáforo
                if traffic_data:
                    result = self.light_controller.optimize_traffic_light(light, traffic_data)
                    
                    if "estimated_throughput_improvement" in result:
                        improvement = result["estimated_throughput_improvement"]
                        if improvement > 0.1:  # Mejora significativa
                            logger.info(f"🚦 Semáforo {light_id} optimizado - Mejora estimada: {improvement*100:.1f}%")
                
            except Exception as e:
                logger.error(f"❌ Error optimizando semáforo {light_id}: {e}")
    
    async def _process_traffic_incident(self, incident: TrafficIncident) -> None:
        """Procesar incidente de tráfico detectado"""
        
        try:
            logger.warning(f"🚨 INCIDENTE DE TRÁFICO: {incident.incident_id}")
            logger.warning(f"   📍 Sensor: {incident.affected_routes[0]}")
            logger.warning(f"   🚧 Tipo: {incident.incident_type} ({incident.severity})")
            logger.warning(f"   📄 {incident.description}")
            logger.warning(f"   ⏱️ Duración estimada: {incident.estimated_duration} min")
            
            # TODO: Acciones automáticas
            # - Ajustar semáforos cercanos para desviar tráfico
            # - Notificar a Waze/Google Maps
            # - Alertar a policía de tránsito
            # - Actualizar paneles de mensaje variable
            # - Sugerir rutas alternativas
            
        except Exception as e:
            logger.error(f"❌ Error procesando incidente: {e}")
    
    async def get_system_status(self) -> Dict:
        """Obtener estado del sistema de transporte inteligente"""
        
        try:
            total_sensors = len(self.traffic_network.traffic_sensors)
            total_lights = len(self.traffic_network.smart_lights)
            active_incidents = len(self.active_incidents)
            
            # Estadísticas de tráfico actual
            if self.current_readings:
                avg_speed = np.mean([r.average_speed for r in self.current_readings.values()])
                total_vehicles = sum([r.vehicle_count for r in self.current_readings.values()])
                avg_occupancy = np.mean([r.occupancy_rate for r in self.current_readings.values()])
            else:
                avg_speed = 0
                total_vehicles = 0
                avg_occupancy = 0
            
            # Clasificar congestión
            if avg_occupancy > 70:
                congestion_level = "high"
            elif avg_occupancy > 40:
                congestion_level = "medium"
            else:
                congestion_level = "low"
            
            # Estadísticas por tipo de incidente
            incident_stats = {"accident": 0, "construction": 0, "event": 0, "weather": 0}
            for incident in self.active_incidents.values():
                incident_stats[incident.incident_type] = incident_stats.get(incident.incident_type, 0) + 1
            
            return {
                "system_status": "monitoring" if self.is_monitoring else "stopped",
                "traffic_infrastructure": {
                    "total_sensors": total_sensors,
                    "smart_traffic_lights": total_lights,
                    "ai_optimized_lights": sum(1 for light in self.traffic_network.smart_lights.values() if light.ai_controlled)
                },
                "current_traffic_conditions": {
                    "average_speed_kmh": round(avg_speed, 1),
                    "total_vehicles_per_minute": total_vehicles,
                    "average_occupancy_rate": round(avg_occupancy, 1),
                    "congestion_level": congestion_level
                },
                "active_incidents": active_incidents,
                "incident_breakdown": incident_stats,
                "coverage_area": {
                    "main_highways": ["Autopista General Cañas", "Circunvalación", "Radial Cartago"],
                    "urban_roads": ["Paseo Colón", "Avenida Central"],
                    "municipalities": ["San José", "Alajuela", "Cartago", "Heredia"]
                },
                "energy_correlation": {
                    "electric_vehicles_detected": total_vehicles * 0.03,  # 3% estimado
                    "traffic_light_energy_saved": total_lights * 0.15,  # 15% ahorro por optimización IA
                    "transportation_co2_impact": total_vehicles * 0.21  # kg CO2 por vehículo/hora
                },
                "last_update": datetime.now().isoformat()
            }
            
        except Exception as e:
            logger.error(f"❌ Error obteniendo estado del sistema: {e}")
            return {"error": str(e)}
