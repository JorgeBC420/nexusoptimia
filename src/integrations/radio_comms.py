"""
Módulo de comunicación LoRa y UHF/VHF para NexusOptim IA
Permite enviar y recibir datos usando LoRa (pyLoRa) y radios UHF/VHF (hamlib, pyserial)
"""

import logging
import serial
from lora import LoRa
import hamlib

logger = logging.getLogger(__name__)

class LoRaRadio:
    def __init__(self, port="COM3", freq=915e6, spi_bus=0, spi_cs=0):
        self.lora = LoRa(port=port, freq=freq, spi_bus=spi_bus, spi_cs=spi_cs)
        logger.info(f"LoRa inicializado en {port} frecuencia {freq/1e6} MHz")

    def send(self, data: bytes):
        logger.info(f"Enviando por LoRa: {data}")
        self.lora.write(data)

    def receive(self) -> bytes:
        data = self.lora.read()
        logger.info(f"Recibido por LoRa: {data}")
        return data

class UHFVHFSerialRadio:
    def __init__(self, port="COM4", baudrate=9600, timeout=2):
        self.ser = serial.Serial(port, baudrate, timeout=timeout)
        logger.info(f"Serial UHF/VHF abierto en {port} baudrate {baudrate}")

    def send(self, data: bytes):
        logger.info(f"Enviando por UHF/VHF serial: {data}")
        self.ser.write(data)

    def receive(self) -> bytes:
        data = self.ser.readline()
        logger.info(f"Recibido por UHF/VHF serial: {data}")
        return data

class HamlibRadio:
    def __init__(self, rig_model=2, rig_port="/dev/ttyUSB0", baudrate=9600):
        hamlib.rig_set_debug(0)
        self.rig = hamlib.Rig(rig_model)
        self.rig.set_conf("rig_pathname", rig_port)
        self.rig.set_conf("serial_speed", str(baudrate))
        self.rig.open()
        logger.info(f"Hamlib radio abierto en {rig_port} modelo {rig_model}")

    def set_freq(self, freq_hz):
        self.rig.set_freq(freq_hz)
        logger.info(f"Frecuencia radio ajustada a {freq_hz} Hz")

    def send(self, data: bytes):
        # Para radios con soporte de transmisión de datos
        logger.info(f"Enviando por hamlib: {data}")
        # Implementar según radio

    def receive(self):
        # Implementar según radio
        pass

# Ejemplo de uso:
# lora = LoRaRadio(port="COM3")
# lora.send(b"Hola LoRa")
# radio = UHFVHFSerialRadio(port="COM4")
# radio.send(b"Hola UHF/VHF")
# ham = HamlibRadio(rig_model=2, rig_port="/dev/ttyUSB0")
# ham.set_freq(145500000)
