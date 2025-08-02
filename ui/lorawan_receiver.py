"""
NexusOptim IA - LoRaWAN Data Receiver
Real-time data reception from electrical sensors

This module handles:
- LoRaWAN packet reception and decoding
- Data parsing from NexusOptim electrical sensors
- Real-time data forwarding to monitoring dashboard
- Network management and device discovery

Compatible with: main_electrical.c firmware
Protocol: LoRaWAN 1.0.3 on Helium Network

Copyright (c) 2025 OpenNexus
Licensed under MIT License
"""

import socket
import struct
import json
import time
import threading
from datetime import datetime
from typing import Dict, List, Optional, Tuple
from dataclasses import dataclass, asdict
import logging

# Configure logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

@dataclass
class LoRaWANPacket:
    """LoRaWAN packet structure matching firmware"""
    dev_addr: int
    fcnt: int
    port: int
    payload: bytes
    rssi: int
    snr: float
    timestamp: float
    gateway_id: str

@dataclass
class ElectricalSensorData:
    """Electrical sensor data structure matching firmware payload"""
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

class LoRaWANReceiver:
    """LoRaWAN data receiver for Helium Network integration"""
    
    def __init__(self, webhook_port: int = 8080):
        self.webhook_port = webhook_port
        self.server_socket = None
        self.running = False
        self.data_callbacks = []
        self.device_registry: Dict[str, Dict] = {}
        
    def add_data_callback(self, callback):
        """Add callback function to receive parsed sensor data"""
        self.data_callbacks.append(callback)
        
    def start_server(self):
        """Start the webhook server to receive LoRaWAN data"""
        try:
            self.server_socket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
            self.server_socket.setsockopt(socket.SOL_SOCKET, socket.SO_REUSEADDR, 1)
            self.server_socket.bind(('localhost', self.webhook_port))
            self.server_socket.listen(5)
            
            self.running = True
            logger.info(f"LoRaWAN receiver started on port {self.webhook_port}")
            
            # Start server thread
            server_thread = threading.Thread(target=self._server_worker, daemon=True)
            server_thread.start()
            
            return True
            
        except Exception as e:
            logger.error(f"Failed to start LoRaWAN receiver: {e}")
            return False
    
    def stop_server(self):
        """Stop the webhook server"""
        self.running = False
        if self.server_socket:
            self.server_socket.close()
            
    def _server_worker(self):
        """Main server worker thread"""
        while self.running:
            try:
                client_socket, address = self.server_socket.accept()
                # Handle client in separate thread
                client_thread = threading.Thread(
                    target=self._handle_client, 
                    args=(client_socket, address),
                    daemon=True
                )
                client_thread.start()
                
            except Exception as e:
                if self.running:  # Only log if we're supposed to be running
                    logger.error(f"Server error: {e}")
                    
    def _handle_client(self, client_socket, address):
        """Handle individual client connections (Helium webhooks)"""
        try:
            # Read HTTP request
            request_data = client_socket.recv(4096).decode('utf-8')
            
            if 'POST' in request_data:
                # Extract JSON payload from HTTP POST
                json_start = request_data.find('\n\n') + 2
                if json_start > 1:
                    json_data = request_data[json_start:]
                    self._process_helium_webhook(json_data)
            
            # Send HTTP response
            response = "HTTP/1.1 200 OK\nContent-Length: 2\n\nOK"
            client_socket.send(response.encode('utf-8'))
            
        except Exception as e:
            logger.error(f"Error handling client {address}: {e}")
        finally:
            client_socket.close()
            
    def _process_helium_webhook(self, json_data: str):
        """Process incoming Helium webhook data"""
        try:
            data = json.loads(json_data)
            
            # Extract LoRaWAN packet information
            if 'uplink_message' in data:
                uplink = data['uplink_message']
                
                packet = LoRaWANPacket(
                    dev_addr=int(uplink.get('dev_addr', '0'), 16),
                    fcnt=uplink.get('f_cnt', 0),
                    port=uplink.get('f_port', 0),
                    payload=bytes.fromhex(uplink.get('frm_payload', '')),
                    rssi=uplink.get('rx_metadata', [{}])[0].get('rssi', -999),
                    snr=uplink.get('rx_metadata', [{}])[0].get('snr', -999),
                    timestamp=time.time(),
                    gateway_id=uplink.get('rx_metadata', [{}])[0].get('gateway_ids', {}).get('gateway_id', 'unknown')
                )
                
                # Parse sensor data based on port
                if packet.port == 10:  # Electrical data port (from firmware)
                    sensor_data = self._parse_electrical_payload(packet.payload)
                    if sensor_data:
                        sensor_data.timestamp = int(packet.timestamp)
                        self._notify_callbacks(sensor_data, packet)
                        
                elif packet.port == 99:  # Emergency port
                    self._handle_emergency_packet(packet)
                    
        except Exception as e:
            logger.error(f"Error processing webhook data: {e}")
            
    def _parse_electrical_payload(self, payload: bytes) -> Optional[ElectricalSensorData]:
        """Parse electrical sensor payload (24 bytes as per firmware)"""
        try:
            if len(payload) < 24:
                logger.warning(f"Payload too short: {len(payload)} bytes")
                return None
                
            # Unpack payload according to firmware structure
            # payload format: sector_id, node_id, type, safety, voltage, current, power, pf, freq, thd_v, thd_i, grade, timestamp, reactive, battery, crc
            
            data = ElectricalSensorData(
                sector_id=payload[0],
                node_id=payload[1],
                measurement_type=payload[2],
                safety_status=payload[3],
                voltage_rms=(payload[4] << 8 | payload[5]) / 10.0,  # 0.1V resolution
                current_rms=(payload[6] << 8 | payload[7]) / 100.0,  # 0.01A resolution
                power_active=payload[8] << 8 | payload[9],  # 1W resolution
                power_factor=payload[10] / 100.0,  # 0.01 resolution
                frequency=(payload[11] / 10.0) + 45.0,  # 0.1Hz resolution, offset from 45Hz
                thd_voltage=payload[12] / 10.0,  # 0.1% resolution
                thd_current=payload[13] / 10.0,  # 0.1% resolution
                quality_grade=payload[14],
                timestamp=(payload[15] << 24 | payload[16] << 16 | payload[17] << 8 | payload[18]),
                power_reactive=payload[19] << 8 | payload[20],  # 1VAR resolution
                battery_level=payload[21],
                checksum=payload[22]
            )
            
            # Verify checksum (simple implementation)
            calculated_crc = sum(payload[:22]) & 0xFF
            if calculated_crc != data.checksum:
                logger.warning(f"Checksum mismatch: calculated {calculated_crc}, received {data.checksum}")
            
            return data
            
        except Exception as e:
            logger.error(f"Error parsing electrical payload: {e}")
            return None
            
    def _handle_emergency_packet(self, packet: LoRaWANPacket):
        """Handle emergency alert packets"""
        try:
            if len(packet.payload) >= 4:
                emergency_flag = packet.payload[0]
                sector_id = packet.payload[1]
                alert_type = packet.payload[2]
                
                logger.critical(f"EMERGENCY ALERT: Sector {sector_id}, Type {alert_type}, Device {packet.dev_addr:08X}")
                
                # Here you would implement emergency notification system
                # (email, SMS, push notifications, etc.)
                
        except Exception as e:
            logger.error(f"Error handling emergency packet: {e}")
            
    def _notify_callbacks(self, sensor_data: ElectricalSensorData, packet: LoRaWANPacket):
        """Notify all registered callbacks with new sensor data"""
        for callback in self.data_callbacks:
            try:
                callback(sensor_data, packet)
            except Exception as e:
                logger.error(f"Error in data callback: {e}")
                
    def register_device(self, dev_addr: str, device_info: dict):
        """Register a device in the device registry"""
        self.device_registry[dev_addr] = device_info
        logger.info(f"Registered device {dev_addr}: {device_info}")
        
    def get_device_info(self, dev_addr: str) -> Optional[dict]:
        """Get device information from registry"""
        return self.device_registry.get(dev_addr)

