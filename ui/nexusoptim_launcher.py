"""
NexusOptim IA - Application Launcher
Main entry point for the electrical monitoring system

This launcher provides:
- System initialization
- Configuration management
- Error handling and recovery
- System status monitoring

Usage:
    python nexusoptim_launcher.py

Copyright (c) 2025 OpenNexus
Licensed under MIT License
"""

import tkinter as tk
from tkinter import ttk, messagebox
import sys
import os
import json
import logging
from pathlib import Path
import subprocess
import threading
import time

# Configure logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
    handlers=[
        logging.FileHandler('nexusoptim_launcher.log'),
        logging.StreamHandler()
    ]
)
logger = logging.getLogger(__name__)

class NexusOptimLauncher:
    """Main application launcher for NexusOptim IA"""
    
    def __init__(self):
        self.root = tk.Tk()
        self.root.title("NexusOptim IA - System Launcher")
        self.root.geometry("600x500")
        self.root.resizable(False, False)
        
        # Configuration
        self.config_file = "nexusoptim_config.json"
        self.config = self.load_config()
        
        # Setup UI
        self.setup_ui()
        
        # System status
        self.system_running = False
        self.monitoring_process = None
        
    def load_config(self):
        """Load system configuration"""
        default_config = {
            "system": {
                "name": "NexusOptim IA",
                "version": "1.0.0",
                "startup_mode": "launcher"
            },
            "monitoring": {
                "simulation_mode": True,
                "data_logging": True,
                "auto_start": False,
                "log_level": "INFO"
            },
            "lorawan": {
                "webhook_port": 8080,
                "frequency_band": "AU915",
                "network": "Helium"
            },
            "alerts": {
                "enable_notifications": True,
                "sound_alerts": True,
                "email_notifications": False,
                "sms_notifications": False
            },
            "ui": {
                "theme": "dark",
                "update_interval": 1000,
                "chart_history": 300
            }
        }
        
        try:
            if os.path.exists(self.config_file):
                with open(self.config_file, 'r') as f:
                    config = json.load(f)
                # Merge with defaults
                for section, values in default_config.items():
                    if section not in config:
                        config[section] = values
                    else:
                        for key, value in values.items():
                            if key not in config[section]:
                                config[section][key] = value
                return config
            else:
                self.save_config(default_config)
                return default_config
        except Exception as e:
            logger.error(f"Error loading config: {e}")
            return default_config
            
    def save_config(self, config=None):
        """Save system configuration"""
        if config is None:
            config = self.config
            
        try:
            with open(self.config_file, 'w') as f:
                json.dump(config, f, indent=4)
        except Exception as e:
            logger.error(f"Error saving config: {e}")
            
    def setup_ui(self):
        """Setup the launcher user interface"""
        # Main frame
        main_frame = ttk.Frame(self.root, padding="20")
        main_frame.grid(row=0, column=0, sticky=(tk.W, tk.E, tk.N, tk.S))
        
        # Title
        title_label = ttk.Label(main_frame, text="NexusOptim IA", 
                               font=('Arial', 24, 'bold'))
        title_label.grid(row=0, column=0, columnspan=2, pady=(0, 10))
        
        subtitle_label = ttk.Label(main_frame, text="Electrical Monitoring System", 
                                  font=('Arial', 12))
        subtitle_label.grid(row=1, column=0, columnspan=2, pady=(0, 20))
        
        # Status frame
        status_frame = ttk.LabelFrame(main_frame, text="System Status", padding="10")
        status_frame.grid(row=2, column=0, columnspan=2, sticky=(tk.W, tk.E), pady=(0, 20))
        
        self.status_var = tk.StringVar(value="System Ready")
        self.status_label = ttk.Label(status_frame, textvariable=self.status_var)
        self.status_label.grid(row=0, column=0, sticky=tk.W)
        
        self.mode_var = tk.StringVar(value=f"Mode: {'Simulation' if self.config['monitoring']['simulation_mode'] else 'Live'}")
        self.mode_label = ttk.Label(status_frame, textvariable=self.mode_var)
        self.mode_label.grid(row=1, column=0, sticky=tk.W)
        
        # Control buttons
        button_frame = ttk.Frame(main_frame)
        button_frame.grid(row=3, column=0, columnspan=2, pady=(0, 20))
        
        self.start_button = ttk.Button(button_frame, text="Start Monitoring", 
                                      command=self.start_monitoring, width=20)
        self.start_button.grid(row=0, column=0, padx=(0, 10))
        
        self.stop_button = ttk.Button(button_frame, text="Stop Monitoring", 
                                     command=self.stop_monitoring, width=20,
                                     state='disabled')
        self.stop_button.grid(row=0, column=1, padx=(10, 0))
        
        # Configuration frame
        config_frame = ttk.LabelFrame(main_frame, text="Configuration", padding="10")
        config_frame.grid(row=4, column=0, columnspan=2, sticky=(tk.W, tk.E), pady=(0, 20))
        
        # Simulation mode
        self.sim_mode_var = tk.BooleanVar(value=self.config['monitoring']['simulation_mode'])
        sim_check = ttk.Checkbutton(config_frame, text="Simulation Mode", 
                                   variable=self.sim_mode_var,
                                   command=self.update_config)
        sim_check.grid(row=0, column=0, sticky=tk.W)
        
        # Data logging
        self.logging_var = tk.BooleanVar(value=self.config['monitoring']['data_logging'])
        logging_check = ttk.Checkbutton(config_frame, text="Enable Data Logging", 
                                       variable=self.logging_var,
                                       command=self.update_config)
        logging_check.grid(row=1, column=0, sticky=tk.W)
        
        # Auto start
        self.autostart_var = tk.BooleanVar(value=self.config['monitoring']['auto_start'])
        autostart_check = ttk.Checkbutton(config_frame, text="Auto-start Monitoring", 
                                         variable=self.autostart_var,
                                         command=self.update_config)
        autostart_check.grid(row=2, column=0, sticky=tk.W)
        
        # Advanced configuration button
        advanced_button = ttk.Button(config_frame, text="Advanced Settings", 
                                    command=self.show_advanced_config)
        advanced_button.grid(row=3, column=0, pady=(10, 0))
        
        # Simulation configurator button
        sim_config_button = ttk.Button(config_frame, text="Configurar Escenarios", 
                                      command=self.show_simulation_config)
        sim_config_button.grid(row=4, column=0, pady=(5, 0))
        
        # Information frame
        info_frame = ttk.LabelFrame(main_frame, text="System Information", padding="10")
        info_frame.grid(row=5, column=0, columnspan=2, sticky=(tk.W, tk.E))
        
        info_text = f"""Version: {self.config['system']['version']}
LoRaWAN Band: {self.config['lorawan']['frequency_band']}
Network: {self.config['lorawan']['network']}
Webhook Port: {self.config['lorawan']['webhook_port']}"""
        
        info_label = ttk.Label(info_frame, text=info_text, justify=tk.LEFT)
        info_label.grid(row=0, column=0, sticky=tk.W)
        
        # Auto-start if configured
        if self.config['monitoring']['auto_start']:
            self.root.after(2000, self.start_monitoring)
            
    def update_config(self):
        """Update configuration from UI"""
        self.config['monitoring']['simulation_mode'] = self.sim_mode_var.get()
        self.config['monitoring']['data_logging'] = self.logging_var.get()
        self.config['monitoring']['auto_start'] = self.autostart_var.get()
        
        self.mode_var.set(f"Mode: {'Simulation' if self.sim_mode_var.get() else 'Live'}")
        self.save_config()
        
    def show_advanced_config(self):
        """Show advanced configuration dialog"""
        config_window = tk.Toplevel(self.root)
        config_window.title("Advanced Configuration")
        config_window.geometry("400x300")
        config_window.resizable(False, False)
        
        notebook = ttk.Notebook(config_window)
        notebook.pack(fill='both', expand=True, padx=10, pady=10)
        
        # LoRaWAN tab
        lorawan_frame = ttk.Frame(notebook)
        notebook.add(lorawan_frame, text='LoRaWAN')
        
        ttk.Label(lorawan_frame, text="Webhook Port:").grid(row=0, column=0, sticky=tk.W, padx=5, pady=5)
        port_var = tk.StringVar(value=str(self.config['lorawan']['webhook_port']))
        port_entry = ttk.Entry(lorawan_frame, textvariable=port_var, width=10)
        port_entry.grid(row=0, column=1, padx=5, pady=5)
        
        ttk.Label(lorawan_frame, text="Frequency Band:").grid(row=1, column=0, sticky=tk.W, padx=5, pady=5)
        band_var = tk.StringVar(value=self.config['lorawan']['frequency_band'])
        band_combo = ttk.Combobox(lorawan_frame, textvariable=band_var, 
                                 values=['AU915', 'US915', 'EU868', 'AS923'])
        band_combo.grid(row=1, column=1, padx=5, pady=5)
        
        # Alerts tab
        alerts_frame = ttk.Frame(notebook)
        notebook.add(alerts_frame, text='Alerts')
        
        notifications_var = tk.BooleanVar(value=self.config['alerts']['enable_notifications'])
        ttk.Checkbutton(alerts_frame, text="Enable Notifications", 
                       variable=notifications_var).grid(row=0, column=0, sticky=tk.W, padx=5, pady=5)
        
        sound_var = tk.BooleanVar(value=self.config['alerts']['sound_alerts'])
        ttk.Checkbutton(alerts_frame, text="Sound Alerts", 
                       variable=sound_var).grid(row=1, column=0, sticky=tk.W, padx=5, pady=5)
        
        # Save button
        def save_advanced():
            try:
                self.config['lorawan']['webhook_port'] = int(port_var.get())
                self.config['lorawan']['frequency_band'] = band_var.get()
                self.config['alerts']['enable_notifications'] = notifications_var.get()
                self.config['alerts']['sound_alerts'] = sound_var.get()
                self.save_config()
                config_window.destroy()
                messagebox.showinfo("Configuration", "Settings saved successfully!")
            except ValueError:
                messagebox.showerror("Error", "Invalid port number!")
                
        save_button = ttk.Button(config_window, text="Save", command=save_advanced)
        save_button.pack(pady=10)
        
    def show_simulation_config(self):
        """Show simulation scenario configurator"""
        try:
            from simulation_configurator import SimulationConfigurator
            configurator = SimulationConfigurator(self.root)
        except ImportError as e:
            messagebox.showerror("Error", f"Cannot load simulation configurator:\n{e}")
        except Exception as e:
            messagebox.showerror("Error", f"Error opening configurator:\n{e}")
        
    def start_monitoring(self):
        """Start the monitoring system"""
        if self.system_running:
            return
            
        try:
            self.status_var.set("Starting monitoring system...")
            self.start_button.config(state='disabled')
            
            # Save current config for the monitoring system
            self.save_config()
            
            # Start monitoring in separate process
            script_path = Path(__file__).parent / "integrated_electrical_monitor.py"
            
            if not script_path.exists():
                raise FileNotFoundError("Monitoring system not found!")
                
            # Start the monitoring process
            self.monitoring_process = subprocess.Popen([
                sys.executable, str(script_path)
            ], stdout=subprocess.PIPE, stderr=subprocess.PIPE)
            
            self.system_running = True
            self.status_var.set("Monitoring system running")
            self.start_button.config(state='disabled')
            self.stop_button.config(state='normal')
            
            # Start monitoring the process
            self.monitor_process()
            
            logger.info("Monitoring system started successfully")
            
        except Exception as e:
            logger.error(f"Failed to start monitoring system: {e}")
            self.status_var.set("Failed to start system")
            self.start_button.config(state='normal')
            messagebox.showerror("Startup Error", f"Failed to start monitoring system:\n{e}")
            
    def stop_monitoring(self):
        """Stop the monitoring system"""
        if not self.system_running:
            return
            
        try:
            self.status_var.set("Stopping monitoring system...")
            
            if self.monitoring_process:
                self.monitoring_process.terminate()
                self.monitoring_process.wait(timeout=5)
                
            self.system_running = False
            self.monitoring_process = None
            self.status_var.set("System stopped")
            self.start_button.config(state='normal')
            self.stop_button.config(state='disabled')
            
            logger.info("Monitoring system stopped")
            
        except Exception as e:
            logger.error(f"Error stopping monitoring system: {e}")
            messagebox.showerror("Stop Error", f"Error stopping system:\n{e}")
            
    def monitor_process(self):
        """Monitor the running process"""
        def check_process():
            while self.system_running and self.monitoring_process:
                if self.monitoring_process.poll() is not None:
                    # Process has terminated
                    self.root.after(0, self.handle_process_exit)
                    break
                time.sleep(1)
                
        threading.Thread(target=check_process, daemon=True).start()
        
    def handle_process_exit(self):
        """Handle monitoring process exit"""
        if self.system_running:
            self.system_running = False
            self.status_var.set("System stopped")
            self.start_button.config(state='normal')
            self.stop_button.config(state='disabled')
            
            # Get error output if available
            if self.monitoring_process:
                try:
                    # Don't show error dialog for normal shutdown
                    return_code = self.monitoring_process.poll()
                    if return_code is not None and return_code != 0:
                        # Only show error for unexpected exits
                        _, stderr = self.monitoring_process.communicate(timeout=1)
                        if stderr:
                            error_msg = stderr.decode('utf-8')
                            if "keyboard interrupt" not in error_msg.lower():
                                logger.error(f"Monitoring process error: {error_msg}")
                except:
                    pass
                    
            logger.info("Monitoring process exited")
            
    def on_closing(self):
        """Handle application close"""
        if self.system_running:
            if messagebox.askokcancel("Quit", "Monitoring system is running. Stop and quit?"):
                self.stop_monitoring()
                self.root.destroy()
        else:
            self.root.destroy()

def main():
    """Main launcher entry point"""
    try:
        # Create launcher
        launcher = NexusOptimLauncher()
        
        # Setup close handler
        launcher.root.protocol("WM_DELETE_WINDOW", launcher.on_closing)
        
        # Start launcher
        launcher.root.mainloop()
        
    except Exception as e:
        logger.error(f"Launcher error: {e}")
        messagebox.showerror("Launcher Error", f"Failed to start launcher:\n{e}")

if __name__ == "__main__":
    main()
