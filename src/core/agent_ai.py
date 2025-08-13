import time
import json

class AgentAI:
    """
    Agente ACE-IA: ejecuta misión, monitorea y reporta eventos por BLE, LoRaWAN o GibberLink-RF
    """
    def __init__(self, agent_id, comm_protocol="BLE"):
        self.agent_id = agent_id
        self.mission = None
        self.last_reported_trigger = {}
        self.previous_value = None
        self.state = "IDLE"
        self.comm_protocol = comm_protocol  # BLE, LoRaWAN, GibberLink-RF

    def load_mission(self, mission_profile):
        self.mission = mission_profile
        print(f"Agente {self.agent_id}: Misión '{self.mission['function_name']}' cargada.")
        self.state = "MONITORING"

    def run_monitoring_cycle(self):
        if self.state != "MONITORING" or not self.mission:
            return
        current_value = self.read_physical_sensor(self.mission['parameters']['value_to_monitor'])
        for trigger in self.mission['triggers']:
            if self.has_cooldown_passed(trigger['trigger_name'], trigger['cooldown_seconds']):
                condition_met = False
                if 'change_percent' in trigger['condition']:
                    if self.previous_value is not None:
                        change = abs((current_value - self.previous_value) / self.previous_value) * 100
                        if change > float(trigger['condition'].split('>')[1]):
                            condition_met = True
                else:
                    if eval(f"{current_value} {trigger['condition'].split(' ')[1]} {trigger['condition'].split(' ')[2]}"):
                        condition_met = True
                if condition_met:
                    self.report_event(trigger, current_value)
                    self.previous_value = current_value
                    return
        self.previous_value = current_value

    def report_event(self, trigger, value):
        self.state = "REPORTING"
        report_packet = {
            "timestamp": int(time.time()),
            "agent_id": self.agent_id,
            "mission_id": self.mission['mission_id'],
            "report_level": trigger['report_level'],
            "trigger_fired": trigger['trigger_name'],
            "measured_value": value,
            "mission_function": self.mission['function_name']
        }
        self.send_report(report_packet)
        self.last_reported_trigger[trigger['trigger_name']] = int(time.time())
        print(f"Agente {self.agent_id}: Evento '{trigger['trigger_name']}' reportado. Volviendo a monitoreo.")
        self.state = "MONITORING"

    def has_cooldown_passed(self, trigger_name, cooldown_seconds):
        last = self.last_reported_trigger.get(trigger_name, 0)
        return (int(time.time()) - last) > cooldown_seconds

    def read_physical_sensor(self, value_to_monitor):
        # Simulación: retorna un valor aleatorio para pruebas
        import random
        if value_to_monitor == "voltage_rms":
            return random.uniform(200, 250)
        return random.uniform(0, 100)

    def send_report(self, report_packet):
        # Simula el envío por el protocolo seleccionado
        if self.comm_protocol == "BLE":
            print(f"[BLE] Reporte enviado: {json.dumps(report_packet)}")
        elif self.comm_protocol == "LoRaWAN":
            print(f"[LoRaWAN] Reporte enviado: {json.dumps(report_packet)}")
        elif self.comm_protocol == "GibberLink-RF":
            print(f"[GibberLink-RF] Reporte enviado: {json.dumps(report_packet)}")
        else:
            print(f"[UNKNOWN] Reporte enviado: {json.dumps(report_packet)}")
