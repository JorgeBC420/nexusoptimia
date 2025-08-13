"""
Orquestador central de NeXOptimIA
Gestiona m�dulos como plugins/microservicios
"""
from typing import Dict, Any, List, Optional, Type
import importlib
import logging
import json
import time
from src.modules.electrical_monitor.module import ElectricalMonitorModule
from src.core.hardware_simulator import HardwareSimulator

class SystemInformation:
    """
    Informaci�n estrat�gica del ecosistema
    """
    households_target: int = 1650000
    patent_protected_ip: bool = True
    market_opportunity_usd: int = 800_000_000

    def as_dict(self) -> Dict[str, Any]:
        return {
            "households_target": self.households_target,
            "patent_protected_ip": self.patent_protected_ip,
            "market_opportunity_usd": self.market_opportunity_usd
        }

class NeXOptimIA_Orchestrator:
    """
    Orquestador central: carga, inicia, detiene y monitorea m�dulos
    """
    def __init__(self):
        self.modules: Dict[str, Any] = {}
        self.system_info = SystemInformation()
        self.logger = logging.getLogger("nexoptimia.orchestrator")

    def load_module(self, name: str, module_path: str, class_name: str) -> None:
        """
        Carga un m�dulo din�micamente como plugin
        """
        try:
            mod = importlib.import_module(module_path)
            module_class = getattr(mod, class_name)
            instance = module_class()
            self.modules[name] = instance
            self.logger.info(f"M�dulo '{name}' cargado desde {module_path}.{class_name}")
        except Exception as e:
            self.logger.error(f"Error cargando m�dulo {name}: {e}")

    def start_module(self, name: str) -> None:
        """
        Inicia un m�dulo si tiene m�todo start()
        """
        module = self.modules.get(name)
        if module and hasattr(module, "start"):
            module.start()
            self.logger.info(f"M�dulo '{name}' iniciado")

    def stop_module(self, name: str) -> None:
        """
        Detiene un m�dulo si tiene m�todo stop()
        """
        module = self.modules.get(name)
        if module and hasattr(module, "stop"):
            module.stop()
            self.logger.info(f"M�dulo '{name}' detenido")

    def get_status(self) -> Dict[str, Any]:
        """
        Devuelve el estado de todos los m�dulos y la informaci�n estrat�gica
        """
        status = {name: getattr(mod, "get_status", lambda: "unknown")() for name, mod in self.modules.items()}
        return {
            "system_info": self.system_info.as_dict(),
            "modules": status
        }

    def monitor_modules(self) -> List[str]:
        """
        Monitorea y retorna el estado de los m�dulos activos
        """
        return [name for name, mod in self.modules.items() if getattr(mod, "get_status", lambda: None)() == "active"]

    def start_hardware_simulation(self, scenario: str = 'normal'):
        """
        Inicia simulaci�n de hardware en el m�dulo de monitoreo el�ctrico
        """
        mod = self.modules.get('electrical_monitor')
        if mod and isinstance(mod, ElectricalMonitorModule):
            mod.set_data_source('simulator')
            mod.set_simulation_scenario(scenario)
            mod.start()
            self.logger.info(f"Simulaci�n de hardware iniciada en escenario: {scenario}")
        else:
            self.logger.error("No se encontr� el m�dulo 'electrical_monitor' para simular hardware.")

    def stop_hardware_simulation(self):
        """
        Detiene la simulaci�n de hardware y restaura la fuente de datos a CENCE
        """
        mod = self.modules.get('electrical_monitor')
        if mod and isinstance(mod, ElectricalMonitorModule):
            mod.set_data_source('cence')
            mod.stop()
            self.logger.info("Simulaci�n de hardware detenida, vuelve a datos reales/simulados CENCE.")
        else:
            self.logger.error("No se encontr� el m�dulo 'electrical_monitor' para detener la simulaci�n.")

class OrchestratorAI:
    """
    Orquestador ACE-IA: gestiona agentes, misiones y reportes
    """
    def __init__(self):
        self.agents = {}  # Estado de agentes

    def assign_mission_to_agent(self, agent_id, mission_profile):
        # Simula env�o de perfil de misi�n (en real: BLE/LoRa/GibberLink)
        send_config_via_gibberlink(agent_id, mission_profile)
        self.agents[agent_id] = {"mission_id": mission_profile['mission_id'], "last_status": "ASSIGNED"}

    def handle_incoming_report(self, report_packet):
        agent_id = report_packet['agent_id']
        level = report_packet['report_level']
        trigger = report_packet['trigger_fired']
        value = report_packet['measured_value']
        print(f"Orquestador: Reporte recibido de {agent_id}: Nivel {level}, Trigger {trigger}, Valor {value}")
        mission_function = report_packet.get('mission_function', None)
        if mission_function == "voltage_stability_monitoring":
            if level == "CRITICAL":
                initiate_load_balancing_protocol()
                notify_human_admins("Alerta de sobrevoltaje cr�tico")
            elif level == "WARNING":
                increase_monitoring_frequency_for_zone(agent_id)
        self.agents[agent_id]['last_status'] = f"REPORTED_{level}"
        self.agents[agent_id]['last_report_time'] = get_current_timestamp()

# Simulaciones de funciones de comunicaci�n y l�gica de negocio

def send_config_via_gibberlink(agent_id, mission_profile):
    print(f"[GibberLink-RF] Enviando perfil de misi�n a {agent_id}: {json.dumps(mission_profile)}")

def initiate_load_balancing_protocol():
    print("[AI] Protocolo de balanceo de carga iniciado.")

def notify_human_admins(msg):
    print(f"[ALERTA HUMANA] {msg}")

def increase_monitoring_frequency_for_zone(agent_id):
    print(f"[AI] Aumentando frecuencia de monitoreo para zona de {agent_id}.")

def get_current_timestamp():
    return int(time.time())
