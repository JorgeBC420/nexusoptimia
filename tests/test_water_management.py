"""
Tests unitarios para sistema de gestión de agua
Pruebas automatizadas para detección de fugas y respuesta de emergencia
"""

import unittest
import asyncio
from unittest.mock import Mock, patch, AsyncMock
from datetime import datetime, timedelta
import numpy as np

import sys
sys.path.append('../')

from src.water_management import (
    WaterSensor, LeakAlert, WaterNetworkSimulator, 
    LeakDetectionAI, EmergencyResponseSystem, WaterManagementCore
)

class TestWaterNetworkSimulator(unittest.TestCase):
    """Tests para simulador de red hídrica"""
    
    def setUp(self):
        """Configurar datos de prueba"""
        self.simulator = WaterNetworkSimulator()
    
    def test_costa_rica_network_setup(self):
        """Verificar configuración de red de Costa Rica"""
        
        # Verificar que se crearon sensores
        self.assertGreater(len(self.simulator.sensors), 0)
        
        # Verificar sensores principales
        sensor_ids = list(self.simulator.sensors.keys())
        
        # Debe incluir fuentes principales
        self.assertIn("orosi_intake", sensor_ids)
        self.assertIn("tres_rios_plant", sensor_ids)
        
        # Debe incluir tanques de almacenamiento
        self.assertIn("curridabat_tank", sensor_ids)
        
        # Debe incluir centros urbanos
        self.assertIn("san_jose_centro", sensor_ids)
        
        # Debe incluir ASADAS rurales
        self.assertIn("monteverde_asada", sensor_ids)
    
    def test_sensor_properties(self):
        """Verificar propiedades de sensores"""
        
        for sensor_id, sensor in self.simulator.sensors.items():
            # Verificar tipos de datos
            self.assertIsInstance(sensor.sensor_id, str)
            self.assertIn(sensor.sensor_type, ["pressure", "flow"])
            self.assertIsInstance(sensor.location, tuple)
            self.assertEqual(len(sensor.location), 2)
            self.assertIn(sensor.water_source, ["aya", "municipal", "asada"])
            
            # Verificar rangos de valores
            self.assertGreater(sensor.pipe_diameter, 0)
            self.assertGreaterEqual(sensor.normal_pressure, 0)
            self.assertGreaterEqual(sensor.normal_flow, 0)
    
    def test_leak_simulation(self):
        """Probar simulación de fugas"""
        
        sensor_id = "san_jose_centro"
        
        # Probar diferentes severidades
        for severity in ["minor", "moderate", "major", "critical"]:
            with self.subTest(severity=severity):
                leak_data = self.simulator.simulate_leak_scenario(sensor_id, severity)
                
                # Verificar estructura de datos
                self.assertIn("sensor_id", leak_data)
                self.assertIn("leak_indicators", leak_data)
                self.assertIn("estimated_loss_lpm", leak_data["leak_indicators"])
                
                # Verificar severidad
                self.assertEqual(leak_data["leak_indicators"]["severity"], severity)
                
                # Verificar que hay cambio en el valor
                normal_value = leak_data["normal_value"]
                current_value = leak_data["current_value"]
                self.assertNotEqual(normal_value, current_value)
    
    def test_invalid_sensor_simulation(self):
        """Probar simulación con sensor inexistente"""
        
        with self.assertRaises(ValueError):
            self.simulator.simulate_leak_scenario("sensor_inexistente", "moderate")

