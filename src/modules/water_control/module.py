"""
Módulo vertical: Water Control
Simula datos de control hídrico
"""
from typing import Dict
import random

class WaterControlModule:
    def __init__(self):
        self.active = False
        self.status = "stopped"

    def start(self):
        self.active = True
        self.status = "active"

    def stop(self):
        self.active = False
        self.status = "stopped"

    def get_status(self) -> str:
        return self.status

    def get_realtime_data(self) -> Dict:
        return {
            "flow_rate_lps": round(random.uniform(10, 100), 1),
            "pressure_bar": round(random.uniform(1.5, 4.0), 2),
            "leak_detected": random.choice([True, False]),
            "timestamp": "simulated"
        }
