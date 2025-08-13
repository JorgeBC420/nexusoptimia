from dataclasses import dataclass
from typing import Optional

@dataclass
class ElectricalData:
    timestamp: float
    voltage_rms: float
    current_rms: float
    power_active: float
    power_reactive: float
    power_apparent: float
    power_factor: float
    frequency: float
    thd_voltage: float
    thd_current: float
    safety_status: int
    quality_grade: int
    node_id: int = 1

@dataclass
class ElectricalSensorData:
    sector_id: int
    node_id: int
    measurement_type: int
    safety_status: int
    voltage_rms: float
    current_rms: float
    power_active: float
    power_factor: float
    frequency: float
    thd_voltage: float
    thd_current: float
    quality_grade: int
    timestamp: int
    power_reactive: float
    battery_level: int
    checksum: int

@dataclass
class LoRaWANPacket:
    dev_addr: int
    fcnt: int
    port: int
    payload: bytes
    rssi: int
    snr: float
    timestamp: float
    gateway_id: str
