"""
Módulo de comunicaciones: GibberLink-RF, LoRaWAN, BLE
"""
from typing import Any, Dict, Optional
from core.security import security_manager
from src.core.types import ElectricalSensorData, LoRaWANPacket
from src.core.utils import validate_checksum
import logging

logger = logging.getLogger(__name__)

class CommunicationsManager:
    """
    Maneja lógica de comunicaciones y traducción de paquetes
    """
    def __init__(self):
        pass

    def translate_and_forward(self, packet: bytes, destination: str = "remote") -> Dict[str, Any]:
        """
        Simula recepción BLE, encapsula para LoRaWAN, reempaqueta para UHF/VHF con seguridad
        """
        # Simular recepción BLE
        ble_packet = packet
        # Encapsular para LoRaWAN
        lorawan_packet = b"LORA:" + ble_packet
        # Si destino es remoto, aplicar seguridad
        if destination == "remote":
            gibbered = security_manager.gibber(lorawan_packet)
            encrypted = security_manager.encrypt(gibbered)
            return {"sent_packet": encrypted, "protocol": "GibberLink+AES256"}
        else:
            return {"sent_packet": lorawan_packet, "protocol": "LoRaWAN"}

    def parse_lorawan_payload(self, payload: bytes) -> Optional[ElectricalSensorData]:
        """Parsea el payload de un sensor eléctrico según el firmware."""
        try:
            if len(payload) < 23:
                logger.warning(f"Payload demasiado corto: {len(payload)} bytes")
                return None
            data = ElectricalSensorData(
                sector_id=payload[0],
                node_id=payload[1],
                measurement_type=payload[2],
                safety_status=payload[3],
                voltage_rms=(payload[4] << 8 | payload[5]) / 10.0,
                current_rms=(payload[6] << 8 | payload[7]) / 100.0,
                power_active=payload[8] << 8 | payload[9],
                power_factor=payload[10] / 100.0,
                frequency=(payload[11] / 10.0) + 45.0,
                thd_voltage=payload[12] / 10.0,
                thd_current=payload[13] / 10.0,
                quality_grade=payload[14],
                timestamp=(payload[15] << 24 | payload[16] << 16 | payload[17] << 8 | payload[18]),
                power_reactive=payload[19] << 8 | payload[20],
                battery_level=payload[21],
                checksum=payload[22]
            )
            if not validate_checksum(payload, data.checksum):
                logger.warning(f"Checksum inválido para el payload recibido")
            return data
        except Exception as e:
            logger.error(f"Error parseando payload LoRaWAN: {e}")
            return None
