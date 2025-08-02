"""
NexusOptim IA - Emergency Configurator
Simple dialog-based configuration
"""

import tkinter as tk
from tkinter import messagebox
import json
import os

def emergency_config():
    """Emergency configuration using message boxes"""
    root = tk.Tk()
    root.withdraw()  # Hide main window
    
    # Show configuration dialog
    result = messagebox.askyesnocancel(
        "⚡ NexusOptim IA - Configuración",
        "🟢 SÍ = Operación Normal (Recomendado)\n"
        "   • Grid estable Costa Rica\n"
        "   • Sin alertas molestas\n"
        "   • Voltaje 230V estable\n\n"
        "🇨🇷 NO = Condiciones Reales CR\n"
        "   • Datos del ICE\n"
        "   • Alertas ocasionales\n\n"
        "❌ CANCELAR = No cambiar nada"
    )
    
    if result is None:  # Cancel
        messagebox.showinfo("Cancelado", "No se realizaron cambios")
        return False
    
    # Create configuration
    if result:  # Yes - Normal
        config = {
            "scenario": "normal",
            "alert_frequency": "very_low",
            "parameters": {
                "voltage_base": 230.0,
                "voltage_variation": 1.0,
                "current_base": 10.0,
                "current_variation": 0.5,
                "frequency_base": 50.0,
                "frequency_variation": 0.02,
                "thd_base": 1.5,
                "alert_probability": 0.005,  # Casi nada
                "active_nodes": 1
            }
        }
        scenario_name = "Operación Normal"
    else:  # No - Costa Rica
        config = {
            "scenario": "costa_rica",
            "alert_frequency": "low",
            "parameters": {
                "voltage_base": 230.0,
                "voltage_variation": 2.5,
                "current_base": 12.0,
                "current_variation": 1.5,
                "frequency_base": 50.0,
                "frequency_variation": 0.06,
                "thd_base": 3.0,
                "alert_probability": 0.02,
                "active_nodes": 1
            }
        }
        scenario_name = "Condiciones Costa Rica"
    
    # Save configuration
    try:
        with open("simulation_config.json", "w") as f:
            json.dump(config, f, indent=4)
        
        messagebox.showinfo(
            "✅ Configuración Aplicada",
            f"Escenario: {scenario_name}\n\n"
            f"✅ Configuración guardada correctamente\n"
            f"⚡ Alertas reducidas al mínimo\n"
            f"🇨🇷 Parámetros optimizados para Costa Rica\n\n"
            f"🚀 Reinicia el sistema de monitoreo\n"
            f"    para aplicar los cambios"
        )
        return True
        
    except Exception as e:
        messagebox.showerror("Error", f"No se pudo guardar:\n{e}")
        return False
    
    finally:
        root.destroy()

if __name__ == "__main__":
    emergency_config()
