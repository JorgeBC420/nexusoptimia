import sys
import threading
import importlib.util
import time
from PyQt6.QtCore import QTimer

from PyQt6.QtWidgets import (
    QApplication, QMainWindow, QTabWidget, QVBoxLayout, QHBoxLayout,
    QLabel, QFrame, QPushButton, QGridLayout, QGroupBox, QTextEdit, QTableWidget, QTableWidgetItem, QSizePolicy, QScrollArea, QComboBox, QWidget, QRadioButton, QButtonGroup
)
from PyQt6.QtGui import QFont, QColor, QPalette
from PyQt6.QtCore import Qt

try:
    from matplotlib.backends.backend_qt5agg import FigureCanvasQTAgg as FigureCanvas
except ImportError:
    try:
        from matplotlib.backends.backend_qt6agg import FigureCanvasQTAgg as FigureCanvas
    except ImportError:
        FigureCanvas = None

try:
    import matplotlib.pyplot as plt
except ImportError:
    plt = None

# Importar ICEDataIntegrator dinámicamente
spec = importlib.util.spec_from_file_location("ice_real_data", "src/integrations/ice_real_data.py")
ice_real_data = importlib.util.module_from_spec(spec)
spec.loader.exec_module(ice_real_data)

# --- Listas administrativas de Costa Rica ---
PROVINCIAS = [
    "San José", "Alajuela", "Cartago", "Heredia", "Guanacaste", "Puntarenas", "Limón"
]
CANTONES = {
    "San José": ["San José", "Escazú", "Desamparados", "Puriscal", "Tarrazú", "Aserrí", "Mora", "Goicoechea", "Santa Ana", "Alajuelita", "Vázquez de Coronado", "Acosta", "Tibás", "Moravia", "Montes de Oca", "Turrubares", "Dota", "Curridabat", "Pérez Zeledón", "León Cortés Castro"],
    "Alajuela": ["Alajuela", "San Ramón", "Grecia", "San Mateo", "Atenas", "Naranjo", "Palmares", "Poás", "Orotina", "San Carlos", "Zarcero", "Sarchí", "Upala", "Los Chiles", "Guatuso", "Río Cuarto"],
    "Cartago": ["Cartago", "Paraíso", "La Unión", "Jiménez", "Turrialba", "Alvarado", "Oreamuno", "El Guarco"],
    "Heredia": ["Heredia", "Barva", "Santo Domingo", "Santa Bárbara", "San Rafael", "San Isidro", "Belén", "Flores", "San Pablo", "Sarapiquí"],
    "Guanacaste": ["Liberia", "Nicoya", "Santa Cruz", "Bagaces", "Carrillo", "Cañas", "Abangares", "Tilarán", "Nandayure", "La Cruz", "Hojancha"],
    "Puntarenas": ["Puntarenas", "Esparza", "Buenos Aires", "Montes de Oro", "Osa", "Quepos", "Golfito", "Coto Brus", "Parrita", "Corredores", "Garabito", "Monteverde"],
    "Limón": ["Limón", "Pococí", "Siquirres", "Talamanca", "Matina", "Guácimo"]
}

class Card(QGroupBox):
    def __init__(self, title, value, subtitle=None, color=None):
        super().__init__()
        self.setTitle("")
        layout = QVBoxLayout()
        title_lbl = QLabel(title)
        title_lbl.setFont(QFont("Segoe UI", 10, QFont.Weight.Bold))
        value_lbl = QLabel(str(value))
        value_lbl.setFont(QFont("Segoe UI", 20, QFont.Weight.Bold))
        if color:
            value_lbl.setStyleSheet(f"color: {color};")
        if subtitle:
            subtitle_lbl = QLabel(subtitle)
            subtitle_lbl.setFont(QFont("Segoe UI", 9))
            layout.addWidget(title_lbl)
            layout.addWidget(value_lbl)
            layout.addWidget(subtitle_lbl)
        else:
            layout.addWidget(title_lbl)
            layout.addWidget(value_lbl)
        self.setLayout(layout)
        self.setStyleSheet("QGroupBox { border: 2px solid #222; border-radius: 8px; margin-top: 8px; background: #222; }")


