"""
NexusOptim IA - Electrical Monitoring Dashboard
Real-time Power Quality and Safety Monitoring UI

Features:
- Real-time electrical parameter visualization
- Power quality analysis with THD monitoring
- Safety alert system with emergency notifications
- Historical data analysis and trends
- Multi-node network monitoring

Compatible with: main_electrical.c firmware
Target: Energy sector infrastructure monitoring

Copyright (c) 2025 OpenNexus
Licensed under MIT License
"""

import tkinter as tk
from tkinter import ttk, messagebox
import matplotlib.pyplot as plt
from matplotlib.figure import Figure
from matplotlib.backends.backend_tkagg import FigureCanvasTkAgg
from matplotlib.animation import FuncAnimation
import numpy as np
import threading
import queue
import time
import json
import socket
from datetime import datetime, timedelta
from dataclasses import dataclass
from enum import Enum
from typing import List, Dict, Optional

# Data structures matching the firmware
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

class SafetyFlags:
    OVERVOLTAGE = 1 << 0
    UNDERVOLTAGE = 1 << 1
    OVERCURRENT = 1 << 2
    OVERPOWER = 1 << 3
    LOW_PF = 1 << 4
    HIGH_THD = 1 << 5
    FREQ_DEVIATION = 1 << 6
    PHASE_IMBALANCE = 1 << 7

class PowerQualityGrade(Enum):
    A = 0  # Excellent
    B = 1  # Good
    C = 2  # Acceptable
    D = 3  # Poor
    E = 4  # Bad
    F = 5  # Unacceptable

