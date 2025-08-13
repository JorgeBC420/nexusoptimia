"""
Módulo vertical: Home Edition
Simula datos de hogar inteligente
"""
from typing import Dict
import random

class HomeEditionModule:
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
            "temperature": round(random.uniform(18, 30), 1),
            "humidity": round(random.uniform(40, 80), 1),
            "energy_usage_kw": round(random.uniform(0.5, 5.0), 2),
            "timestamp": "simulated"
        }