class MainWindow(QMainWindow):
    def show_transport(self):
        self.show_module_tabbed("Transporte Inteligente", "#a259e6", [
            ("Panel Transporte", self.create_transport_tab)
        ])

    def show_agriculture(self):
        self.show_module_tabbed("Agricultura Inteligente", "#2e7d32", [
            ("Panel Agricultura", self.create_agriculture_tab)
        ])

    def create_transport_tab(self):
        tab = QWidget()
        layout = QVBoxLayout()
        layout.addWidget(QLabel("🚗 Panel de Transporte Inteligente (morado)\n[Próximamente: analítica de tráfico, optimización de rutas y semáforos]"))
        tab.setLayout(layout)
        tab.setStyleSheet("background: #f3e6fd; color: #111;")
        return tab

    def create_agriculture_tab(self):
        tab = QWidget()
        layout = QVBoxLayout()
        layout.addWidget(QLabel("🌱 Panel de Agricultura Inteligente (verde oscuro)\n[Próximamente: monitoreo de cultivos, predicción de riego y alertas de plagas]"))
        tab.setLayout(layout)
        tab.setStyleSheet("background: #e8f5e9; color: #111;")
        return tab
    def __init__(self):
        super().__init__()
        self.setWindowTitle("NeXOptimIA - Selección de Módulo")
        # Tamaño inicial 1980x1080, posición (0,0)
        self.setGeometry(0, 0, 1980, 1080)
        # Asegura que los botones de ventana estén visibles (no fullscreen, solo maximizado si el usuario lo desea)
        self.setWindowFlags(self.windowFlags() & ~Qt.WindowType.FramelessWindowHint)
        self.central = QWidget()
        self.setCentralWidget(self.central)
        self.main_layout = QVBoxLayout()
        self.central.setLayout(self.main_layout)
        self.show_main_selection()

    def show_main_selection(self):
        self.clear_layout(self.main_layout)
        title = QLabel("NeXOptimIA - Selección de Módulo")
        title.setFont(QFont("Segoe UI", 22, QFont.Weight.Bold))
        title.setAlignment(Qt.AlignmentFlag.AlignCenter)
        self.main_layout.addWidget(title)
        grid_layout = QGridLayout()
        btns = [
            ("⚡ App Eléctrica", "#1de982", self.show_electric),
            ("🌴 Turismo Inteligente", "#00e6e6", self.show_tourism),
            ("🎓 Tutor Estudiantil", "#3a8dde", self.show_tutor),
            ("💧 Agua", "#4fc3f7", self.show_water),
            ("🚗 Transporte Inteligente", "#a259e6", self.show_transport),
            ("🌱 Agricultura Inteligente", "#2e7d32", self.show_agriculture),
            ("🏠 Casa Inteligente", "#ffd600", self.show_home)
        ]
        for idx, (text, color, slot) in enumerate(btns):
            btn = QPushButton(text)
            btn.setMinimumHeight(80)
            btn.setFont(QFont("Segoe UI", 14, QFont.Weight.Bold))
            btn.setStyleSheet(f"background: {color}; color: #111; border-radius: 16px; margin: 12px; padding: 24px 40px;")
            btn.clicked.connect(slot)
            row, col = divmod(idx, 3)
            grid_layout.addWidget(btn, row, col)
        # Si quieres 9 botones, puedes agregar 2 más aquí
        grid_frame = QFrame()
        grid_frame.setLayout(grid_layout)
        grid_frame.setStyleSheet("background: transparent;")
        self.main_layout.addWidget(grid_frame)
        self.main_layout.addStretch()

    def clear_layout(self, layout):
        while layout.count():
            item = layout.takeAt(0)
            widget = item.widget()
            if widget:
                widget.deleteLater()
            elif item.layout():
                self.clear_layout(item.layout())

    def show_electric(self):
        self.show_module_tabbed("App Eléctrica", "#1de982", [
            ("Dashboard", self.create_dashboard_tab),
            ("Entrenamiento IA", self.create_training_tab),
            ("Fuentes Oficiales", self.create_sources_tab)
        ])

    def show_tourism(self):
        self.show_module_tabbed("Turismo Inteligente", "#00e6e6", [
            ("Recomendador", self.create_tourism_tab)
        ])

    def show_tutor(self):
        self.show_module_tabbed("Tutor Estudiantil", "#3a8dde", [
            ("Tutor", self.create_tutor_tab)
        ])

    def show_water(self):
        self.show_module_tabbed("Agua", "#4fc3f7", [
            ("Panel Agua", self.create_water_tab)
        ])

    def show_home(self):
        self.show_module_tabbed("Casa Inteligente", "#ffd600", [
            ("Panel Casa", self.create_home_tab)
        ])

    def show_module_tabbed(self, title, color, tabs):
        self.setWindowTitle(f"NeXOptimIA - {title}")
        self.clear_layout(self.main_layout)
        tab_widget = QTabWidget()
        for tab_name, tab_func in tabs:
            tab = tab_func()
            tab_widget.addTab(tab, tab_name)
        # Eliminar el botón grande de volver (ya no se agrega aquí)
        vbox = QVBoxLayout()
        vbox.addWidget(tab_widget)
        container = QWidget()
        container.setLayout(vbox)
        self.main_layout.addWidget(container)
        self.main_layout.addStretch()

    def create_water_tab(self):
        tab = QWidget()
        layout = QVBoxLayout()
        layout.addWidget(QLabel("💧 Panel de Agua (celeste)\n[Próximamente: integración sensores y control hídrico]"))
        tab.setLayout(layout)
        tab.setStyleSheet("background: #e3f6fd; color: #111;")
        return tab

    def create_home_tab(self):
        tab = QWidget()
        layout = QVBoxLayout()
        layout.addWidget(QLabel("🏠 Panel Casa Inteligente (amarillo)\n[Próximamente: integración y control de dispositivos IoT]"))
        tab.setLayout(layout)
        tab.setStyleSheet("background: #fffde7; color: #111;")
        return tab

    def create_tutor_tab(self):
        tab = QWidget()
        layout = QVBoxLayout()
        layout.addWidget(QLabel("\U0001F393 Tutor Estudiantil (Ollama)"))
        self.tutor_input = QTextEdit()
        self.tutor_input.setPlaceholderText("Escribe tu pregunta académica...")
        self.tutor_input.setFixedHeight(50)
        self.tutor_output = QTextEdit()
        self.tutor_output.setReadOnly(True)
        tutor_btn = QPushButton("Preguntar a Ollama")
        tutor_btn.clicked.connect(self.ask_ollama)
        layout.addWidget(self.tutor_input)
        layout.addWidget(tutor_btn)
        layout.addWidget(self.tutor_output)
        tab.setLayout(layout)
        return tab

    def ask_ollama(self):
        question = self.tutor_input.toPlainText().strip()
        if not question:
            self.tutor_output.setText("Por favor escribe una pregunta.")
            return
        self.tutor_output.setText("Consultando a Ollama...")
        def run_ollama():
            try:
                import requests
                response = requests.post("http://localhost:11434/api/generate", json={"model": "llama2", "prompt": question, "stream": False}, timeout=10)
                if response.status_code == 200:
                    data = response.json()
                    self.tutor_output.setText(data.get("response", "Sin respuesta de Ollama."))
                else:
                    self.tutor_output.setText("Error al consultar Ollama.")
            except Exception as e:
                self.tutor_output.setText(f"Error: {e}")
        threading.Thread(target=run_ollama, daemon=True).start()

    def create_tourism_tab(self):
        tab = QWidget()
        layout = QVBoxLayout()
        layout.addWidget(QLabel("\U0001F30D Turismo Inteligente (Recomendador)"))
        self.tourism_input = QTextEdit()
        self.tourism_input.setPlaceholderText("Escribe tu ubicación o interés turístico...")
        self.tourism_input.setFixedHeight(50)
        self.tourism_output = QTextEdit()
        self.tourism_output.setReadOnly(True)
        tourism_btn = QPushButton("Recomendar sitios")
        tourism_btn.clicked.connect(self.recommend_tourism)
        layout.addWidget(self.tourism_input)
        layout.addWidget(tourism_btn)
        layout.addWidget(self.tourism_output)
        tab.setLayout(layout)
        return tab

    def recommend_tourism(self):
        location = self.tourism_input.toPlainText().strip()
        if not location:
            self.tourism_output.setText("Por favor ingresa una ubicación o interés.")
            return
        self.tourism_output.setText("Buscando recomendaciones...")
        def run_tourism():
            try:
                import requests
                prompt = f"Recomienda sitios turísticos en Costa Rica cerca de: {location}. Responde en español y con contexto local."
                response = requests.post("http://localhost:11434/api/generate", json={"model": "llama2", "prompt": prompt, "stream": False}, timeout=10)
                if response.status_code == 200:
                    data = response.json()
                    self.tourism_output.setText(data.get("response", "Sin respuesta de Ollama."))
                else:
                    self.tourism_output.setText("Error al consultar Ollama.")
            except Exception as e:
                self.tourism_output.setText(f"Error: {e}")
        threading.Thread(target=run_tourism, daemon=True).start()


    def create_dashboard_tab(self):
        tab = QWidget()
        main_layout = QHBoxLayout(tab)
        # --- Real-Time Measurements Panel ---
        left_col = QVBoxLayout()
        left_col.addWidget(QLabel("\u26A1 Real-Time Measurements"))
        self.realtime_table = QTableWidget(8, 2)
        self.realtime_table.setHorizontalHeaderLabels(["Variable", "Valor"])
        self.realtime_table.setEditTriggers(QTableWidget.EditTrigger.NoEditTriggers)
        left_col.addWidget(self.realtime_table)
        self.quality_label = QLabel("Power Quality Grade\nA - Excellent")
        self.quality_label.setStyleSheet("color: #00e676; font-weight: bold; font-size: 18px;")
        left_col.addWidget(self.quality_label)
        self.safety_label = QLabel("Safety Status\n• Voltage OK • Current OK • Power OK • Freq OK")
        self.safety_label.setStyleSheet("color: #00e676;")
        left_col.addWidget(self.safety_label)
        # Botón volver pequeño debajo de Power Quality
        back_btn = QPushButton("Volver al menú principal")
        back_btn.setStyleSheet("background: #222; color: #fff; border-radius: 8px; font-size: 11px; padding: 6px 12px; margin-top: 12px;")
        back_btn.setFixedWidth(180)
        back_btn.clicked.connect(self.show_main_selection)
        left_col.addWidget(back_btn)
        left_col.addStretch()
        # --- Graphs Panel ---
        right_col = QVBoxLayout()
        right_col.addWidget(QLabel("\U0001F4C8 Electrical Monitoring Dashboard"))
        # --- Simulación y Fuentes de Datos (colapsable) ---
        self.sim_panel = QGroupBox("Simulación y Fuentes de Datos")
        self.sim_panel.setCheckable(True)
        self.sim_panel.setChecked(False)
        sim_layout = QVBoxLayout()
        # Fuente de datos radio
        self.radio_real = QRadioButton("Datos Reales (CENCE/ICE)")
        self.radio_sim = QRadioButton("Simulador de Hardware")
        self.radio_real.setChecked(True)
        self.data_source_group = QButtonGroup()
        self.data_source_group.addButton(self.radio_real)
        self.data_source_group.addButton(self.radio_sim)
        sim_layout.addWidget(self.radio_real)
        sim_layout.addWidget(self.radio_sim)
        # Escenario simulador
        self.sim_scenario_combo = QComboBox()
        self.sim_scenario_combo.addItems(["Normal", "Sobrecarga", "Caída de Tensión", "Mala Calidad de Red"])
        self.sim_scenario_combo.setEnabled(False)
        sim_layout.addWidget(QLabel("Escenario del Simulador:"))
        sim_layout.addWidget(self.sim_scenario_combo)
        # Habilitar combo solo si radio_sim
        def update_sim_controls():
            self.sim_scenario_combo.setEnabled(self.radio_sim.isChecked())
        self.radio_real.toggled.connect(update_sim_controls)
        self.radio_sim.toggled.connect(update_sim_controls)
        # Botón aplicar
        self.sim_apply_btn = QPushButton("Aplicar")
        self.sim_apply_btn.clicked.connect(self.apply_simulation_settings)
        sim_layout.addWidget(self.sim_apply_btn)
        self.sim_panel.setLayout(sim_layout)
        right_col.addWidget(self.sim_panel)
        # --- 9 Graphs in 3x3 Grid, fixed size ---
        graph_grid = QGridLayout()
        self.graph_titles = [
            "Voltage RMS (V)", "Current RMS (A)", "Active Power (W)",
            "Power Factor", "Frequency (Hz)", "THD (%)",
            "Demanda Total (MW)", "Generación Neta (MW)", "Reservas del Sistema (MW)"
        ]
        self.graph_colors = ["#2196f3", "#43a047", "#ffd600", "#3a8dde", "#00e676", "#e53935", "#ff9800", "#00bcd4", "#8bc34a"]
        self.graph_canvases = []
        for i in range(9):
            canvas = FigureCanvas(plt.Figure(figsize=(6, 4)))
            canvas.setMinimumSize(300, 180)
            canvas.setMaximumSize(16777215, 16777215)
            canvas.setSizePolicy(QSizePolicy.Policy.Expanding, QSizePolicy.Policy.Expanding)
            canvas.setFocusPolicy(Qt.FocusPolicy.NoFocus)
            canvas.setMouseTracking(False)
            self.graph_canvases.append(canvas)
            graph_grid.addWidget(QLabel(self.graph_titles[i]), i//3*2, i%3)
            graph_grid.addWidget(canvas, i//3*2+1, i%3)
        right_col.addLayout(graph_grid)
        main_layout.addLayout(left_col, 1)
        main_layout.addLayout(right_col, 3)
        # --- Data update logic ---
        self.sim_data_source = 'real'  # 'real' o 'simulator'
        self.sim_scenario = 'Normal'
        def update_measurements_and_graphs():
            try:
                import numpy as np
                # --- Datos de calidad eléctrica ---
                if self.sim_data_source == 'simulator':
                    from src.core.hardware_simulator import HardwareSimulator
                    sim = HardwareSimulator()
                    sim.set_scenario(self.sim_scenario.lower().replace(' ', '_'))
                    reading = sim.generate_new_reading()
                    values = [
                        ("Voltage RMS", f"{reading['Voltage RMS']:.2f} V"),
                        ("Current RMS", f"{reading['Current RMS']:.2f} A"),
                        ("Active Power", f"{reading['Active Power']:.1f} W"),
                        ("Power Factor", f"{reading['Power Factor']:.3f}"),
                        ("Frequency", f"{reading['Frequency']:.2f} Hz"),
                        ("THD Voltage", f"{reading['THD Voltage']:.1f} %"),
                        ("THD Current", f"{reading['THD Current']:.1f} %"),
                        ("Power Quality Grade", reading['Power Quality Grade'])
                    ]
                    # Simular series para gráficos
                    x = np.arange(0, 10)
                    y_data = [
                        np.array([reading['Voltage RMS'] + np.random.normal(0, 0.5) for _ in range(10)]),
                        np.array([reading['Current RMS'] + np.random.normal(0, 0.2) for _ in range(10)]),
                        np.array([reading['Active Power'] + np.random.normal(0, 10) for _ in range(10)]),
                        np.array([reading['Power Factor'] + np.random.normal(0, 0.01) for _ in range(10)]),
                        np.array([reading['Frequency'] + np.random.normal(0, 0.02) for _ in range(10)]),
                        np.array([reading['THD Voltage'] + np.random.normal(0, 0.2) for _ in range(10)]),
                        # Demanda, generación, reservas simuladas según escenario
                        np.array([1800 + (400 if self.sim_scenario=="Sobrecarga" else 0) + np.random.normal(0, 30) for _ in range(10)]),
                        np.array([1700 + (300 if self.sim_scenario=="Sobrecarga" else 0) + np.random.normal(0, 30) for _ in range(10)]),
                        np.array([200 + (50 if self.sim_scenario=="Sobrecarga" else 0) + np.random.normal(0, 10) for _ in range(10)])
                    ]
                else:
                    from src.integrations.ice_real_data import ICEDataIntegrator
                    integrator = ICEDataIntegrator()
                    resumen = integrator.get_cenceweb_summary()
                    values = [
                        ("Voltage RMS", f"{234.0:.2f} V"),
                        ("Current RMS", f"{9.7:.2f} A"),
                        ("Active Power", f"{2150.0:.1f} W"),
                        ("Power Factor", f"{0.99:.3f}"),
                        ("Frequency", f"{49.95:.2f} Hz"),
                        ("THD Voltage", f"{3.2:.1f} %"),
                        ("THD Current", f"{4.7:.1f} %"),
                        ("Power Quality Grade", "A - Excellent")
                    ]
                    # Series reales para demanda, generación, reservas
                    x = np.arange(0, 10)
                    demanda = resumen.get('demanda_serie', [[i,1800+np.random.normal(0,30)] for i in range(10)])
                    generacion = resumen.get('generacion_serie', [[i,1700+np.random.normal(0,30)] for i in range(10)])
                    reservas = resumen.get('reserva_serie', [[i,200+np.random.normal(0,10)] for i in range(10)])
                    y_data = [
                        np.array([234 + np.random.normal(0, 0.5) for _ in range(10)]),
                        np.array([9.7 + np.random.normal(0, 0.2) for _ in range(10)]),
                        np.array([2150 + np.random.normal(0, 10) for _ in range(10)]),
                        np.array([0.99 + np.random.normal(0, 0.01) for _ in range(10)]),
                        np.array([49.95 + np.random.normal(0, 0.02) for _ in range(10)]),
                        np.array([3.2 + np.random.normal(0, 0.2) for _ in range(10)]),
                        np.array([float(y[1]) for y in demanda[-10:]]),
                        np.array([float(y[1]) for y in generacion[-10:]]),
                        np.array([float(y[1]) for y in reservas[-10:]])
                    ]
                for i, (k, v) in enumerate(values):
                    self.realtime_table.setItem(i, 0, QTableWidgetItem(k))
                    self.realtime_table.setItem(i, 1, QTableWidgetItem(v))
                # Actualizar gráficos
                for i, canvas in enumerate(self.graph_canvases):
                    ax = canvas.figure.subplots()
                    ax.clear()
                    ax.plot(x, y_data[i], color=self.graph_colors[i], marker="o", linewidth=2)
                    ax.set_facecolor("#181c24")
                    ax.grid(True, alpha=0.3)
                    ax.set_title(self.graph_titles[i], color="#fff", fontsize=10)
                    ax.tick_params(axis='x', labelsize=8, colors="#fff")
                    ax.tick_params(axis='y', labelsize=8, colors="#fff")
                    for spine in ax.spines.values():
                        spine.set_color("#888")
                    # Eliminar márgenes y espacio blanco
                    ax.margins(0)
                    ax.set_position([0, 0, 1, 1])
                    canvas.figure.subplots_adjust(left=0, right=1, top=1, bottom=0)
                    canvas.draw()
                # Actualizar Power Quality Grade
                self.quality_label.setText(f"Power Quality Grade\n{values[7][1]}")
            except Exception as e:
                print(f"Error updating measurements: {e}")
        self.data_timer = QTimer()
        self.data_timer.timeout.connect(update_measurements_and_graphs)
        self.data_timer.start(3000)
        update_measurements_and_graphs()
        return tab
    def apply_simulation_settings(self):
        if self.radio_real.isChecked():
            self.sim_data_source = 'real'
        else:
            self.sim_data_source = 'simulator'
        self.sim_scenario = self.sim_scenario_combo.currentText()
        self.data_timer.stop()
        self.data_timer.start(3000)

    def create_training_tab(self):
        """
        Pestaña de placeholder para Entrenamiento IA.
        """
        tab = QWidget()
        layout = QVBoxLayout()
        layout.addWidget(QLabel("\U0001F916 Próximamente: Entrenamiento IA para modelos de optimización eléctrica y detección de anomalías."))
        tab.setLayout(layout)
        return tab

    def create_sources_tab(self):
        """
        Pestaña de placeholder para Fuentes Oficiales.
        """
        tab = QWidget()
        layout = QVBoxLayout()
        layout.addWidget(QLabel("\U0001F4D1 Fuentes Oficiales: ICE, CENCE, ARESEP, EIA, CICR, PGR.\nDatos y referencias oficiales para validación y benchmarking."))
        tab.setLayout(layout)
        return tab


if __name__ == "__main__":
    app = QApplication(sys.argv)
    window = MainWindow()
    window.show()
    sys.exit(app.exec())