class TestLeakDetectionAI(unittest.TestCase):
    """Tests para sistema de detección de fugas con IA"""
    
    def setUp(self):
        """Configurar detector de fugas"""
        self.detector = LeakDetectionAI()
    
    def test_pressure_leak_detection(self):
        """Probar detección por caída de presión"""
        
        # Sensor con caída crítica de presión
        sensor_data = {
            "sensor_id": "test_sensor",
            "sensor_type": "pressure",
            "current_value": 1.0,  # 1 bar actual
            "normal_value": 4.5,   # 4.5 bar normal (caída de 3.5 bar)
            "pipe_diameter": 0.6
        }
        
        analysis = self.detector.analyze_sensor_data(sensor_data)
        
        # Verificar detección
        self.assertEqual(analysis["severity"], "critical")
        self.assertGreater(analysis["leak_probability"], 0.9)
        self.assertTrue(analysis["requires_action"])
        self.assertIn("Caída crítica de presión", analysis["indicators"])
    
    def test_flow_leak_detection(self):
        """Probar detección por aumento de flujo"""
        
        # Sensor con aumento significativo de flujo
        sensor_data = {
            "sensor_id": "test_sensor",
            "sensor_type": "flow",
            "current_value": 175.0,  # 175 L/s actual
            "normal_value": 50.0,    # 50 L/s normal (aumento de 125 L/s)
            "pipe_diameter": 1.2
        }
        
        analysis = self.detector.analyze_sensor_data(sensor_data)
        
        # Verificar detección
        self.assertEqual(analysis["severity"], "critical")
        self.assertGreater(analysis["leak_probability"], 0.9)
        self.assertTrue(analysis["requires_action"])
        self.assertIn("Aumento crítico de flujo", analysis["indicators"])
    
    def test_normal_readings(self):
        """Probar lecturas normales sin fugas"""
        
        sensor_data = {
            "sensor_id": "test_sensor",
            "sensor_type": "pressure",
            "current_value": 2.5,
            "normal_value": 2.5,  # Sin cambio
            "pipe_diameter": 0.8
        }
        
        analysis = self.detector.analyze_sensor_data(sensor_data)
        
        # Verificar normalidad
        self.assertEqual(analysis["severity"], "normal")
        self.assertLess(analysis["leak_probability"], 0.1)
        self.assertFalse(analysis["requires_action"])
    
    def test_trend_analysis(self):
        """Probar análisis de tendencias"""
        
        sensor_data = {
            "sensor_id": "test_sensor",
            "sensor_type": "pressure",
            "current_value": 2.0,
            "normal_value": 2.5,
            "pipe_diameter": 0.6
        }
        
        # Datos históricos con tendencia descendente
        historical_data = [
            {"current_value": 2.4},
            {"current_value": 2.2},
            {"current_value": 2.0}
        ]
        
        analysis = self.detector.analyze_sensor_data(sensor_data, historical_data)
        
        # Verificar que detecta tendencia
        self.assertIn("Tendencia descendente sostenida", analysis["indicators"])
        
        # Debe aumentar probabilidad de fuga
        analysis_without_trend = self.detector.analyze_sensor_data(sensor_data)
        self.assertGreater(analysis["leak_probability"], analysis_without_trend["leak_probability"])
    
    def test_water_loss_estimation(self):
        """Probar estimación de pérdida de agua"""
        
        sensor_data = {
            "sensor_id": "test_sensor",
            "sensor_type": "pressure",
            "current_value": 1.0,
            "normal_value": 3.0,
            "pipe_diameter": 1.0  # 1 metro de diámetro
        }
        
        analysis = self.detector.analyze_sensor_data(sensor_data)
        
        # Verificar que estima pérdida
        self.assertGreater(analysis["estimated_loss_lpm"], 0)
        self.assertIsInstance(analysis["estimated_loss_lpm"], float)