class ElectricalMonitoringUI:
    def __init__(self, root):
        self.root = root
        self.root.title("NexusOptim IA - Electrical Monitoring Dashboard")
        self.root.geometry("1400x900")
        self.root.configure(bg='#1e1e1e')  # Dark theme
        
        # System state
        self.running = True
        self.shutdown_requested = False
        
        # Data storage
        self.data_queue = queue.Queue()
        self.historical_data: List[ElectricalData] = []
        self.max_history_points = 1000
        
        # Real-time data simulation/receiver
        self.simulation_running = True
        self.data_thread = None
        
        # Color scheme
        self.colors = {
            'bg_dark': '#1e1e1e',
            'bg_medium': '#2d2d2d',
            'bg_light': '#3d3d3d',
            'text_primary': '#ffffff',
            'text_secondary': '#cccccc',
            'accent_blue': '#4a9eff',
            'accent_green': '#4ade80',
            'accent_yellow': '#fbbf24',
            'accent_red': '#ef4444',
            'grid_color': '#404040'
        }
        
        self.setup_ui()
        self.start_data_simulation()
        
    def setup_ui(self):
        """Setup the main UI components"""
        # Main container
        main_frame = tk.Frame(self.root, bg=self.colors['bg_dark'])
        main_frame.pack(fill=tk.BOTH, expand=True, padx=10, pady=10)
        
        # Header
        self.create_header(main_frame)
        
        # Content area - split into left and right panels
        content_frame = tk.Frame(main_frame, bg=self.colors['bg_dark'])
        content_frame.pack(fill=tk.BOTH, expand=True, pady=(10, 0))
        
        # Left panel - Real-time metrics
        left_panel = tk.Frame(content_frame, bg=self.colors['bg_medium'], width=350)
        left_panel.pack(side=tk.LEFT, fill=tk.Y, padx=(0, 10))
        left_panel.pack_propagate(False)
        
        # Right panel - Charts and graphs
        right_panel = tk.Frame(content_frame, bg=self.colors['bg_medium'])
        right_panel.pack(side=tk.RIGHT, fill=tk.BOTH, expand=True)
        
        self.create_metrics_panel(left_panel)
        self.create_charts_panel(right_panel)
        
        # Start real-time updates
        self.update_display()
        
    def create_header(self, parent):
        """Create the header with title and status indicators"""
        header_frame = tk.Frame(parent, bg=self.colors['bg_medium'], height=80)
        header_frame.pack(fill=tk.X)
        header_frame.pack_propagate(False)
        
        # Title
        title_label = tk.Label(
            header_frame,
            text="⚡ NexusOptim IA - Electrical Monitoring",
            font=('Arial', 18, 'bold'),
            fg=self.colors['text_primary'],
            bg=self.colors['bg_medium']
        )
        title_label.pack(side=tk.LEFT, padx=20, pady=20)
        
        # Status indicators
        status_frame = tk.Frame(header_frame, bg=self.colors['bg_medium'])
        status_frame.pack(side=tk.RIGHT, padx=20, pady=20)
        
        # Network status
        self.network_status = tk.Label(
            status_frame,
            text="🌐 LoRaWAN: Connected",
            font=('Arial', 12),
            fg=self.colors['accent_green'],
            bg=self.colors['bg_medium']
        )
        self.network_status.pack(anchor=tk.E)
        
        # System status
        self.system_status = tk.Label(
            status_frame,
            text="⚡ System: Normal",
            font=('Arial', 12),
            fg=self.colors['accent_green'],
            bg=self.colors['bg_medium']
        )
        self.system_status.pack(anchor=tk.E)
        
        # Last update
        self.last_update = tk.Label(
            status_frame,
            text="Last Update: --:--:--",
            font=('Arial', 10),
            fg=self.colors['text_secondary'],
            bg=self.colors['bg_medium']
        )
        self.last_update.pack(anchor=tk.E)
        
    def create_metrics_panel(self, parent):
        """Create the left panel with real-time metrics"""
        # Panel title
        title = tk.Label(
            parent,
            text="Real-Time Measurements",
            font=('Arial', 14, 'bold'),
            fg=self.colors['text_primary'],
            bg=self.colors['bg_medium']
        )
        title.pack(pady=(15, 10))
        
        # Metrics container
        metrics_frame = tk.Frame(parent, bg=self.colors['bg_medium'])
        metrics_frame.pack(fill=tk.BOTH, expand=True, padx=15)
        
        # Create metric displays
        self.metric_displays = {}
        
        metrics_config = [
            ("Voltage RMS", "V", "voltage_rms", self.colors['accent_blue']),
            ("Current RMS", "A", "current_rms", self.colors['accent_blue']),
            ("Active Power", "W", "power_active", self.colors['accent_green']),
            ("Power Factor", "", "power_factor", self.colors['accent_yellow']),
            ("Frequency", "Hz", "frequency", self.colors['accent_blue']),
            ("THD Voltage", "%", "thd_voltage", self.colors['accent_yellow']),
            ("THD Current", "%", "thd_current", self.colors['accent_yellow']),
        ]
        
        for i, (label, unit, key, color) in enumerate(metrics_config):
            metric_frame = self.create_metric_display(metrics_frame, label, unit, color)
            metric_frame.pack(fill=tk.X, pady=5)
            
            # Store references to value labels
            value_label = metric_frame.children['!label2']  # Second label (value)
            self.metric_displays[key] = value_label
        
        # Power Quality Grade
        self.create_quality_grade_display(metrics_frame)
        
        # Safety Status
        self.create_safety_status_display(metrics_frame)
        
    def create_metric_display(self, parent, label, unit, color):
        """Create a single metric display widget"""
        frame = tk.Frame(parent, bg=self.colors['bg_light'], relief=tk.RAISED, bd=1)
        
        # Label
        label_widget = tk.Label(
            frame,
            text=label,
            font=('Arial', 10),
            fg=self.colors['text_secondary'],
            bg=self.colors['bg_light']
        )
        label_widget.pack(side=tk.LEFT, padx=10, pady=8)
        
        # Value
        value_text = f"0.00 {unit}".strip()
        value_widget = tk.Label(
            frame,
            text=value_text,
            font=('Arial', 12, 'bold'),
            fg=color,
            bg=self.colors['bg_light']
        )
        value_widget.pack(side=tk.RIGHT, padx=10, pady=8)
        
        return frame
    
    def create_quality_grade_display(self, parent):
        """Create power quality grade display"""
        frame = tk.Frame(parent, bg=self.colors['bg_light'], relief=tk.RAISED, bd=2)
        frame.pack(fill=tk.X, pady=10)
        
        title = tk.Label(
            frame,
            text="Power Quality Grade",
            font=('Arial', 12, 'bold'),
            fg=self.colors['text_primary'],
            bg=self.colors['bg_light']
        )
        title.pack(pady=(10, 5))
        
        self.quality_grade_label = tk.Label(
            frame,
            text="A - Excellent",
            font=('Arial', 16, 'bold'),
            fg=self.colors['accent_green'],
            bg=self.colors['bg_light']
        )
        self.quality_grade_label.pack(pady=(0, 10))
        
    def create_safety_status_display(self, parent):
        """Create safety status indicators"""
        frame = tk.Frame(parent, bg=self.colors['bg_light'], relief=tk.RAISED, bd=2)
        frame.pack(fill=tk.X, pady=10)
        
        title = tk.Label(
            frame,
            text="Safety Status",
            font=('Arial', 12, 'bold'),
            fg=self.colors['text_primary'],
            bg=self.colors['bg_light']
        )
        title.pack(pady=(10, 5))
        
        # Safety indicators container
        indicators_frame = tk.Frame(frame, bg=self.colors['bg_light'])
        indicators_frame.pack(fill=tk.X, padx=10, pady=(0, 10))
        
        self.safety_indicators = {}
        safety_items = [
            ("Voltage", "voltage_ok"),
            ("Current", "current_ok"),
            ("Power", "power_ok"),
            ("Frequency", "freq_ok")
        ]
        
        for i, (name, key) in enumerate(safety_items):
            row = i // 2
            col = i % 2
            
            indicator = tk.Label(
                indicators_frame,
                text=f"🟢 {name} OK",
                font=('Arial', 9),
                fg=self.colors['accent_green'],
                bg=self.colors['bg_light']
            )
            indicator.grid(row=row, column=col, sticky=tk.W, padx=5, pady=2)
            
            self.safety_indicators[key] = indicator
            
    def create_charts_panel(self, parent):
        """Create the right panel with charts and graphs"""
        # Create notebook for multiple tabs
        notebook = ttk.Notebook(parent)
        notebook.pack(fill=tk.BOTH, expand=True, padx=10, pady=10)
        
        # Configure notebook style
        style = ttk.Style()
        style.theme_use('clam')
        style.configure('TNotebook', background=self.colors['bg_medium'])
        style.configure('TNotebook.Tab', background=self.colors['bg_light'])
        
        # Real-time charts tab
        realtime_frame = tk.Frame(notebook, bg=self.colors['bg_medium'])
        notebook.add(realtime_frame, text="Real-time Monitoring")
        
        # Historical analysis tab
        history_frame = tk.Frame(notebook, bg=self.colors['bg_medium'])
        notebook.add(history_frame, text="Historical Analysis")
        
        # Power quality tab
        quality_frame = tk.Frame(notebook, bg=self.colors['bg_medium'])
        notebook.add(quality_frame, text="Power Quality")
        
        self.create_realtime_charts(realtime_frame)
        self.create_historical_charts(history_frame)
        self.create_quality_charts(quality_frame)
        
    def create_realtime_charts(self, parent):
        """Create real-time monitoring charts"""
        # Create matplotlib figure
        self.fig_realtime = Figure(figsize=(12, 8), facecolor=self.colors['bg_medium'])
        
        # Create subplots
        gs = self.fig_realtime.add_gridspec(3, 2, hspace=0.3, wspace=0.3)
        
        self.ax_voltage = self.fig_realtime.add_subplot(gs[0, 0])
        self.ax_current = self.fig_realtime.add_subplot(gs[0, 1])
        self.ax_power = self.fig_realtime.add_subplot(gs[1, 0])
        self.ax_pf = self.fig_realtime.add_subplot(gs[1, 1])
        self.ax_freq = self.fig_realtime.add_subplot(gs[2, 0])
        self.ax_thd = self.fig_realtime.add_subplot(gs[2, 1])
        
        # Configure subplot styles
        axes = [self.ax_voltage, self.ax_current, self.ax_power, 
                self.ax_pf, self.ax_freq, self.ax_thd]
        
        titles = ["Voltage RMS (V)", "Current RMS (A)", "Active Power (W)",
                 "Power Factor", "Frequency (Hz)", "THD (%)"]
        
        for ax, title in zip(axes, titles):
            ax.set_title(title, color=self.colors['text_primary'], fontsize=10, fontweight='bold')
            ax.set_facecolor(self.colors['bg_dark'])
            ax.tick_params(colors=self.colors['text_secondary'], labelsize=8)
            ax.grid(True, color=self.colors['grid_color'], alpha=0.3)
            ax.spines['bottom'].set_color(self.colors['grid_color'])
            ax.spines['top'].set_color(self.colors['grid_color'])
            ax.spines['right'].set_color(self.colors['grid_color'])
            ax.spines['left'].set_color(self.colors['grid_color'])
        
        # Initialize data arrays for real-time plotting
        self.time_data = []
        self.voltage_data = []
        self.current_data = []
        self.power_data = []
        self.pf_data = []
        self.freq_data = []
        self.thd_v_data = []
        self.thd_c_data = []
        
        # Create canvas
        self.canvas_realtime = FigureCanvasTkAgg(self.fig_realtime, parent)
        self.canvas_realtime.draw()
        self.canvas_realtime.get_tk_widget().pack(fill=tk.BOTH, expand=True)
        
    def create_historical_charts(self, parent):
        """Create historical analysis charts"""
        # Placeholder for historical analysis
        label = tk.Label(
            parent,
            text="Historical Analysis\n(24-hour trends, weekly patterns, etc.)",
            font=('Arial', 14),
            fg=self.colors['text_secondary'],
            bg=self.colors['bg_medium']
        )
        label.pack(expand=True)
        
    def create_quality_charts(self, parent):
        """Create power quality analysis charts"""
        # Placeholder for power quality analysis
        label = tk.Label(
            parent,
            text="Power Quality Analysis\n(Harmonic analysis, THD trends, etc.)",
            font=('Arial', 14),
            fg=self.colors['text_secondary'],
            bg=self.colors['bg_medium']
        )
        label.pack(expand=True)
        
    def start_data_simulation(self):
        """Start the data simulation/reception thread"""
        self.data_thread = threading.Thread(target=self.data_simulation_worker, daemon=True)
        self.data_thread.start()
        
    def data_simulation_worker(self):
        """Simulate real-time electrical data (replace with actual LoRaWAN receiver)"""
        base_time = time.time()
        
        while self.simulation_running:
            # Simulate realistic electrical data
            current_time = time.time()
            elapsed = current_time - base_time
            
            # Base values with some realistic variation
            voltage_base = 230.0  # 230V nominal
            current_base = 10.0   # 10A nominal
            
            # Add realistic variations and occasional anomalies
            voltage_noise = np.random.normal(0, 2.0)  # ±2V noise
            current_noise = np.random.normal(0, 0.5)  # ±0.5A noise
            
            # Simulate some harmonics and power quality issues
            thd_v = 2.0 + np.random.exponential(1.0)  # THD typically 2-5%
            thd_c = 3.0 + np.random.exponential(1.5)  # Current THD usually higher
            
            # Frequency variation (50Hz ±0.2Hz)
            freq_variation = np.random.normal(0, 0.1)
            
            # Create simulated data
            data = ElectricalData(
                timestamp=current_time,
                voltage_rms=max(0, voltage_base + voltage_noise),
                current_rms=max(0, current_base + current_noise),
                power_active=(voltage_base + voltage_noise) * (current_base + current_noise) * 0.95,  # PF=0.95
                power_reactive=0,
                power_apparent=0,
                power_factor=0.95 + np.random.normal(0, 0.02),
                frequency=50.0 + freq_variation,
                thd_voltage=max(0.1, thd_v),
                thd_current=max(0.1, thd_c),
                safety_status=0,  # No alerts in simulation
                quality_grade=0,  # A grade
                node_id=1
            )
            
            # Calculate derived values
            data.power_apparent = np.sqrt(data.power_active**2 + data.power_reactive**2)
            if data.power_apparent > 0:
                data.power_factor = data.power_active / data.power_apparent
            
            # Add to queue
            self.data_queue.put(data)
            
            time.sleep(1.0)  # Update every second
            
    def update_display(self):
        """Update all UI components with latest data"""
        # Check if system is still running
        if not self.running or self.shutdown_requested:
            return
            
        try:
            # Process new data from queue
            new_data_available = False
            while not self.data_queue.empty():
                try:
                    data = self.data_queue.get_nowait()
                    self.historical_data.append(data)
                    new_data_available = True
                    
                    # Limit historical data size
                    if len(self.historical_data) > self.max_history_points:
                        self.historical_data.pop(0)
                        
                except queue.Empty:
                    break
            
            # Update displays if new data is available
            if new_data_available and self.historical_data:
                latest_data = self.historical_data[-1]
                self.update_metrics_display(latest_data)
                self.update_charts()
                self.update_status_indicators(latest_data)
            
            # Schedule next update only if still running
            if self.running and not self.shutdown_requested:
                self.root.after(1000, self.update_display)  # Update every second
                
        except Exception as e:
            # Handle any errors gracefully
            if self.running:
                print(f"Error in update_display: {e}")
                # Try to continue updates
                self.root.after(1000, self.update_display)
        
    def update_metrics_display(self, data: ElectricalData):
        """Update the metrics panel with latest data"""
        updates = {
            'voltage_rms': f"{data.voltage_rms:.2f} V",
            'current_rms': f"{data.current_rms:.2f} A",
            'power_active': f"{data.power_active:.1f} W",
            'power_factor': f"{data.power_factor:.3f}",
            'frequency': f"{data.frequency:.2f} Hz",
            'thd_voltage': f"{data.thd_voltage:.1f} %",
            'thd_current': f"{data.thd_current:.1f} %"
        }
        
        for key, value in updates.items():
            if key in self.metric_displays:
                self.metric_displays[key].config(text=value)
        
        # Update power quality grade
        grade_names = ["A - Excellent", "B - Good", "C - Acceptable", 
                      "D - Poor", "E - Bad", "F - Unacceptable"]
        grade_colors = [self.colors['accent_green'], self.colors['accent_green'],
                       self.colors['accent_yellow'], self.colors['accent_yellow'],
                       self.colors['accent_red'], self.colors['accent_red']]
        
        grade_idx = min(data.quality_grade, 5)
        self.quality_grade_label.config(
            text=grade_names[grade_idx],
            fg=grade_colors[grade_idx]
        )
        
    def update_charts(self):
        """Update real-time charts with latest data"""
        if len(self.historical_data) < 2:
            return
            
        # Get recent data for plotting (last 60 points = 1 minute)
        recent_data = self.historical_data[-60:]
        
        # Extract data arrays
        times = [(d.timestamp - recent_data[0].timestamp) for d in recent_data]
        voltages = [d.voltage_rms for d in recent_data]
        currents = [d.current_rms for d in recent_data]
        powers = [d.power_active for d in recent_data]
        power_factors = [d.power_factor for d in recent_data]
        frequencies = [d.frequency for d in recent_data]
        thd_voltages = [d.thd_voltage for d in recent_data]
        thd_currents = [d.thd_current for d in recent_data]
        
        # Clear and update plots
        self.ax_voltage.clear()
        self.ax_voltage.plot(times, voltages, color=self.colors['accent_blue'], linewidth=2)
        self.ax_voltage.set_title("Voltage RMS (V)", color=self.colors['text_primary'], fontweight='bold')
        self.ax_voltage.set_facecolor(self.colors['bg_dark'])
        self.ax_voltage.grid(True, color=self.colors['grid_color'], alpha=0.3)
        
        self.ax_current.clear()
        self.ax_current.plot(times, currents, color=self.colors['accent_green'], linewidth=2)
        self.ax_current.set_title("Current RMS (A)", color=self.colors['text_primary'], fontweight='bold')
        self.ax_current.set_facecolor(self.colors['bg_dark'])
        self.ax_current.grid(True, color=self.colors['grid_color'], alpha=0.3)
        
        self.ax_power.clear()
        self.ax_power.plot(times, powers, color=self.colors['accent_yellow'], linewidth=2)
        self.ax_power.set_title("Active Power (W)", color=self.colors['text_primary'], fontweight='bold')
        self.ax_power.set_facecolor(self.colors['bg_dark'])
        self.ax_power.grid(True, color=self.colors['grid_color'], alpha=0.3)
        
        self.ax_pf.clear()
        self.ax_pf.plot(times, power_factors, color=self.colors['accent_blue'], linewidth=2)
        self.ax_pf.set_title("Power Factor", color=self.colors['text_primary'], fontweight='bold')
        self.ax_pf.set_facecolor(self.colors['bg_dark'])
        self.ax_pf.grid(True, color=self.colors['grid_color'], alpha=0.3)
        self.ax_pf.axhline(y=0.85, color=self.colors['accent_red'], linestyle='--', alpha=0.7)  # Warning line
        
        self.ax_freq.clear()
        self.ax_freq.plot(times, frequencies, color=self.colors['accent_green'], linewidth=2)
        self.ax_freq.set_title("Frequency (Hz)", color=self.colors['text_primary'], fontweight='bold')
        self.ax_freq.set_facecolor(self.colors['bg_dark'])
        self.ax_freq.grid(True, color=self.colors['grid_color'], alpha=0.3)
        self.ax_freq.axhline(y=50.0, color=self.colors['accent_blue'], linestyle='--', alpha=0.5)  # Nominal line
        
        self.ax_thd.clear()
        self.ax_thd.plot(times, thd_voltages, color=self.colors['accent_yellow'], linewidth=2, label='THD-V')
        self.ax_thd.plot(times, thd_currents, color=self.colors['accent_red'], linewidth=2, label='THD-I')
        self.ax_thd.set_title("THD (%)", color=self.colors['text_primary'], fontweight='bold')
        self.ax_thd.set_facecolor(self.colors['bg_dark'])
        self.ax_thd.grid(True, color=self.colors['grid_color'], alpha=0.3)
        self.ax_thd.axhline(y=5.0, color=self.colors['accent_red'], linestyle='--', alpha=0.7)  # Warning line
        self.ax_thd.legend(facecolor=self.colors['bg_light'], edgecolor=self.colors['grid_color'])
        
        # Apply common styling to all axes
        for ax in [self.ax_voltage, self.ax_current, self.ax_power, self.ax_pf, self.ax_freq, self.ax_thd]:
            ax.tick_params(colors=self.colors['text_secondary'], labelsize=8)
            ax.set_xlabel("Time (s)", color=self.colors['text_secondary'])
            for spine in ax.spines.values():
                spine.set_color(self.colors['grid_color'])
        
        self.canvas_realtime.draw()
        
    def update_status_indicators(self, data: ElectricalData):
        """Update status indicators in header and safety panel"""
        # Update last update time
        current_time = datetime.now().strftime("%H:%M:%S")
        self.last_update.config(text=f"Last Update: {current_time}")
        
        # Update safety indicators based on data
        safety_status = {
            'voltage_ok': 210 <= data.voltage_rms <= 250,  # ±10V tolerance for 230V
            'current_ok': data.current_rms < 15.0,         # Current limit
            'power_ok': data.power_active < 3000,          # Power limit
            'freq_ok': 49.5 <= data.frequency <= 50.5     # Frequency tolerance
        }
        
        for key, is_ok in safety_status.items():
            if key in self.safety_indicators:
                if is_ok:
                    self.safety_indicators[key].config(
                        text=f"🟢 {key.replace('_ok', '').title()} OK",
                        fg=self.colors['accent_green']
                    )
                else:
                    self.safety_indicators[key].config(
                        text=f"🔴 {key.replace('_ok', '').title()} Alert",
                        fg=self.colors['accent_red']
                    )
        
        # Update system status
        any_alert = not all(safety_status.values())
        if any_alert:
            self.system_status.config(
                text="⚠️  System: Alert",
                fg=self.colors['accent_red']
            )
        else:
            self.system_status.config(
                text="⚡ System: Normal",
                fg=self.colors['accent_green']
            )
    
    def on_closing(self):
        """Handle application closing"""
        self.simulation_running = False
        if self.data_thread:
            self.data_thread.join(timeout=1.0)
        self.root.destroy()

def main():
    """Main application entry point"""
    root = tk.Tk()
    app = ElectricalMonitoringUI(root)
    
    # Handle window closing
    root.protocol("WM_DELETE_WINDOW", app.on_closing)
    
    # Start the application
    root.mainloop()

if __name__ == "__main__":
    main()
