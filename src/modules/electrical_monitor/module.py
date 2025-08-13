"""
Módulo vertical: Monitoreo Eléctrico
Simula conexión a CENCE y genera datos de dashboard o usa simulador de hardware
"""
from typing import Dict, Optional
import random
from src.core.hardware_simulator import HardwareSimulator

class ElectricalMonitorModule:
    """
    Módulo de monitoreo eléctrico: puede usar CENCE o simulador de hardware
    """
    def __init__(self, data_source: str = 'cence'):
        self.active = False
        self.status = "stopped"
        self.data_source = data_source  # 'cence' o 'simulator'
        self.simulator: Optional[HardwareSimulator] = None
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