class TestEmergencyResponseSystem(unittest.TestCase):
    """Tests para sistema de respuesta de emergencia"""
    
    def setUp(self):
        """Configurar sistema de emergencia"""
        self.emergency_system = EmergencyResponseSystem()
    
    def test_response_teams_setup(self):
        """Verificar configuración de equipos de respuesta"""
        
        # Verificar que se configuraron equipos
        self.assertGreater(len(self.emergency_system.response_teams), 0)
        
        # Verificar equipos principales
        expected_teams = ["san_jose", "cartago", "alajuela", "guanacaste", "limon"]
        for team_id in expected_teams:
            self.assertIn(team_id, self.emergency_system.response_teams)
            
            team = self.emergency_system.response_teams[team_id]
            
            # Verificar propiedades requeridas
            self.assertIn("team_name", team)
            self.assertIn("contact_phone", team)
            self.assertIn("contact_email", team)
            self.assertIn("coverage_area", team)
            self.assertIn("response_time_target", team)
    
    def test_nearest_team_calculation(self):
        """Probar cálculo de equipo más cercano"""
        
        # Ubicación en San José centro
        san_jose_location = (9.9333, -84.0833)
        
        nearest_team = self.emergency_system._find_nearest_response_team(san_jose_location)
        
        # Debe ser el equipo de San José
        self.assertEqual(nearest_team["team_name"], "Equipo GAM Norte")
        self.assertIn("distance_km", nearest_team)
        self.assertIn("estimated_arrival", nearest_team)
        self.assertLess(nearest_team["distance_km"], 5)  # Muy cerca del centro
    
    def test_isolation_valves_search(self):
        """Probar búsqueda de válvulas de aislamiento"""
        
        location = (9.9333, -84.0833)  # San José
        valves = self.emergency_system._find_isolation_valves(location, radius_km=3.0)
        
        # Debe encontrar válvulas simuladas
        self.assertIsInstance(valves, list)
        
        # Con radio de 3km debe encontrar varias válvulas
        valves_wide = self.emergency_system._find_isolation_valves(location, radius_km=10.0)
        self.assertGreaterEqual(len(valves_wide), len(valves))
    
    def test_emergency_message_generation(self):
        """Probar generación de mensajes de emergencia"""
        
        # Crear alerta de prueba
        leak_alert = LeakAlert(
            alert_id="TEST_001",
            sensor_id="test_sensor",
            location=(9.9333, -84.0833),
            severity="major",
            estimated_loss=150.0,
            confidence=0.85,
            detection_time=datetime.now(),
            description="Fuga de prueba",
            recommended_actions=["Acción 1", "Acción 2"]
        )
        
        # Equipo de respuesta
        response_team = {
            "team_name": "Equipo Prueba",
            "distance_km": 2.5,
            "estimated_arrival": 60
        }
        
        message = self.emergency_system._generate_emergency_message(leak_alert, response_team)
        
        # Verificar contenido del mensaje
        self.assertIn("ALERTA DE FUGA", message)
        self.assertIn("TEST_001", message)
        self.assertIn("MAJOR", message.upper())
        self.assertIn("150", message)  # Pérdida estimada
        self.assertIn("85%", message)  # Confianza
        self.assertIn("Equipo Prueba", message)
        self.assertIn("2.5 km", message)
        self.assertIn("maps.google.com", message)  # Link de Google Maps
    
    @patch('asyncio.sleep')
    async def test_notification_sending(self, mock_sleep):
        """Probar envío de notificaciones"""
        
        mock_sleep.return_value = None
        
        # Crear alerta de prueba
        leak_alert = LeakAlert(
            alert_id="TEST_002",
            sensor_id="test_sensor",
            location=(9.9333, -84.0833),
            severity="critical",
            estimated_loss=300.0,
            confidence=0.95,
            detection_time=datetime.now(),
            description="Fuga crítica de prueba",
            recommended_actions=["Respuesta inmediata"]
        )
        
        response_team = {
            "team_name": "Equipo GAM Norte",
            "contact_phone": "+506-8888-1001",
            "contact_email": "test@example.com",
            "distance_km": 1.0,
            "estimated_arrival": 45
        }
        
        # Probar envío de notificaciones
        result = await self.emergency_system._send_emergency_notifications(leak_alert, response_team)
        
        # Verificar resultado
        self.assertIn("success_count", result)
        self.assertIn("channels_used", result)
        self.assertGreater(result["success_count"], 0)

