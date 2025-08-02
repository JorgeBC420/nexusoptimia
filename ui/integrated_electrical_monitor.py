"""
NexusOptim IA - Integrated Electrical Monitoring System
Complete electrical monitoring solution with LoRaWAN integration

This is the main application that combines:
- Real-time electrical monitoring dashboard
- LoRaWAN data reception from sensors
- Data logging and historical analysis
- Alert management and notifications

Usage:
    python integrated_electrical_monitor.py

Copyright (c) 2025 OpenNexus
Licensed under MIT License
"""

import tkinter as tk
from tkinter import messagebox
import threading
import time
import json
from datetime import datetime
from electrical_monitoring_dashboard import ElectricalMonitoringUI, ElectricalData
from lorawan_receiver import SimulatedLoRaWANReceiver, ElectricalSensorData, LoRaWANPacket
import logging

# Configure logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
    handlers=[
        logging.FileHandler('nexusoptim_electrical.log'),
        logging.StreamHandler()
    ]
)
logger = logging.getLogger(__name__)

class IntegratedElectricalMonitor:
    """Integrated electrical monitoring system"""
    
    def __init__(self):
        self.root = tk.Tk()
        self.dashboard = None
        self.lorawan_receiver = None
        self.data_logger = None
        
        # Configuration
        self.config = {
            'simulation_mode': True,  # Set to False for real LoRaWAN
            'log_data': True,
            'alert_thresholds': {
                'voltage_min': 210.0,
                'voltage_max': 250.0,
                'current_max': 15.0,
                'frequency_min': 49.5,
                'frequency_max': 50.5,
                'thd_max': 5.0,
                'power_factor_min': 0.85
            }
        }
        
    def start(self):
        """Start the integrated monitoring system"""
        logger.info("Starting NexusOptim IA Electrical Monitoring System")
        
        try:
            # Create dashboard
            self.dashboard = ElectricalMonitoringUI(self.root)
            
            # Setup proper window close handler
            self.root.protocol("WM_DELETE_WINDOW", self._on_window_close)
            
            # Setup LoRaWAN receiver
            self._setup_lorawan_receiver()
            
            # Setup data logging
            if self.config['log_data']:
                self._setup_data_logging()
            
            # Show startup message
            self._show_startup_message()
            
            # Start the GUI
            self.root.mainloop()
            
        except Exception as e:
            logger.error(f"Failed to start monitoring system: {e}")
            messagebox.showerror("Startup Error", f"Failed to start monitoring system:\n{e}")
            
    def _on_window_close(self):
        """Handle window close event safely"""
        try:
            logger.info("Window close requested - initiating clean shutdown")
            
            # Show confirmation dialog
            if messagebox.askokcancel("Cerrar Sistema", 
                                    "¿Desea cerrar el sistema de monitoreo?\n\n"
                                    "Se detendrán todas las mediciones en tiempo real."):
                
                # Perform clean shutdown
                self.shutdown()
                
                # Close the window
                self.root.quit()
                self.root.destroy()
                
        except Exception as e:
            logger.error(f"Error during window close: {e}")
            # Force close if there's an error
            try:
                self.root.quit()
                self.root.destroy()
            except:
                pass
            
    def _setup_lorawan_receiver(self):
        """Setup LoRaWAN data receiver"""
        try:
            if self.config['simulation_mode']:
                self.lorawan_receiver = SimulatedLoRaWANReceiver()
                self.lorawan_receiver.add_data_callback(self._handle_sensor_data)
                self.lorawan_receiver.start_simulation()
                logger.info("Started in simulation mode")
            else:
                # Real LoRaWAN receiver (requires Helium webhook setup)
                from lorawan_receiver import LoRaWANReceiver
                self.lorawan_receiver = LoRaWANReceiver(webhook_port=8080)
                self.lorawan_receiver.add_data_callback(self._handle_sensor_data)
                if not self.lorawan_receiver.start_server():
                    raise Exception("Failed to start LoRaWAN receiver")
                logger.info("Started LoRaWAN webhook receiver on port 8080")
                
        except Exception as e:
            logger.error(f"Failed to setup LoRaWAN receiver: {e}")
            raise
            
    def _setup_data_logging(self):
        """Setup data logging to file"""
        self.data_logger = DataLogger('nexusoptim_data.json')
        logger.info("Data logging enabled")
        
    def _handle_sensor_data(self, sensor_data: ElectricalSensorData, packet: LoRaWANPacket):
        """Handle incoming sensor data from LoRaWAN"""
        try:
            # Convert to dashboard format
            dashboard_data = ElectricalData(
                timestamp=sensor_data.timestamp,
                voltage_rms=sensor_data.voltage_rms,
                current_rms=sensor_data.current_rms,
                power_active=sensor_data.power_active,
                power_reactive=sensor_data.power_reactive,
                power_apparent=0,  # Will be calculated
                power_factor=sensor_data.power_factor,
                frequency=sensor_data.frequency,
                thd_voltage=sensor_data.thd_voltage,
                thd_current=sensor_data.thd_current,
                safety_status=sensor_data.safety_status,
                quality_grade=sensor_data.quality_grade,
                node_id=sensor_data.node_id
            )
            
            # Calculate apparent power
            dashboard_data.power_apparent = (
                dashboard_data.power_active**2 + dashboard_data.power_reactive**2
            )**0.5
            
            # Add to dashboard queue
            if self.dashboard:
                self.dashboard.data_queue.put(dashboard_data)
            
            # Log data if enabled
            if self.data_logger:
                self.data_logger.log_data(sensor_data, packet)
            
            # Check for alerts
            self._check_alerts(sensor_data, packet)
            
            logger.debug(f"Processed data from node {sensor_data.node_id}: "
                        f"V={sensor_data.voltage_rms:.1f}V, "
                        f"I={sensor_data.current_rms:.1f}A, "
                        f"P={sensor_data.power_active:.0f}W")
            
        except Exception as e:
            logger.error(f"Error handling sensor data: {e}")
            
    def _check_alerts(self, sensor_data: ElectricalSensorData, packet: LoRaWANPacket):
        """Check sensor data against alert thresholds"""
        alerts = []
        thresholds = self.config['alert_thresholds']
        
        # Voltage alerts
        if sensor_data.voltage_rms < thresholds['voltage_min']:
            alerts.append(f"Low voltage: {sensor_data.voltage_rms:.1f}V")
        elif sensor_data.voltage_rms > thresholds['voltage_max']:
            alerts.append(f"High voltage: {sensor_data.voltage_rms:.1f}V")
            
        # Current alerts
        if sensor_data.current_rms > thresholds['current_max']:
            alerts.append(f"High current: {sensor_data.current_rms:.1f}A")
            
        # Frequency alerts
        if (sensor_data.frequency < thresholds['frequency_min'] or 
            sensor_data.frequency > thresholds['frequency_max']):
            alerts.append(f"Frequency deviation: {sensor_data.frequency:.2f}Hz")
            
        # THD alerts
        if (sensor_data.thd_voltage > thresholds['thd_max'] or 
            sensor_data.thd_current > thresholds['thd_max']):
            alerts.append(f"High THD: V={sensor_data.thd_voltage:.1f}%, I={sensor_data.thd_current:.1f}%")
            
        # Power factor alerts
        if sensor_data.power_factor < thresholds['power_factor_min']:
            alerts.append(f"Low power factor: {sensor_data.power_factor:.3f}")
            
        # Safety status alerts (from firmware)
        if sensor_data.safety_status != 0:
            safety_flags = []
            if sensor_data.safety_status & 0x01:
                safety_flags.append("Overvoltage")
            if sensor_data.safety_status & 0x02:
                safety_flags.append("Undervoltage")
            if sensor_data.safety_status & 0x04:
                safety_flags.append("Overcurrent")
            if sensor_data.safety_status & 0x08:
                safety_flags.append("Overpower")
            if sensor_data.safety_status & 0x10:
                safety_flags.append("Low PF")
            if sensor_data.safety_status & 0x20:
                safety_flags.append("High THD")
            if sensor_data.safety_status & 0x40:
                safety_flags.append("Freq deviation")
            if sensor_data.safety_status & 0x80:
                safety_flags.append("Phase imbalance")
            
            alerts.append(f"Safety alerts: {', '.join(safety_flags)}")
        
        # Log and display alerts
        if alerts:
            alert_message = f"Node {sensor_data.node_id} ALERTS: {'; '.join(alerts)}"
            logger.warning(alert_message)
            
            # Show critical alerts in GUI
            if any(keyword in alert_message.lower() for keyword in ['overvoltage', 'overcurrent', 'overpower']):
                self.root.after(0, lambda: messagebox.showwarning("Critical Alert", alert_message))
                
    def _show_startup_message(self):
        """Show startup information"""
        mode = "Simulation" if self.config['simulation_mode'] else "Live LoRaWAN"
        logging_status = "Enabled" if self.config['log_data'] else "Disabled"
        
        startup_msg = f"""NexusOptim IA Electrical Monitoring System Started
        
Mode: {mode}
Data Logging: {logging_status}
Dashboard: Active
        
Ready for electrical monitoring...
        """
        
        logger.info("System startup complete")
        messagebox.showinfo("NexusOptim IA - System Ready", startup_msg)
        
    def shutdown(self):
        """Shutdown the monitoring system"""
        logger.info("Shutting down monitoring system")
        
        try:
            # Stop dashboard updates first
            if self.dashboard:
                self.dashboard.running = False
                
            # Stop LoRaWAN receiver
            if self.lorawan_receiver:
                if hasattr(self.lorawan_receiver, 'stop_simulation'):
                    self.lorawan_receiver.stop_simulation()
                elif hasattr(self.lorawan_receiver, 'stop_server'):
                    self.lorawan_receiver.stop_server()
                    
            # Close data logger
            if self.data_logger:
                self.data_logger.close()
                
            # Give threads time to clean up
            import time
            time.sleep(0.5)
            
            logger.info("Shutdown complete")
            
        except Exception as e:
            logger.error(f"Error during shutdown: {e}")
            # Continue with shutdown even if there are errors