class SimulatedLoRaWANReceiver(LoRaWANReceiver):
    """Simulated LoRaWAN receiver for testing without real hardware"""
    
    def __init__(self):
        super().__init__()
        self.simulation_thread = None
        
        # Load simulation configuration
        self.load_simulation_config()
        
    def load_simulation_config(self):
        """Load simulation configuration from file"""
        try:
            import json
            import os
            
            config_file = "simulation_config.json"
            if os.path.exists(config_file):
                with open(config_file, 'r') as f:
                    config = json.load(f)
                self.sim_config = config.get("parameters", self.get_default_config())
                logger.info(f"Loaded simulation scenario: {config.get('scenario', 'default')}")
            else:
                self.sim_config = self.get_default_config()
                logger.info("Using default simulation configuration")
                
        except Exception as e:
            logger.error(f"Error loading simulation config: {e}")
            self.sim_config = self.get_default_config()
            
    def get_default_config(self):
        """Get default simulation configuration"""
        return {
            "voltage_base": 230.0,
            "voltage_variation": 2.0,
            "current_base": 10.0,
            "current_variation": 1.0,
            "frequency_base": 50.0,
            "frequency_variation": 0.05,
            "thd_base": 2.0,
            "alert_probability": 0.05,
            "active_nodes": 1
        }
        
    def start_simulation(self):
        """Start data simulation instead of real LoRaWAN reception"""
        self.running = True
        self.simulation_thread = threading.Thread(target=self._simulation_worker, daemon=True)
        self.simulation_thread.start()
        logger.info("Started LoRaWAN simulation mode")
        
    def _simulation_worker(self):
        """Generate simulated electrical sensor data"""
        import random
        import numpy as np
        
        while self.running:
            try:
                # Use configuration-based parameters
                voltage = (self.sim_config["voltage_base"] + 
                          random.gauss(0, self.sim_config["voltage_variation"]))
                voltage = max(180, min(260, voltage))  # Clamp to realistic range
                
                current = (self.sim_config["current_base"] + 
                          random.gauss(0, self.sim_config["current_variation"]))
                current = max(0.5, min(25, current))  # Clamp to realistic range
                
                # Calculate power
                power = voltage * current * (0.95 + random.gauss(0, 0.02))  # PF ~0.95
                
                # Simulate occasional power quality issues
                thd_v = max(0.5, abs(random.gauss(self.sim_config["thd_base"], 1.0)))
                thd_c = max(0.5, abs(random.gauss(self.sim_config["thd_base"], 1.2)))
                
                # Frequency variation based on config
                frequency = (self.sim_config["frequency_base"] + 
                           random.gauss(0, self.sim_config["frequency_variation"]))
                
                # Power factor
                power_factor = max(0.7, min(1.0, 0.95 + random.gauss(0, 0.02)))
                
                # Safety status based on configuration probability
                safety_status = 0
                if random.random() < self.sim_config["alert_probability"]:
                    # Choose alerts based on actual conditions
                    if voltage > 245.0:
                        safety_status |= 0x01  # Overvoltage
                    elif voltage < 210.0:
                        safety_status |= 0x02  # Undervoltage
                    
                    if current > 16.0:
                        safety_status |= 0x04  # Overcurrent
                    
                    if power > 3800.0:
                        safety_status |= 0x08  # Overpower
                    
                    if power_factor < 0.8:
                        safety_status |= 0x10  # Low PF
                    
                    if thd_v > 6.0 or thd_c > 6.0:
                        safety_status |= 0x20  # High THD
                    
                    if abs(frequency - 50.0) > 0.3:
                        safety_status |= 0x40  # Freq deviation
                    
                    # If no specific alerts, occasionally add mild ones
                    if safety_status == 0 and random.random() < 0.3:
                        safety_status = random.choice([0x10, 0x20])  # Mild quality issues
                
                # Quality grade based on THD and power factor
                quality_grade = 0  # Start with A
                if thd_v > 3.0 or thd_c > 3.0:
                    quality_grade += 1
                if power_factor < 0.9:
                    quality_grade += 1
                quality_grade = min(quality_grade, 5)
                
                # Create simulated sensor data
                sensor_data = ElectricalSensorData(
                    sector_id=1,  # Energy sector
                    node_id=1,
                    measurement_type=0x10,  # Electrical measurements
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
                    power_reactive=power * 0.1,  # Assume small reactive component
                    battery_level=random.randint(80, 100),  # Good battery
                    checksum=0x42  # Dummy checksum
                )
                
                # Create dummy packet info
                packet = LoRaWANPacket(
                    dev_addr=0x12345678,
                    fcnt=random.randint(1000, 9999),
                    port=10,
                    payload=b'',  # Not used in simulation
                    rssi=random.randint(-120, -60),
                    snr=random.uniform(-10, 10),
                    timestamp=time.time(),
                    gateway_id='sim_gateway_001'
                )
                
                # Notify callbacks
                self._notify_callbacks(sensor_data, packet)
                
                # Wait for next update (1 second intervals)
                time.sleep(1.0)
                
            except Exception as e:
                logger.error(f"Simulation error: {e}")
                time.sleep(1.0)
                
    def stop_simulation(self):
        """Stop the simulation"""
        logger.info("Stopping LoRaWAN simulation...")
        self.running = False
        if self.simulation_thread and self.simulation_thread.is_alive():
            try:
                self.simulation_thread.join(timeout=2.0)
                if self.simulation_thread.is_alive():
                    logger.warning("Simulation thread did not stop gracefully")
            except Exception as e:
                logger.error(f"Error stopping simulation: {e}")
        logger.info("LoRaWAN simulation stopped")

def main():
    """Test the LoRaWAN receiver"""
    def data_received(sensor_data: ElectricalSensorData, packet: LoRaWANPacket):
        print(f"Received data from device {packet.dev_addr:08X}:")
        print(f"  Voltage: {sensor_data.voltage_rms:.2f}V")
        print(f"  Current: {sensor_data.current_rms:.2f}A")
        print(f"  Power: {sensor_data.power_active:.1f}W")
        print(f"  Power Factor: {sensor_data.power_factor:.3f}")
        print(f"  Frequency: {sensor_data.frequency:.2f}Hz")
        print(f"  RSSI: {packet.rssi}dBm")
        print("---")
    
    # Create receiver
    receiver = SimulatedLoRaWANReceiver()
    receiver.add_data_callback(data_received)
    
    # Start simulation
    receiver.start_simulation()
    
    try:
        # Let it run for demo
        time.sleep(10)
    except KeyboardInterrupt:
        pass
    finally:
        receiver.stop_simulation()

if __name__ == "__main__":
    main()
