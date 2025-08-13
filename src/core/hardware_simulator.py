import random

class HardwareSimulator:
    """
    Simulador de hardware para pruebas de NeXOptimIA.
    Permite simular diferentes escenarios eléctricos realistas.
    """
    def __init__(self):
        self.set_scenario('normal')

    def set_scenario(self, scenario_name):
        self.scenario = scenario_name

    def generate_new_reading(self):
        # Valores base (modo normal)
        voltage = random.gauss(234, 1.2)
        current = random.gauss(9.5, 0.5)
        active_power = voltage * current * random.uniform(0.97, 1.01)
        power_factor = random.gauss(0.99, 0.01)
        frequency = random.gauss(49.95, 0.04)
        thd_voltage = random.gauss(3.2, 0.5)
        thd_current = random.gauss(4.7, 0.6)
        quality = 'A - Excellent'
        # Modos especiales
        if self.scenario == 'overload':
            current *= random.uniform(1.5, 2.0)
            active_power = voltage * current * random.uniform(0.97, 1.01)
        elif self.scenario == 'voltage_drop':
            voltage *= random.uniform(0.85, 0.93)
            active_power = voltage * current * random.uniform(0.97, 1.01)
        elif self.scenario == 'bad_power_quality':
            thd_voltage *= random.uniform(2.0, 3.0)
            thd_current *= random.uniform(2.0, 3.0)
            quality = 'C - Poor'
        # Calcular calidad
        if thd_voltage > 8 or thd_current > 8 or power_factor < 0.92:
            quality = 'C - Poor'
        elif thd_voltage > 5 or thd_current > 5 or power_factor < 0.96:
            quality = 'B - Fair'
        return {
            'Voltage RMS': round(voltage, 2),
            'Current RMS': round(current, 2),
            'Active Power': round(active_power, 1),
            'Power Factor': round(power_factor, 3),
            'Frequency': round(frequency, 2),
            'THD Voltage': round(thd_voltage, 1),
            'THD Current': round(thd_current, 1),
            'Power Quality Grade': quality
        }