class DataLogger:
    """Data logging utility"""
    
    def __init__(self, filename: str):
        self.filename = filename
        self.log_file = open(filename, 'a')
        
    def log_data(self, sensor_data: ElectricalSensorData, packet: LoRaWANPacket):
        """Log sensor data to file"""
        try:
            log_entry = {
                'timestamp': datetime.now().isoformat(),
                'sensor_data': {
                    'node_id': sensor_data.node_id,
                    'voltage_rms': sensor_data.voltage_rms,
                    'current_rms': sensor_data.current_rms,
                    'power_active': sensor_data.power_active,
                    'power_factor': sensor_data.power_factor,
                    'frequency': sensor_data.frequency,
                    'thd_voltage': sensor_data.thd_voltage,
                    'thd_current': sensor_data.thd_current,
                    'safety_status': sensor_data.safety_status,
                    'quality_grade': sensor_data.quality_grade,
                    'battery_level': sensor_data.battery_level
                },
                'network_data': {
                    'dev_addr': f"{packet.dev_addr:08X}",
                    'rssi': packet.rssi,
                    'snr': packet.snr,
                    'gateway_id': packet.gateway_id
                }
            }
            
            self.log_file.write(json.dumps(log_entry) + '\n')
            self.log_file.flush()
            
        except Exception as e:
            logger.error(f"Error logging data: {e}")
            
    def close(self):
        """Close log file"""
        if self.log_file:
            self.log_file.close()

def main():
    """Main application entry point"""
    try:
        # Create and start the integrated monitoring system
        monitor = IntegratedElectricalMonitor()
        
        # Setup shutdown handler for clean exit
        def on_closing():
            try:
                monitor.shutdown()
                monitor.root.quit()
                monitor.root.destroy()
            except:
                pass
            
        # Handle Ctrl+C gracefully
        def signal_handler(signum, frame):
            logger.info("Received interrupt signal")
            on_closing()
            
        import signal
        signal.signal(signal.SIGINT, signal_handler)
        signal.signal(signal.SIGTERM, signal_handler)
        
        # Start the system
        monitor.start()
        
    except KeyboardInterrupt:
        logger.info("Application interrupted by user")
    except Exception as e:
        logger.error(f"Application error: {e}")
        try:
            messagebox.showerror("Application Error", f"An error occurred:\n{e}")
        except:
            pass

if __name__ == "__main__":
    main()
