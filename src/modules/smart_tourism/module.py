"""
Módulo vertical: Smart Tourism
Simula datos de turismo inteligente
"""
from typing import Dict
import random

class SmartTourismModule:
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
            "tourist_count": random.randint(100, 1000),
            "popular_sites": ["Volcán Poás", "Manuel Antonio", "Monteverde"],
            "avg_stay_days": round(random.uniform(2, 7), 1),
            "timestamp": "simulated"
        }
