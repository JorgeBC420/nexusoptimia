import random
import time
from src.core.types import ElectricalSensorData
from src.core.utils import clamp

class HardwareSimulator:
    """
    Simulador de hardware eléctrico para pruebas y demos.
    """
    def __init__(self, scenario: str = "normal"):
        self.set_scenario(scenario)

    def set_scenario(self, scenario: str):
        self.scenario = scenario
        self.config = self.get_scenario_config(scenario)

    def get_scenario_config(self, scenario: str):
        configs = {
            "normal": {"voltage_base": 230.0, "voltage_variation": 2.0, "current_base": 10.0, "current_variation": 1.0, "frequency_base": 50.0, "frequency_variation": 0.05, "thd_base": 2.0, "alert_probability": 0.02},
            "high_load": {"voltage_base": 225.0, "voltage_variation": 5.0, "current_base": 15.0, "current_variation": 3.0, "frequency_base": 49.95, "frequency_variation": 0.1, "thd_base": 4.0, "alert_probability": 0.1},
            "power_quality": {"voltage_base": 235.0, "voltage_variation": 8.0, "current_base": 12.0, "current_variation": 4.0, "frequency_base": 50.0, "frequency_variation": 0.15, "thd_base": 6.0, "alert_probability": 0.2},
            "grid_instability": {"voltage_base": 228.0, "voltage_variation": 12.0, "current_base": 11.0, "current_variation": 5.0, "frequency_base": 49.9, "frequency_variation": 0.3, "thd_base": 5.0, "alert_probability": 0.25},
            "costa_rica": {"voltage_base": 230.0, "voltage_variation": 3.0, "current_base": 12.0, "current_variation": 2.0, "frequency_base": 50.0, "frequency_variation": 0.08, "thd_base": 3.5, "alert_probability": 0.08}
        }
        return configs.get(scenario, configs["normal"])

    def generate_new_reading(self):
        c = self.config
        voltage = clamp(random.gauss(c["voltage_base"], c["voltage_variation"]), 180, 260)
        current = clamp(random.gauss(c["current_base"], c["current_variation"]), 0.5, 25)
        power = voltage * current * random.uniform(0.93, 0.98)
        thd_v = max(0.5, abs(random.gauss(c["thd_base"], 1.0)))
        thd_c = max(0.5, abs(random.gauss(c["thd_base"], 1.2)))
        frequency = random.gauss(c["frequency_base"], c["frequency_variation"])
        power_factor = clamp(random.gauss(0.95, 0.02), 0.7, 1.0)
        safety_status = 0
        if random.random() < c["alert_probability"]:
            if voltage > 245.0:
                safety_status |= 0x01
            elif voltage < 210.0:
                safety_status |= 0x02
            if current > 16.0:
                safety_status |= 0x04
            if power > 3800.0:
                safety_status |= 0x08
            if power_factor < 0.8:
                safety_status |= 0x10
            if thd_v > 6.0 or thd_c > 6.0:
                safety_status |= 0x20
            if abs(frequency - 50.0) > 0.3:
                safety_status |= 0x40
            if safety_status == 0 and random.random() < 0.3:
                safety_status = random.choice([0x10, 0x20])
        quality_grade = 0
        if thd_v > 3.0 or thd_c > 3.0:
            quality_grade += 1
        if power_factor < 0.9:
            quality_grade += 1
        quality_grade = min(quality_grade, 5)
        return ElectricalSensorData(
            sector_id=1,
            node_id=1,
            measurement_type=0x10,
            safety_status=safety_status,
            voltage_rms=voltage,
            current_rms=current,
            power_active=power,
            power_factor=power_factor,
            frequency=frequency,
            thd_voltage=thd_v,
            thd_current=thd_c,
            quality_grade=quality_grade,
            timestamp=int(time.time()),
            power_reactive=power * 0.1,
            battery_level=random.randint(80, 100),
            checksum=0x42
        )
