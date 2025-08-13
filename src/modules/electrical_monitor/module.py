# -*- coding: utf-8 -*-
"""
Módulo vertical: Monitoreo Eléctrico
Simula conexión a CENCE y genera datos de dashboard o usa simulador de hardware
"""
from typing import Dict, Optional, List
import random
from src.core.types import ElectricalData
from src.core.hardware_simulator import HardwareSimulator

class ElectricalMonitorModule:
    """
    Módulo de monitoreo eléctrico: procesa datos, evalúa alertas y calcula Power Quality Grade.
    """
    def __init__(self, data_source: str = 'cence'):
        self.active = False
        self.status = "stopped"
        self.data_source = data_source  # 'cence' o 'simulator'
        self.simulator: Optional[HardwareSimulator] = None
        self.last_alerts: List[Dict] = []
        self.last_quality_grade: str = "A - Excellent"
        if self.data_source == 'simulator':
            self.simulator = HardwareSimulator()

    def set_data_source(self, source: str):
        self.data_source = source
        if source == 'simulator' and self.simulator is None:
            self.simulator = HardwareSimulator()

    def set_simulation_scenario(self, scenario: str):
        if self.simulator:
            self.simulator.set_scenario(scenario)

    def start(self):
        self.active = True
        self.status = "active"

    def stop(self):
        self.active = False
        self.status = "stopped"

    def get_status(self) -> str:
        return self.status

    def get_realtime_data(self) -> Dict:
        if self.data_source == 'simulator' and self.simulator:
            reading = self.simulator.generate_new_reading()
            # Adaptar a formato esperado por UI
            return {
                "voltage_rms": reading['Voltage RMS'],
                "current_rms": reading['Current RMS'],
                "active_power": reading['Active Power'],
                "power_factor": reading['Power Factor'],
                "frequency": reading['Frequency'],
                "thd_voltage": reading['THD Voltage'],
                "thd_current": reading['THD Current'],
                "power_quality_grade": reading['Power Quality Grade'],
                "timestamp": "simulated"
            }
        # Default: datos públicos simulados (CENCE)
        return {
            "voltage_rms": round(random.uniform(110, 127), 2),
            "current_rms": round(random.uniform(8, 12), 2),
            "active_power": round(random.uniform(1800, 2500), 1),
            "power_factor": round(random.uniform(0.95, 1.0), 3),
            "frequency": round(random.uniform(59.8, 60.2), 2),
            "thd_voltage": round(random.uniform(2.5, 4.5), 1),
            "thd_current": round(random.uniform(3.5, 5.5), 1),
            "power_quality_grade": random.choice(["A - Excellent", "B - Fair", "C - Poor"]),
            "timestamp": "simulated"
        }

    def process_new_data(self, data: ElectricalData) -> Dict:
        """
        Procesa nuevos datos eléctricos, evalúa alertas y calcula Power Quality Grade.
        Devuelve un diccionario con el resultado y alertas.
        """
        alerts = []
        thresholds = {
            'voltage_min': 210.0,
            'voltage_max': 250.0,
            'current_max': 15.0,
            'frequency_min': 49.5,
            'frequency_max': 50.5,
            'thd_max': 5.0,
            'power_factor_min': 0.85
        }
        # Voltage
        if data.voltage_rms < thresholds['voltage_min']:
            alerts.append({"level": "CRITICAL", "msg": f"Low voltage: {data.voltage_rms:.1f}V"})
        elif data.voltage_rms > thresholds['voltage_max']:
            alerts.append({"level": "CRITICAL", "msg": f"High voltage: {data.voltage_rms:.1f}V"})
        # Current
        if data.current_rms > thresholds['current_max']:
            alerts.append({"level": "CRITICAL", "msg": f"High current: {data.current_rms:.1f}A"})
        # Frequency
        if data.frequency < thresholds['frequency_min'] or data.frequency > thresholds['frequency_max']:
            alerts.append({"level": "WARNING", "msg": f"Frequency deviation: {data.frequency:.2f}Hz"})
        # THD
        if data.thd_voltage > thresholds['thd_max'] or data.thd_current > thresholds['thd_max']:
            alerts.append({"level": "WARNING", "msg": f"High THD: V={data.thd_voltage:.1f}%, I={data.thd_current:.1f}%"})
        # Power factor
        if data.power_factor < thresholds['power_factor_min']:
            alerts.append({"level": "WARNING", "msg": f"Low power factor: {data.power_factor:.3f}"})

        # Safety status
        if data.safety_status != 0:
            safety_flags = []
            if data.safety_status & 0x01:
                safety_flags.append("Overvoltage")
            if data.safety_status & 0x02:
                safety_flags.append("Undervoltage")
            if data.safety_status & 0x04:
                safety_flags.append("Overcurrent")
            if data.safety_status & 0x08:
                safety_flags.append("Overpower")
            if data.safety_status & 0x10:
                safety_flags.append("Low PF")
            if data.safety_status & 0x20:
                safety_flags.append("High THD")
            if data.safety_status & 0x40:
                safety_flags.append("Freq deviation")
            if data.safety_status & 0x80:
                safety_flags.append("Phase imbalance")
            alerts.append({"level": "CRITICAL", "msg": f"Safety alerts: {', '.join(safety_flags)}"})
        # Power Quality Grade
        grade, grade_label = self.calculate_power_quality_grade(data)
        self.last_quality_grade = grade_label
        self.last_alerts = alerts
        return {
            "quality_grade": grade_label,
            "alerts": alerts
        }

    def calculate_power_quality_grade(self, data: ElectricalData):
        """
        Calcula el Power Quality Grade basado en THD y Power Factor.
        """
        grade = 0
        if data.thd_voltage > 3.0 or data.thd_current > 3.0:
            grade += 1
        if data.power_factor < 0.9:
            grade += 1
        if data.voltage_rms < 210 or data.voltage_rms > 250:
            grade += 1
        if data.safety_status != 0:
            grade = 5  # F - Unacceptable
        grade = min(grade, 5)
        grade_names = [
            "A - Excellent", "B - Good", "C - Acceptable", "D - Poor", "E - Bad", "F - DANGEROUS"
        ]
        return grade, grade_names[grade]
