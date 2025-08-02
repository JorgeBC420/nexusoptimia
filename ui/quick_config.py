"""
NexusOptim IA - Quick Scenario Setup
Simple configuration for electrical monitoring scenarios
"""

import tkinter as tk
from tkinter import ttk, messagebox
import json
import os

def create_config(scenario_type="normal"):
    """Create configuration file directly"""
    configs = {
        "normal": {
            "scenario": "normal",
            "alert_frequency": "low", 
            "parameters": {
                "voltage_base": 230.0,
                "voltage_variation": 2.0,
                "current_base": 10.0,
                "current_variation": 1.0,
                "frequency_base": 50.0,
                "frequency_variation": 0.05,
                "thd_base": 2.0,
                "alert_probability": 0.02,  # Very low alerts
                "active_nodes": 1
            }
        },
        "costa_rica": {
            "scenario": "costa_rica",
            "alert_frequency": "low",
            "parameters": {
                "voltage_base": 230.0,
                "voltage_variation": 3.0,
                "current_base": 12.0,
                "current_variation": 2.0,
                "frequency_base": 50.0,
                "frequency_variation": 0.08,
                "thd_base": 3.5,
                "alert_probability": 0.03,  # Realistic for CR
                "active_nodes": 1
            }
        }
    }
    
    config = configs.get(scenario_type, configs["normal"])
    
    try:
        with open("simulation_config.json", "w") as f:
            json.dump(config, f, indent=4)
        return True
    except Exception as e:
        print(f"Error saving config: {e}")
        return False