class TestWaterManagementCore(unittest.TestCase):
    """Tests para núcleo principal del sistema"""
    
    def setUp(self):
        """Configurar sistema principal"""
        self.water_system = WaterManagementCore()
    
    def test_system_initialization(self):
        """Probar inicialización del sistema"""
        
        # Verificar componentes inicializados
        self.assertIsNotNone(self.water_system.simulator)
        self.assertIsNotNone(self.water_system.leak_detector)
        self.assertIsNotNone(self.water_system.emergency_system)
        
        # Verificar estado inicial
        self.assertFalse(self.water_system.is_monitoring)
        self.assertEqual(len(self.water_system.active_alerts), 0)
    
    @patch('asyncio.sleep')
    async def test_monitoring_lifecycle(self, mock_sleep):
        """Probar ciclo de vida del monitoreo"""
        
        mock_sleep.return_value = None
        
        # Verificar estado inicial
        self.assertFalse(self.water_system.is_monitoring)
        
        # Crear task de monitoreo que se detenga rápidamente
        async def quick_monitoring():
            self.water_system.is_monitoring = True
            await self.water_system._monitor_all_sensors()
            self.water_system.is_monitoring = False
        
        # Ejecutar monitoreo rápido
        await quick_monitoring()
        
        # Verificar que procesó sensores
        self.assertFalse(self.water_system.is_monitoring)
    
    def test_sensor_reading_simulation(self):
        """Probar simulación de lecturas de sensores"""
        
        sensor_id = "san_jose_centro"
        sensor = self.water_system.simulator.sensors[sensor_id]
        
        # Generar múltiples lecturas
        readings = []
        for _ in range(10):
            reading = self.water_system._simulate_sensor_reading(sensor)
            readings.append(reading)
        
        # Verificar estructura de lecturas
        for reading in readings:
            self.assertIn("sensor_id", reading)
            self.assertIn("sensor_type", reading)
            self.assertIn("current_value", reading)
            self.assertIn("normal_value", reading)
            self.assertIn("timestamp", reading)
            
            # Valores deben ser numéricos
            self.assertIsInstance(reading["current_value"], (int, float))
            self.assertIsInstance(reading["normal_value"], (int, float))
    
    async def test_system_status(self):
        """Probar obtención de estado del sistema"""
        
        status = await self.water_system.get_system_status()
        
        # Verificar estructura del estado
        expected_keys = [
            "system_status", "total_sensors", "sensor_breakdown",
            "active_alerts", "severity_breakdown", "coverage_area"
        ]
        
        for key in expected_keys:
            self.assertIn(key, status)
        
        # Verificar tipos de datos
        self.assertIsInstance(status["total_sensors"], int)
        self.assertIsInstance(status["active_alerts"], int)
        self.assertIsInstance(status["sensor_breakdown"], dict)
        self.assertIsInstance(status["coverage_area"], dict)
    
    def test_recommendation_generation(self):
        """Probar generación de recomendaciones"""
        
        # Probar cada nivel de severidad
        severities = ["minor", "moderate", "major", "critical"]
        
        for severity in severities:
            with self.subTest(severity=severity):
                recommendations = self.water_system._generate_recommendations(severity)
                
                # Debe devolver lista de strings
                self.assertIsInstance(recommendations, list)
                self.assertGreater(len(recommendations), 0)
                
                for rec in recommendations:
                    self.assertIsInstance(rec, str)
                    self.assertGreater(len(rec), 10)  # Recomendaciones descriptivas

class TestIntegration(unittest.TestCase):
    """Tests de integración end-to-end"""
    
    def setUp(self):
        """Configurar sistema completo"""
        self.water_system = WaterManagementCore()
    
    async def test_complete_leak_scenario(self):
        """Probar escenario completo de detección y respuesta"""
        
        sensor_id = "curridabat_tank"
        
        # 1. Simular fuga mayor
        leak_data = self.water_system.simulator.simulate_leak_scenario(sensor_id, "major")
        
        # 2. Analizar con IA
        analysis = self.water_system.leak_detector.analyze_sensor_data(leak_data)
        
        # 3. Verificar detección
        self.assertEqual(analysis["severity"], "major")
        self.assertTrue(analysis["requires_action"])
        
        # 4. Procesar detección (crear alerta)
        sensor = self.water_system.simulator.sensors[sensor_id]
        await self.water_system._process_leak_detection(sensor, analysis)
        
        # 5. Verificar alerta creada
        self.assertGreater(len(self.water_system.active_alerts), 0)
        
        # 6. Obtener estado del sistema
        status = await self.water_system.get_system_status()
        
        # 7. Verificar que refleja la alerta
        self.assertGreater(status["active_alerts"], 0)
        self.assertGreater(status["total_estimated_loss_lpm"], 0)

# Utilidad para ejecutar tests asyncronos
def run_async_test(test_func):
    """Helper para ejecutar tests asíncronos"""
    loop = asyncio.get_event_loop()
    return loop.run_until_complete(test_func())

if __name__ == '__main__':
    # Configurar logging para tests
    import logging
    logging.basicConfig(level=logging.INFO)
    
    # Ejecutar tests
    unittest.main(verbosity=2)
