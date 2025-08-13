"""
Demo Master Control Center para NeXOptimIA
Simula la integraci�n y operaci�n de todos los m�dulos
"""
from core.orchestrator import NeXOptimIA_Orchestrator, OrchestratorAI
from core.communications import CommunicationsManager
from modules.ai_services.main import AIServicesHub
from modules.electrical_monitor.module import ElectricalMonitorModule
from modules.smart_tourism.module import SmartTourismModule
from modules.home_edition.module import HomeEditionModule
from modules.water_control.module import WaterControlModule
from integrations.government import CenceClient, IMNClient, AyAClient
from core.security import security_manager
from core.agent_ai import AgentAI
import time


def main():
    print("\n=== NeXOptimIA Master Control Center ===\n")
    orchestrator = NeXOptimIA_Orchestrator()
    comms = CommunicationsManager()
    ai_hub = AIServicesHub()

    # Cargar m�dulos verticales
    orchestrator.modules["electrical"] = ElectricalMonitorModule()
    orchestrator.modules["tourism"] = SmartTourismModule()
    orchestrator.modules["home"] = HomeEditionModule()
    orchestrator.modules["water"] = WaterControlModule()
    orchestrator.modules["ai_services"] = ai_hub

    # Iniciar m�dulos principales
    orchestrator.start_module("electrical")
    orchestrator.start_module("ai_services")

    # Estado de todos los m�dulos
    status = orchestrator.get_status()
    print("System Overview:", status)

    # Simular recepci�n de paquete cifrado desde sensor
    print("\nSimulando recepci�n de paquete cifrado desde sensor BLE...")
    sensor_data = b"sensor:voltage=120.5"
    encrypted_packet = comms.translate_and_forward(sensor_data)["sent_packet"]
    print("Paquete cifrado enviado:", encrypted_packet)
    decrypted = security_manager.ungibber(security_manager.decrypt(encrypted_packet))
    print("Paquete descifrado:", decrypted)

    # Analizar con IA
    ai_result = ai_hub.analyze_request([120.5, 121.0, 119.8], model_type="anomaly")
    print("Resultado an�lisis IA:", ai_result)

    # Simulaci�n de matriz de funciones implementadas
    print("\nMatriz Completa de Funciones Implementadas:")
    for name, mod in orchestrator.modules.items():
        if hasattr(mod, "get_status"):
            print(f"- {name}: {mod.get_status()}")
        else:
            print(f"- {name}: (no status method)")

def demo_ace_ia():
    print("\n=== Demo ACE-IA: Arquitectura de Colaboraci�n Eficiente para IA ===\n")
    orchestrator = OrchestratorAI()
    # Ejemplo de perfil de misi�n
    mission_profile = {
        "mission_id": "M-ELECTRICAL-SUBSTATION-01",
        "agent_id_target": "SENSOR-UHF-GBL-007",
        "function_name": "voltage_stability_monitoring",
        "priority": 1,
        "active": True,
        "parameters": {
            "monitoring_interval_seconds": 5,
            "value_to_monitor": "voltage_rms"
        },
        "triggers": [
            {"trigger_name": "critical_overvoltage", "condition": "value > 245.0", "report_level": "CRITICAL", "cooldown_seconds": 300},
            {"trigger_name": "critical_undervoltage", "condition": "value < 210.0", "report_level": "CRITICAL", "cooldown_seconds": 300},
            {"trigger_name": "abrupt_change_warning", "condition": "change_percent > 5.0", "report_level": "WARNING", "cooldown_seconds": 60}
        ],
        "communication": {"protocol": "GibberLink-RF", "target": "NEXUSOPTIM_IA_CENTRAL"}
    }
    # Instanciar agente con cada protocolo
    agent_ble = AgentAI("SENSOR-BLE-001", comm_protocol="BLE")
    agent_lora = AgentAI("SENSOR-LORA-002", comm_protocol="LoRaWAN")
    agent_gibber = AgentAI("SENSOR-UHF-GBL-007", comm_protocol="GibberLink-RF")
    # Asignar misi�n
    orchestrator.assign_mission_to_agent(agent_gibber.agent_id, mission_profile)
    agent_gibber.load_mission(mission_profile)
    # Simular ciclos de monitoreo
    for _ in range(10):
        agent_gibber.run_monitoring_cycle()
        time.sleep(1)

if __name__ == "__main__":
    main()
    demo_ace_ia()