class QuickConfig:
    def __init__(self):
        self.root = tk.Tk()
        self.root.title("NexusOptim IA - Configuración Rápida")
        self.root.geometry("450x450")  # Más alto para mostrar botones
        self.root.resizable(False, False)
        
        # Center window
        self.root.geometry("+{}+{}".format(
            int(self.root.winfo_screenwidth()/2 - 225),
            int(self.root.winfo_screenheight()/2 - 225)
        ))
        
        # Dark theme
        self.root.configure(bg='#2b2b2b')
        
        self.setup_ui()
        
    def setup_ui(self):
        # Main frame with scrollbar
        canvas = tk.Canvas(self.root, bg='#2b2b2b', highlightthickness=0)
        scrollbar = tk.Scrollbar(self.root, orient="vertical", command=canvas.yview)
        scrollable_frame = tk.Frame(canvas, bg='#2b2b2b')
        
        scrollable_frame.bind(
            "<Configure>",
            lambda e: canvas.configure(scrollregion=canvas.bbox("all"))
        )
        
        canvas.create_window((0, 0), window=scrollable_frame, anchor="nw")
        canvas.configure(yscrollcommand=scrollbar.set)
        
        main_frame = tk.Frame(scrollable_frame, padx=30, pady=30, bg='#2b2b2b')
        main_frame.pack(fill='both', expand=True)
        
        # Title
        title_label = tk.Label(main_frame, text="CONFIGURACIÓN DE ESCENARIOS", 
                              font=('Arial', 16, 'bold'), 
                              fg='white', bg='#2b2b2b')
        title_label.pack(pady=(0, 20))
        
        # Info
        info_label = tk.Label(main_frame, 
                             text="Selecciona el tipo de simulación para el monitoreo eléctrico:",
                             font=('Arial', 11), wraplength=350,
                             fg='#cccccc', bg='#2b2b2b')
        info_label.pack(pady=(0, 30))
        
        # Scenario selection
        self.scenario_var = tk.StringVar(value="normal")
        
        # Normal operation
        normal_frame = tk.Frame(main_frame, bg='#2b2b2b')
        normal_frame.pack(fill='x', pady=10)
        
        tk.Radiobutton(normal_frame, text="🟢 Operación Normal (Recomendado)", 
                      variable=self.scenario_var, value="normal",
                      font=('Arial', 12, 'bold'),
                      fg='#4CAF50', bg='#2b2b2b',
                      selectcolor='#2b2b2b').pack(anchor='w')
        
        tk.Label(normal_frame, text="• Grid estable de Costa Rica\n• Alertas mínimas (1%)\n• Voltaje: 230V ±1.5V", 
                font=('Arial', 10), fg='#888888', bg='#2b2b2b').pack(anchor='w', padx=25)
        
        # Costa Rica realistic
        cr_frame = tk.Frame(main_frame, bg='#2b2b2b')
        cr_frame.pack(fill='x', pady=10)
        
        tk.Radiobutton(cr_frame, text="🇨🇷 Condiciones Reales Costa Rica", 
                      variable=self.scenario_var, value="costa_rica",
                      font=('Arial', 12),
                      fg='#FFC107', bg='#2b2b2b',
                      selectcolor='#2b2b2b').pack(anchor='w')
        
        tk.Label(cr_frame, text="• Basado en datos del ICE\n• Alertas ocasionales (2%)\n• Variaciones típicas del país", 
                font=('Arial', 10), fg='#888888', bg='#2b2b2b').pack(anchor='w', padx=25)
        
        # Separator
        separator = tk.Frame(main_frame, height=2, bg='#444444')
        separator.pack(fill='x', pady=20)
        
        # Buttons - FORZAR VISIBILIDAD
        button_frame = tk.Frame(main_frame, bg='#2b2b2b')
        button_frame.pack(pady=40, fill='x')
        
        # Apply button - MUY VISIBLE
        apply_btn = tk.Button(button_frame, 
                             text="✅ APLICAR CONFIGURACIÓN", 
                             command=self.apply_config,
                             font=('Arial', 14, 'bold'),
                             bg='#4CAF50', fg='white',
                             padx=30, pady=15,
                             relief='raised', borderwidth=3)
        apply_btn.pack(pady=10)
        
        # Cancel button
        cancel_btn = tk.Button(button_frame, 
                              text="❌ CANCELAR", 
                              command=self.cancel,
                              font=('Arial', 12),
                              bg='#f44336', fg='white',
                              padx=25, pady=10,
                              relief='raised', borderwidth=2)
        cancel_btn.pack(pady=5)
        
        # Status
        self.status_label = tk.Label(main_frame, text="Listo para configurar", 
                                    font=('Arial', 11),
                                    fg='#cccccc', bg='#2b2b2b')
        self.status_label.pack(pady=20)
        
        # Pack canvas and scrollbar
        canvas.pack(side="left", fill="both", expand=True)
        scrollbar.pack(side="right", fill="y")
        
    def apply_config(self):
        """Apply the selected configuration"""
        scenario = self.scenario_var.get()
        
        self.status_label.config(text="Aplicando configuración...", fg='blue')
        self.root.update()
        
        if create_config(scenario):
            scenario_names = {
                "normal": "Operación Normal",
                "costa_rica": "Condiciones Costa Rica"
            }
            
            messagebox.showinfo("✅ Configuración Aplicada", 
                               f"Escenario: {scenario_names[scenario]}\n\n"
                               f"✅ Alertas reducidas al mínimo\n"
                               f"✅ Valores realistas para Costa Rica\n"
                               f"✅ Configuración guardada\n\n"
                               f"Reinicia el sistema de monitoreo para aplicar los cambios.")
            self.root.destroy()
        else:
            messagebox.showerror("❌ Error", "No se pudo guardar la configuración")
            self.status_label.config(text="Error al guardar", fg='red')
            
    def cancel(self):
        """Cancel and close"""
        self.root.destroy()

def main():
    """Run quick configurator"""
    try:
        app = QuickConfig()
        app.root.mainloop()
    except Exception as e:
        print(f"Error: {e}")
        # Fallback: create normal config directly
        if create_config("normal"):
            print("✅ Configuración normal aplicada automáticamente")
        else:
            print("❌ Error creando configuración")

if __name__ == "__main__":
    main()
