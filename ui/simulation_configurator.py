"""
NexusOptim IA - Simulation Scenario Configurator
Configure different electrical monitoring scenarios

Scenarios available:
1. Normal Operation - Stable electrical grid
2. High Load - Industrial peak consumption
3. Power Quality Issues - THD and voltage problems
4. Grid Instability - Frequency and voltage variations
5. Costa Rica Real Conditions - Based on actual grid data

Copyright (c) 2025 OpenNexus
Licensed under MIT License
"""

import tkinter as tk
from tkinter import ttk, messagebox
import json
import os

class SimulationConfigurator:
    """Configure simulation scenarios for electrical monitoring"""
    
    def __init__(self, parent=None):
        self.window = tk.Toplevel(parent) if parent else tk.Tk()
        self.window.title("NexusOptim IA - Configurador de Escenarios")
        self.window.geometry("500x600")
        self.window.resizable(False, False)
        
        self.config_file = "simulation_config.json"
        self.setup_ui()
        self.load_config()
        
    def setup_ui(self):
        """Setup the configuration UI"""
        # Main frame
        main_frame = ttk.Frame(self.window, padding="20")
        main_frame.grid(row=0, column=0, sticky=(tk.W, tk.E, tk.N, tk.S))
        
        # Title
        title_label = ttk.Label(main_frame, text="CONFIGURADOR DE ESCENARIOS", 
                               font=('Arial', 16, 'bold'))
        title_label.grid(row=0, column=0, columnspan=2, pady=(0, 20))
        
        # Scenario selection
        scenario_frame = ttk.LabelFrame(main_frame, text="Escenario de Simulación", padding="10")
        scenario_frame.grid(row=1, column=0, columnspan=2, sticky=(tk.W, tk.E), pady=(0, 20))
        
        self.scenario_var = tk.StringVar(value="normal")
        
        scenarios = [
            ("normal", "🟢 Operación Normal", "Grid estable, sin alertas"),
            ("high_load", "🟡 Alta Carga", "Consumo industrial alto"),
            ("power_quality", "🟠 Problemas de Calidad", "THD alto, voltaje irregular"),
            ("grid_instability", "🔴 Inestabilidad de Red", "Frecuencia y voltaje variables"),
            ("costa_rica", "🇨🇷 Condiciones Costa Rica", "Basado en datos reales del ICE")
        ]
        
        for i, (value, title, desc) in enumerate(scenarios):
            radio = ttk.Radiobutton(scenario_frame, text=title, 
                                   variable=self.scenario_var, value=value)
            radio.grid(row=i, column=0, sticky=tk.W, pady=2)
            
            desc_label = ttk.Label(scenario_frame, text=desc, 
                                  font=('Arial', 8), foreground='gray')
            desc_label.grid(row=i, column=1, sticky=tk.W, padx=(20, 0))
        
        # Alert frequency
        alert_frame = ttk.LabelFrame(main_frame, text="Frecuencia de Alertas", padding="10")
        alert_frame.grid(row=2, column=0, columnspan=2, sticky=(tk.W, tk.E), pady=(0, 20))
        
        self.alert_freq_var = tk.StringVar(value="low")
        
        alert_options = [
            ("none", "Sin Alertas", "Solo operación normal"),
            ("low", "Alertas Bajas (5%)", "Ocasionales problemas menores"),
            ("medium", "Alertas Moderadas (15%)", "Problemas regulares"),
            ("high", "Alertas Altas (30%)", "Grid con problemas frecuentes")
        ]
        
        for i, (value, title, desc) in enumerate(alert_options):
            radio = ttk.Radiobutton(alert_frame, text=title, 
                                   variable=self.alert_freq_var, value=value)
            radio.grid(row=i, column=0, sticky=tk.W, pady=2)
            
            desc_label = ttk.Label(alert_frame, text=desc, 
                                  font=('Arial', 8), foreground='gray')
            desc_label.grid(row=i, column=1, sticky=tk.W, padx=(20, 0))
        
        # Node configuration
        node_frame = ttk.LabelFrame(main_frame, text="Configuración de Nodos", padding="10")
        node_frame.grid(row=3, column=0, columnspan=2, sticky=(tk.W, tk.E), pady=(0, 20))
        
        ttk.Label(node_frame, text="Número de Nodos Activos:").grid(row=0, column=0, sticky=tk.W)
        self.nodes_var = tk.IntVar(value=1)
        nodes_spin = ttk.Spinbox(node_frame, from_=1, to=10, textvariable=self.nodes_var, width=10)
        nodes_spin.grid(row=0, column=1, padx=(10, 0))
        
        # Grid parameters
        params_frame = ttk.LabelFrame(main_frame, text="Parámetros del Grid", padding="10")
        params_frame.grid(row=4, column=0, columnspan=2, sticky=(tk.W, tk.E), pady=(0, 20))
        
        # Voltage range
        ttk.Label(params_frame, text="Voltaje Base (V):").grid(row=0, column=0, sticky=tk.W)
        self.voltage_var = tk.DoubleVar(value=230.0)
        voltage_spin = ttk.Spinbox(params_frame, from_=200, to=250, 
                                  textvariable=self.voltage_var, width=10, increment=5)
        voltage_spin.grid(row=0, column=1, padx=(10, 0))
        
        # Current range
        ttk.Label(params_frame, text="Corriente Base (A):").grid(row=1, column=0, sticky=tk.W)
        self.current_var = tk.DoubleVar(value=10.0)
        current_spin = ttk.Spinbox(params_frame, from_=1, to=20, 
                                  textvariable=self.current_var, width=10, increment=1)
        current_spin.grid(row=1, column=1, padx=(10, 0))
        
        # Frequency
        ttk.Label(params_frame, text="Frecuencia (Hz):").grid(row=2, column=0, sticky=tk.W)
        self.frequency_var = tk.DoubleVar(value=50.0)
        freq_spin = ttk.Spinbox(params_frame, from_=49.5, to=50.5, 
                               textvariable=self.frequency_var, width=10, increment=0.1)
        freq_spin.grid(row=2, column=1, padx=(10, 0))
        
        # Buttons
        button_frame = ttk.Frame(main_frame)
        button_frame.grid(row=5, column=0, columnspan=2, pady=(20, 0))
        
        apply_button = ttk.Button(button_frame, text="Aplicar Configuración", 
                                 command=self.apply_config, width=20)
        apply_button.grid(row=0, column=0, padx=(0, 10))
        
        reset_button = ttk.Button(button_frame, text="Restaurar Defaults", 
                                 command=self.reset_config, width=20)
        reset_button.grid(row=0, column=1, padx=(10, 0))
        
        close_button = ttk.Button(button_frame, text="Cerrar", 
                                 command=self.close_window, width=15)
        close_button.grid(row=0, column=2, padx=(10, 0))
        
        # Info panel
        info_frame = ttk.LabelFrame(main_frame, text="Información", padding="10")
        info_frame.grid(row=6, column=0, columnspan=2, sticky=(tk.W, tk.E), pady=(20, 0))
        
        info_text = """Esta configuración controla la simulación del monitoreo eléctrico.
        
🟢 Normal: Grid estable de Costa Rica
🟡 Alta Carga: Simulación de demanda industrial
🟠 Calidad: Problemas de THD y regulación
🔴 Inestabilidad: Variaciones de frecuencia
🇨🇷 Costa Rica: Datos reales del ICE"""
        
        info_label = ttk.Label(info_frame, text=info_text, justify=tk.LEFT, 
                              font=('Arial', 8))
        info_label.grid(row=0, column=0, sticky=tk.W)
        
    def get_scenario_config(self, scenario):
        """Get configuration for a specific scenario"""
        configs = {
            "normal": {
                "voltage_base": 230.0,
                "voltage_variation": 2.0,
                "current_base": 10.0,
                "current_variation": 1.0,
                "frequency_base": 50.0,
                "frequency_variation": 0.05,
                "thd_base": 2.0,
                "alert_probability": 0.02
            },
            "high_load": {
                "voltage_base": 225.0,  # Slightly lower due to load
                "voltage_variation": 5.0,
                "current_base": 15.0,   # Higher current
                "current_variation": 3.0,
                "frequency_base": 49.95,
                "frequency_variation": 0.1,
                "thd_base": 4.0,        # Higher THD
                "alert_probability": 0.1
            },
            "power_quality": {
                "voltage_base": 235.0,
                "voltage_variation": 8.0,  # High voltage variation
                "current_base": 12.0,
                "current_variation": 4.0,
                "frequency_base": 50.0,
                "frequency_variation": 0.15,
                "thd_base": 6.0,        # High THD issues
                "alert_probability": 0.2
            },
            "grid_instability": {
                "voltage_base": 228.0,
                "voltage_variation": 12.0,  # Very unstable
                "current_base": 11.0,
                "current_variation": 5.0,
                "frequency_base": 49.9,
                "frequency_variation": 0.3,  # High frequency variation
                "thd_base": 5.0,
                "alert_probability": 0.25
            },
            "costa_rica": {
                "voltage_base": 230.0,  # ICE standard
                "voltage_variation": 3.0,
                "current_base": 12.0,   # Typical residential
                "current_variation": 2.0,
                "frequency_base": 50.0, # ICE maintains 50Hz
                "frequency_variation": 0.08,
                "thd_base": 3.5,        # Real grid conditions
                "alert_probability": 0.08
            }
        }
        return configs.get(scenario, configs["normal"])
        
    def apply_config(self):
        """Apply the selected configuration"""
        try:
            # Get scenario config
            scenario_config = self.get_scenario_config(self.scenario_var.get())
            
            # Override with user values
            scenario_config.update({
                "voltage_base": self.voltage_var.get(),
                "current_base": self.current_var.get(),
                "frequency_base": self.frequency_var.get(),
                "active_nodes": self.nodes_var.get()
            })
            
            # Set alert frequency
            alert_probs = {
                "none": 0.0,
                "low": 0.05,
                "medium": 0.15,
                "high": 0.3
            }
            scenario_config["alert_probability"] = alert_probs[self.alert_freq_var.get()]
            
            # Save configuration
            config = {
                "scenario": self.scenario_var.get(),
                "alert_frequency": self.alert_freq_var.get(),
                "parameters": scenario_config
            }
            
            self.save_config(config)
            
            messagebox.showinfo("¡Configuración Aplicada!", 
                              f"✅ Escenario: {self.get_scenario_name(self.scenario_var.get())}\n"
                              f"⚠️ Alertas: {self.get_alert_name(self.alert_freq_var.get())}\n"
                              f"🔧 Voltaje: {self.voltage_var.get()}V\n"
                              f"⚡ Corriente: {self.current_var.get()}A\n\n"
                              f"Reinicia el sistema de monitoreo para aplicar los cambios.")
            
        except Exception as e:
            messagebox.showerror("Error", f"Error aplicando configuración:\n{e}")
            
    def get_scenario_name(self, scenario):
        """Get user-friendly scenario name"""
        names = {
            "normal": "Operación Normal",
            "high_load": "Alta Carga Industrial", 
            "power_quality": "Problemas de Calidad",
            "grid_instability": "Inestabilidad de Red",
            "costa_rica": "Condiciones Costa Rica"
        }
        return names.get(scenario, scenario)
        
    def get_alert_name(self, alert_freq):
        """Get user-friendly alert frequency name"""
        names = {
            "none": "Sin Alertas",
            "low": "Alertas Bajas (5%)",
            "medium": "Alertas Moderadas (15%)",
            "high": "Alertas Altas (30%)"
        }
        return names.get(alert_freq, alert_freq)
        
    def close_window(self):
        """Close the configurator window"""
        self.window.destroy()
            
    def reset_config(self):
        """Reset to default configuration"""
        self.scenario_var.set("normal")
        self.alert_freq_var.set("low")
        self.nodes_var.set(1)
        self.voltage_var.set(230.0)
        self.current_var.set(10.0)
        self.frequency_var.set(50.0)
        
    def load_config(self):
        """Load existing configuration"""
        try:
            if os.path.exists(self.config_file):
                with open(self.config_file, 'r') as f:
                    config = json.load(f)
                    
                self.scenario_var.set(config.get("scenario", "normal"))
                self.alert_freq_var.set(config.get("alert_frequency", "low"))
                
                params = config.get("parameters", {})
                self.nodes_var.set(params.get("active_nodes", 1))
                self.voltage_var.set(params.get("voltage_base", 230.0))
                self.current_var.set(params.get("current_base", 10.0))
                self.frequency_var.set(params.get("frequency_base", 50.0))
                
        except Exception as e:
            print(f"Error loading config: {e}")
            
    def save_config(self, config):
        """Save configuration to file"""
        try:
            with open(self.config_file, 'w') as f:
                json.dump(config, f, indent=4)
        except Exception as e:
            raise Exception(f"Error saving config: {e}")

def main():
    """Run the configurator standalone"""
    configurator = SimulationConfigurator()
    configurator.window.mainloop()

if __name__ == "__main__":
    main()
