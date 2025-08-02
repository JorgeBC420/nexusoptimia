"""
NexusOptim IA - Home Edition
Versión doméstica para todos los hogares de Costa Rica

Sistema completo familiar:
- Asistente doméstico inteligente
- Educación personalizada para toda la familia
- Turismo local y recomendaciones
- Monitoreo del hogar inteligente
- Gestión financiera familiar
- Salud y bienestar familiar

Copyright (c) 2025 OpenNexus - NexusOptim IA
En cada hogar costarricense - Democratizando la IA
"""

import tkinter as tk
from tkinter import ttk, messagebox, scrolledtext, Canvas
import json
import threading
import time
from datetime import datetime, timedelta
import random
import os
import requests
from PIL import Image, ImageTk
import sqlite3
import uuid

class NexusOptimHomeEdition:
    """Versión doméstica de NexusOptim IA para todos los hogares de Costa Rica"""
    
    def __init__(self):
        self.root = tk.Tk()
        self.root.title("🏠 NexusOptim IA - Hogar Inteligente")
        self.root.geometry("1200x800")
        self.root.configure(bg='#0f1419')
        
        # Mostrar banners de bienvenida
        self.show_startup_banners()
        
        # Configuración familiar
        self.family_config = {
            'home_name': 'Casa Familia Costa Rica',
            'location': 'San José, Costa Rica',
            'family_members': [
                {'name': 'Papá', 'age': 45, 'interests': ['noticias', 'deportes', 'trabajo']},
                {'name': 'Mamá', 'age': 42, 'interests': ['cocina', 'salud', 'familia']},
                {'name': 'Ana', 'age': 16, 'interests': ['música', 'estudios', 'tecnología']},
                {'name': 'Carlos', 'age': 12, 'interests': ['juegos', 'ciencias', 'deportes']}
            ],
            'household_devices': ['smart_tv', 'alexa', 'phones', 'tablets', 'security_cameras'],
            'subscription_tier': 'familiar_premium'  # Gratis para todos los hogares CR
        }
        
        # Base de datos local para cada hogar
        self.init_home_database()
        
        # Estado del hogar
        self.home_status = {
            'security': 'armed',
            'temperature': 24,
            'energy_usage': 85,
            'internet_status': 'connected',
            'family_present': ['Mamá', 'Carlos']
        }
        
        self.setup_ui()
        self.start_home_services()
        
    def init_home_database(self):
        """Inicializar base de datos local del hogar"""
        self.db_path = 'nexusoptim_hogar.db'
        
        conn = sqlite3.connect(self.db_path)
        cursor = conn.cursor()
        
        # Tabla de actividades familiares
        cursor.execute('''
            CREATE TABLE IF NOT EXISTS family_activities (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                member_name TEXT,
                activity_type TEXT,
                description TEXT,
                timestamp DATETIME DEFAULT CURRENT_TIMESTAMP
            )
        ''')
        
        # Tabla de configuraciones del hogar
        cursor.execute('''
            CREATE TABLE IF NOT EXISTS home_settings (
                key TEXT PRIMARY KEY,
                value TEXT,
                updated_at DATETIME DEFAULT CURRENT_TIMESTAMP
            )
        ''')
        
        # Tabla de recomendaciones familiares
        cursor.execute('''
            CREATE TABLE IF NOT EXISTS family_recommendations (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                category TEXT,
                title TEXT,
                description TEXT,
                priority INTEGER,
                created_at DATETIME DEFAULT CURRENT_TIMESTAMP
            )
        ''')
        
        # Tabla de reportes de averías
        cursor.execute('''
            CREATE TABLE IF NOT EXISTS damage_reports (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                report_id TEXT UNIQUE,
                report_type TEXT,
                location TEXT,
                description TEXT,
                priority TEXT,
                status TEXT DEFAULT 'pendiente',
                reporter_name TEXT,
                contact_info TEXT,
                coordinates TEXT,
                timestamp DATETIME DEFAULT CURRENT_TIMESTAMP,
                resolution_date DATETIME,
                assigned_technician TEXT,
                estimated_repair_time TEXT
            )
        ''')
        
        conn.commit()
        conn.close()
        
    def setup_ui(self):
        """Configurar interfaz familiar"""
        # Header familiar
        header_frame = tk.Frame(self.root, bg='#1e2328', height=80)
        header_frame.pack(fill='x', pady=0)
        header_frame.pack_propagate(False)
        
        # Logo y bienvenida
        welcome_frame = tk.Frame(header_frame, bg='#1e2328')
        welcome_frame.pack(expand=True)
        
        title_label = tk.Label(welcome_frame, 
                              text="🏠 NexusOptim IA - Hogar Inteligente", 
                              font=('Arial', 20, 'bold'), 
                              fg='#00d4aa', bg='#1e2328')
        title_label.pack(pady=5)
        
        home_label = tk.Label(welcome_frame, 
                             text=f"🇨🇷 {self.family_config['home_name']} • {self.family_config['location']}", 
                             font=('Arial', 12), 
                             fg='#ffd700', bg='#1e2328')
        home_label.pack()
        
        # Status bar
        status_frame = tk.Frame(self.root, bg='#2d3748', height=40)
        status_frame.pack(fill='x')
        status_frame.pack_propagate(False)
        
        status_info = tk.Frame(status_frame, bg='#2d3748')
        status_info.pack(expand=True)
        
        # Indicadores de estado
        indicators = [
            ("🔒", f"Seguridad: {self.home_status['security']}", '#00d4aa'),
            ("🌡️", f"{self.home_status['temperature']}°C", '#4a9eff'),
            ("⚡", f"Energía: {self.home_status['energy_usage']}%", '#ff6b6b'),
            ("🌐", f"Internet: {self.home_status['internet_status']}", '#00d4aa'),
            ("👥", f"En casa: {len(self.home_status['family_present'])}", '#ffd700')
        ]
        
        for icon, text, color in indicators:
            indicator = tk.Label(status_info, text=f"{icon} {text}", 
                                font=('Arial', 10), fg=color, bg='#2d3748')
            indicator.pack(side='left', padx=15, pady=8)
            
        # Main container
        main_container = tk.Frame(self.root, bg='#0f1419')
        main_container.pack(fill='both', expand=True, padx=10, pady=10)
        
        # Notebook para diferentes secciones
        self.notebook = ttk.Notebook(main_container)
        self.notebook.pack(fill='both', expand=True)
        
        # Configurar estilo familiar
        style = ttk.Style()
        style.theme_use('clam')
        style.configure('TNotebook', background='#0f1419')
        style.configure('TNotebook.Tab', background='#1e2328', foreground='white', padding=[15, 10])
        style.map('TNotebook.Tab', background=[('selected', '#00d4aa')], foreground=[('selected', 'black')])
        
        # Crear tabs familiares
        self.create_family_dashboard_tab()
        self.create_education_tab()
        self.create_entertainment_tab()
        self.create_home_automation_tab()
        self.create_family_finance_tab()
        self.create_health_wellness_tab()
        self.create_local_services_tab()
        self.create_damage_reports_tab()  # Nueva tab de reportes
        
    def create_family_dashboard_tab(self):
        """Dashboard principal familiar"""
        dashboard_frame = tk.Frame(self.notebook, bg='#0f1419')
        self.notebook.add(dashboard_frame, text='🏠 Casa')
        
        # Bienvenida personalizada
        welcome_frame = tk.LabelFrame(dashboard_frame, text="👋 Bienvenida Familiar", 
                                     bg='#0f1419', fg='#00d4aa', font=('Arial', 12, 'bold'))
        welcome_frame.pack(fill='x', padx=20, pady=10)
        
        current_hour = datetime.now().hour
        if current_hour < 12:
            greeting = "¡Buenos días familia!"
        elif current_hour < 18:
            greeting = "¡Buenas tardes familia!"
        else:
            greeting = "¡Buenas noches familia!"
            
        welcome_text = f"""
{greeting} 🌅

🏠 Bienvenidos a su hogar inteligente
👥 Miembros en casa: {', '.join(self.home_status['family_present'])}
📅 Hoy es {datetime.now().strftime('%A, %d de %B')}
🌤️ Clima en {self.family_config['location']}: 26°C, parcialmente nublado

💡 Recomendación del día: 
   Hoy es perfecto para una actividad familiar al aire libre.
   ¿Qué tal una visita al Parque La Sabana?
        """
        
        welcome_label = tk.Label(welcome_frame, text=welcome_text, 
                                font=('Arial', 11), fg='#cccccc', bg='#0f1419', 
                                justify=tk.LEFT)
        welcome_label.pack(pady=15, padx=20)
        
        # Panel de miembros de la familia
        family_frame = tk.LabelFrame(dashboard_frame, text="👨‍👩‍👧‍👦 Familia", 
                                    bg='#0f1419', fg='white', font=('Arial', 12, 'bold'))
        family_frame.pack(fill='x', padx=20, pady=10)
        
        family_grid = tk.Frame(family_frame, bg='#0f1419')
        family_grid.pack(pady=15, padx=15)
        
        for i, member in enumerate(self.family_config['family_members']):
            member_card = tk.Frame(family_grid, bg='#1e2328', relief='raised', bd=2)
            member_card.grid(row=0, column=i, padx=10, pady=5, sticky='nsew')
            
            # Status presencia
            status_color = '#00d4aa' if member['name'] in self.home_status['family_present'] else '#666666'
            status_text = '🟢 En casa' if member['name'] in self.home_status['family_present'] else '⚫ Fuera'
            
            tk.Label(member_card, text=f"👤 {member['name']}", 
                    font=('Arial', 12, 'bold'), fg='#00d4aa', bg='#1e2328').pack(pady=5)
            
            tk.Label(member_card, text=f"📅 {member['age']} años", 
                    font=('Arial', 10), fg='#cccccc', bg='#1e2328').pack(pady=2)
            
            tk.Label(member_card, text=status_text, 
                    font=('Arial', 9), fg=status_color, bg='#1e2328').pack(pady=2)
            
            interests_text = "🎯 " + ", ".join(member['interests'][:2])
            tk.Label(member_card, text=interests_text, 
                    font=('Arial', 8), fg='#888888', bg='#1e2328', wraplength=120).pack(pady=5)
            
        # Configurar grid
        for i in range(len(self.family_config['family_members'])):
            family_grid.columnconfigure(i, weight=1)
            
        # Actividades del día
        activities_frame = tk.LabelFrame(dashboard_frame, text="📅 Actividades de Hoy", 
                                        bg='#0f1419', fg='white', font=('Arial', 12, 'bold'))
        activities_frame.pack(fill='both', expand=True, padx=20, pady=10)
        
        self.activities_text = scrolledtext.ScrolledText(activities_frame, height=10, width=100, 
                                                        bg='#1e2328', fg='#cccccc', font=('Arial', 10))
        self.activities_text.pack(pady=10, padx=10, fill='both', expand=True)
        
        # Actividades simuladas
        sample_activities = """
📅 ACTIVIDADES FAMILIARES DEL DÍA

08:00 - ☕ Desayuno familiar (Toda la familia)
09:30 - 📚 Clases virtuales - Ana (Matemáticas)
10:00 - 🎮 Tiempo de juego educativo - Carlos
11:00 - 💼 Reunión de trabajo remoto - Papá
12:30 - 🍽️ Almuerzo familiar
14:00 - 📖 Lectura guiada - Carlos y Mamá
15:30 - 🎵 Práctica de piano - Ana
16:00 - 🛒 Compras en línea - Mamá
17:30 - ⚽ Fútbol en el parque - Papá y Carlos
19:00 - 🥘 Cena familiar
20:00 - 📺 Película familiar
21:30 - 😴 Hora de dormir - Carlos
22:00 - 📱 Tiempo familiar libre

🤖 Sugerencias IA:
• El clima está perfecto para actividades al aire libre
• Ana tiene examen de ciencias mañana - recordar estudiar
• Cumpleaños de la abuela en 3 días - planificar celebración
• Mantenimiento del auto programado para el viernes
        """
        
        self.activities_text.insert('1.0', sample_activities)
        
    def create_education_tab(self):
        """Tab de educación familiar"""
        education_frame = tk.Frame(self.notebook, bg='#0f1419')
        self.notebook.add(education_frame, text='🎓 Educación')
        
        # Selector de miembro familiar
        selector_frame = tk.Frame(education_frame, bg='#0f1419')
        selector_frame.pack(fill='x', padx=20, pady=10)
        
        tk.Label(selector_frame, text="👤 Selecciona miembro de la familia:", 
                bg='#0f1419', fg='white', font=('Arial', 12, 'bold')).pack(side='left', padx=10)
        
        self.education_member_var = tk.StringVar(value='Ana')
        member_combo = ttk.Combobox(selector_frame, textvariable=self.education_member_var, 
                                   values=[m['name'] for m in self.family_config['family_members']])
        member_combo.pack(side='left', padx=10)
        member_combo.bind('<<ComboboxSelected>>', self.update_education_content)
        
        # Contenido educativo personalizado
        content_frame = tk.LabelFrame(education_frame, text="📚 Contenido Educativo Personalizado", 
                                     bg='#0f1419', fg='white', font=('Arial', 12, 'bold'))
        content_frame.pack(fill='both', expand=True, padx=20, pady=10)
        
        self.education_content = scrolledtext.ScrolledText(content_frame, height=20, width=100, 
                                                          bg='#1e2328', fg='#cccccc', font=('Arial', 10))
        self.education_content.pack(pady=10, padx=10, fill='both', expand=True)
        
        # Botones de acción educativa
        edu_buttons_frame = tk.Frame(content_frame, bg='#0f1419')
        edu_buttons_frame.pack(fill='x', padx=10, pady=10)
        
        tk.Button(edu_buttons_frame, text="🎯 Crear Lección Personalizada", 
                 command=self.create_family_lesson,
                 bg='#00d4aa', fg='black', font=('Arial', 11, 'bold')).pack(side='left', padx=10)
        
        tk.Button(edu_buttons_frame, text="📊 Ver Progreso", 
                 command=self.show_education_progress,
                 bg='#4a9eff', fg='white', font=('Arial', 11, 'bold')).pack(side='left', padx=10)
        
        tk.Button(edu_buttons_frame, text="🎮 Juegos Educativos", 
                 command=self.launch_educational_games,
                 bg='#ff6b6b', fg='white', font=('Arial', 11, 'bold')).pack(side='left', padx=10)
        
        self.update_education_content()
        
    def create_entertainment_tab(self):
        """Tab de entretenimiento familiar"""
        entertainment_frame = tk.Frame(self.notebook, bg='#0f1419')
        self.notebook.add(entertainment_frame, text='🎬 Entretenimiento')
        
        # Recomendaciones familiares
        recommendations_frame = tk.LabelFrame(entertainment_frame, text="🎯 Recomendaciones para la Familia", 
                                             bg='#0f1419', fg='white', font=('Arial', 12, 'bold'))
        recommendations_frame.pack(fill='x', padx=20, pady=10)
        
        # Grid de recomendaciones
        rec_grid = tk.Frame(recommendations_frame, bg='#0f1419')
        rec_grid.pack(pady=15, padx=15)
        
        entertainment_categories = [
            ("🎬 Películas", "Coco, Encanto, Los Increíbles 2", '#ff6b6b'),
            ("📺 Series", "Avatar, Gravity Falls, Bluey", '#4a9eff'),
            ("🎵 Música", "Jesse & Joy, Manu Chao, Disney", '#00d4aa'),
            ("🎮 Juegos", "Minecraft, Mario Kart, Just Dance", '#ffd700')
        ]
        
        for i, (category, content, color) in enumerate(entertainment_categories):
            cat_frame = tk.Frame(rec_grid, bg='#1e2328', relief='raised', bd=2)
            cat_frame.grid(row=0, column=i, padx=8, pady=5, sticky='nsew')
            
            tk.Label(cat_frame, text=category, font=('Arial', 12, 'bold'), 
                    fg=color, bg='#1e2328').pack(pady=8)
            
            tk.Label(cat_frame, text=content, font=('Arial', 9), 
                    fg='#cccccc', bg='#1e2328', wraplength=150, justify=tk.CENTER).pack(pady=5, padx=10)
            
            tk.Button(cat_frame, text="▶️ Ver más", 
                     command=lambda c=category: self.show_entertainment_category(c),
                     bg=color, fg='white' if color != '#ffd700' else 'black', 
                     font=('Arial', 8, 'bold')).pack(pady=8)
            
        # Configurar grid
        for i in range(4):
            rec_grid.columnconfigure(i, weight=1)
            
        # Actividades familiares
        activities_ent_frame = tk.LabelFrame(entertainment_frame, text="🏡 Actividades en Casa", 
                                            bg='#0f1419', fg='white', font=('Arial', 12, 'bold'))
        activities_ent_frame.pack(fill='both', expand=True, padx=20, pady=10)
        
        activities_info = """
🏡 ACTIVIDADES FAMILIARES EN CASA

🎲 JUEGOS DE MESA:
• Monopolio Costa Rica Edition
• Scrabble en Español  
• Uno Familiar
• Pictionary Digital

🎨 ACTIVIDADES CREATIVAS:
• Dibujo digital familiar
• Cocina costarricense tradicional
• Jardinería en el patio
• Fotografía familiar

🎬 NOCHES TEMÁTICAS:
• Viernes de Películas Costarricenses
• Karaoke Familiar
• Documentales de Naturaleza
• Concursos Familiares

🌟 EXPERIENCIAS VIRTUALES:
• Tour virtual por Parques Nacionales CR
• Museos virtuales del mundo
• Conciertos en línea
• Clases de baile familiar

🤖 SUGERENCIAS IA PERSONALIZADAS:
• Basadas en gustos de cada miembro
• Considerando horarios familiares
• Adaptadas al clima y época del año
• Integradas con calendario familiar
        """
        
        activities_display = scrolledtext.ScrolledText(activities_ent_frame, height=15, width=100, 
                                                      bg='#1e2328', fg='#cccccc', font=('Arial', 10))
        activities_display.pack(pady=10, padx=10, fill='both', expand=True)
        activities_display.insert('1.0', activities_info)
        
    def create_home_automation_tab(self):
        """Tab de automatización del hogar"""
        automation_frame = tk.Frame(self.notebook, bg='#0f1419')
        self.notebook.add(automation_frame, text='🏠 Casa Inteligente')
        
        # Control de dispositivos
        devices_frame = tk.LabelFrame(automation_frame, text="🔌 Control de Dispositivos", 
                                     bg='#0f1419', fg='white', font=('Arial', 12, 'bold'))
        devices_frame.pack(fill='x', padx=20, pady=10)
        
        devices_grid = tk.Frame(devices_frame, bg='#0f1419')
        devices_grid.pack(pady=15, padx=15)
        
        # Dispositivos del hogar
        home_devices = [
            ("💡 Luces", "12 dispositivos", "8 encendidas", '#ffd700'),
            ("🌡️ Clima", "3 termostatos", "24°C promedio", '#4a9eff'),
            ("🔒 Seguridad", "6 cámaras", "Sistema armado", '#00d4aa'),
            ("📺 Entretenimiento", "4 pantallas", "2 en uso", '#ff6b6b'),
            ("🏠 Sensores", "15 sensores", "Todos activos", '#9b59b6'),
            ("⚡ Energía", "Monitor activo", "85% uso normal", '#ff9f43')
        ]
        
        row, col = 0, 0
        for device, count, status, color in home_devices:
            device_card = tk.Frame(devices_grid, bg='#1e2328', relief='raised', bd=2)
            device_card.grid(row=row, column=col, padx=8, pady=8, sticky='nsew')
            
            tk.Label(device_card, text=device, font=('Arial', 12, 'bold'), 
                    fg=color, bg='#1e2328').pack(pady=5)
            
            tk.Label(device_card, text=count, font=('Arial', 10), 
                    fg='#cccccc', bg='#1e2328').pack(pady=2)
            
            tk.Label(device_card, text=status, font=('Arial', 9), 
                    fg='#888888', bg='#1e2328').pack(pady=2)
            
            tk.Button(device_card, text="⚙️ Control", 
                     command=lambda d=device: self.control_device(d),
                     bg=color, fg='white' if color != '#ffd700' else 'black', 
                     font=('Arial', 8, 'bold')).pack(pady=5)
            
            col += 1
            if col > 2:
                col = 0
                row += 1
                
        # Configurar grid
        for i in range(3):
            devices_grid.columnconfigure(i, weight=1)
            
        # Automatizaciones activas
        automation_list_frame = tk.LabelFrame(automation_frame, text="🤖 Automatizaciones Activas", 
                                             bg='#0f1419', fg='white', font=('Arial', 12, 'bold'))
        automation_list_frame.pack(fill='both', expand=True, padx=20, pady=10)
        
        automation_info = """
🤖 AUTOMATIZACIONES FAMILIARES ACTIVAS

⏰ RUTINAS MATUTINAS (6:00 - 8:00 AM):
• Encender luces gradualmente
• Reproducir música suave
• Preparar temperatura ambiente
• Mostrar agenda familiar del día
• Encender cafetera automática

🌅 RUTINAS VESPERTINAS (6:00 - 8:00 PM):
• Luces cálidas automáticas
• Cerrar cortinas inteligentes
• Ajustar temperatura nocturna
• Preparar entretenimiento familiar
• Activar modo seguridad nocturna

🏠 DETECCIÓN DE PRESENCIA:
• Luces automáticas al entrar
• Música personalizada por miembro
• Ajuste de temperatura al llegar
• Notificaciones de llegada/salida
• Desactivación eco-friendly al salir

📱 CONTROL POR VOZ:
• "Alexa, modo familia" - Configura ambiente familiar
• "Ok Google, buenas noches" - Rutina nocturna
• "Siri, estoy en casa" - Bienvenida personalizada
• "Maestro, ayuda con tareas" - Asistente educativo

🔐 SEGURIDAD INTELIGENTE:
• Reconocimiento facial familiar
• Alertas de movimiento inusual
• Grabación automática de visitantes
• Notificaciones móviles en tiempo real
• Integración con policía local

💡 EFICIENCIA ENERGÉTICA:
• Apagado automático de dispositivos
• Optimización de uso eléctrico
• Reporte mensual de consumo
• Sugerencias de ahorro energético
• Integración con paneles solares
        """
        
        automation_display = scrolledtext.ScrolledText(automation_list_frame, height=18, width=100, 
                                                      bg='#1e2328', fg='#cccccc', font=('Arial', 10))
        automation_display.pack(pady=10, padx=10, fill='both', expand=True)
        automation_display.insert('1.0', automation_info)
        
    def create_family_finance_tab(self):
        """Tab de finanzas familiares"""
        finance_frame = tk.Frame(self.notebook, bg='#0f1419')
        self.notebook.add(finance_frame, text='💰 Finanzas')
        
        # Resumen financiero
        summary_frame = tk.LabelFrame(finance_frame, text="📊 Resumen Financiero Familiar", 
                                     bg='#0f1419', fg='white', font=('Arial', 12, 'bold'))
        summary_frame.pack(fill='x', padx=20, pady=10)
        
        finance_grid = tk.Frame(summary_frame, bg='#0f1419')
        finance_grid.pack(pady=15, padx=15)
        
        # Métricas financieras
        finance_metrics = [
            ("💵 Ingresos", "₡850,000", "Este mes", '#00d4aa'),
            ("💸 Gastos", "₡650,000", "Este mes", '#ff6b6b'),
            ("💰 Ahorros", "₡200,000", "Disponible", '#ffd700'),
            ("📈 Inversiones", "₡150,000", "Creciendo", '#4a9eff')
        ]
        
        for i, (category, amount, period, color) in enumerate(finance_metrics):
            metric_card = tk.Frame(finance_grid, bg='#1e2328', relief='raised', bd=2)
            metric_card.grid(row=0, column=i, padx=10, pady=5, sticky='nsew')
            
            tk.Label(metric_card, text=category, font=('Arial', 11, 'bold'), 
                    fg=color, bg='#1e2328').pack(pady=5)
            
            tk.Label(metric_card, text=amount, font=('Arial', 16, 'bold'), 
                    fg=color, bg='#1e2328').pack(pady=2)
            
            tk.Label(metric_card, text=period, font=('Arial', 9), 
                    fg='#888888', bg='#1e2328').pack(pady=2)
            
        # Configurar grid
        for i in range(4):
            finance_grid.columnconfigure(i, weight=1)
            
        # Gestión financiera inteligente
        management_frame = tk.LabelFrame(finance_frame, text="🤖 Gestión Financiera Inteligente", 
                                        bg='#0f1419', fg='white', font=('Arial', 12, 'bold'))
        management_frame.pack(fill='both', expand=True, padx=20, pady=10)
        
        finance_info = """
🤖 ASISTENTE FINANCIERO FAMILIAR IA

📊 ANÁLISIS AUTOMÁTICO:
• Categorización inteligente de gastos
• Detección de patrones de consumo
• Predicción de gastos futuros
• Alertas de gastos inusuales
• Comparación con familias similares

💡 RECOMENDACIONES PERSONALIZADAS:
• Oportunidades de ahorro identificadas
• Mejores momentos para compras grandes
• Comparación automática de precios
• Sugerencias de inversión familiar
• Planificación de vacaciones familiares

🏦 INTEGRACIÓN BANCARIA:
• Conexión con bancos costarricenses
• Sincronización automática de cuentas
• Alertas de movimientos bancarios
• Recordatorios de pagos importantes
• Gestión de presupuesto familiar

📈 METAS FAMILIARES:
• Casa propia: ₡15,000,000 (Meta en 5 años)
• Educación hijos: ₡5,000,000 (Universidad)
• Vacaciones anuales: ₡800,000
• Fondo de emergencia: ₡2,000,000
• Inversiones futuro: ₡1,000,000

💳 CONTROL DE GASTOS:
• Límites automáticos por categoría
• Notificaciones de presupuesto
• Análisis de gastos por miembro
• Sugerencias de optimización
• Reportes mensuales familiares

🔔 ALERTAS INTELIGENTES:
• "Papá gastó más en gasolina este mes"
• "Oportunidad: Descuento en supermercado favorito"
• "Meta de ahorros alcanzada al 80%"
• "Recordatorio: Pago de seguros en 3 días"
• "Sugerencia: Cambiar plan de telefonía puede ahorrar ₡15,000/mes"

🇨🇷 ESPECÍFICO PARA COSTA RICA:
• Integración con SINPE Móvil
• Cálculo automático de impuestos
• Seguimiento de servicios públicos (ICE, AyA)
• Descuentos en comercios locales
• Planificación para aguinaldo
        """
        
        finance_display = scrolledtext.ScrolledText(management_frame, height=20, width=100, 
                                                   bg='#1e2328', fg='#cccccc', font=('Arial', 10))
        finance_display.pack(pady=10, padx=10, fill='both', expand=True)
        finance_display.insert('1.0', finance_info)
        
    def create_health_wellness_tab(self):
        """Tab de salud y bienestar familiar"""
        health_frame = tk.Frame(self.notebook, bg='#0f1419')
        self.notebook.add(health_frame, text='🏥 Salud')
        
        # Estado de salud familiar
        health_status_frame = tk.LabelFrame(health_frame, text="💓 Estado de Salud Familiar", 
                                           bg='#0f1419', fg='white', font=('Arial', 12, 'bold'))
        health_status_frame.pack(fill='x', padx=20, pady=10)
        
        health_grid = tk.Frame(health_status_frame, bg='#0f1419')
        health_grid.pack(pady=15, padx=15)
        
        # Métricas de salud por miembro
        family_health = [
            ("👨 Papá", "Excelente", "Ejercicio: 5/7 días", '#00d4aa'),
            ("👩 Mamá", "Muy bien", "Yoga: 4/7 días", '#00d4aa'),
            ("👧 Ana", "Perfecto", "Deportes: 6/7 días", '#00d4aa'),
            ("👦 Carlos", "Excelente", "Actividad: 7/7 días", '#00d4aa')
        ]
        
        for i, (member, status, activity, color) in enumerate(family_health):
            health_card = tk.Frame(health_grid, bg='#1e2328', relief='raised', bd=2)
            health_card.grid(row=0, column=i, padx=8, pady=5, sticky='nsew')
            
            tk.Label(health_card, text=member, font=('Arial', 12, 'bold'), 
                    fg='#ffd700', bg='#1e2328').pack(pady=5)
            
            tk.Label(health_card, text=status, font=('Arial', 11, 'bold'), 
                    fg=color, bg='#1e2328').pack(pady=2)
            
            tk.Label(health_card, text=activity, font=('Arial', 9), 
                    fg='#cccccc', bg='#1e2328').pack(pady=2)
            
            tk.Button(health_card, text="📊 Detalles", 
                     command=lambda m=member: self.show_health_details(m),
                     bg='#4a9eff', fg='white', font=('Arial', 8, 'bold')).pack(pady=5)
            
        # Configurar grid
        for i in range(4):
            health_grid.columnconfigure(i, weight=1)
            
        # Sistema de salud inteligente
        health_system_frame = tk.LabelFrame(health_frame, text="🤖 Sistema de Salud Inteligente", 
                                           bg='#0f1419', fg='white', font=('Arial', 12, 'bold'))
        health_system_frame.pack(fill='both', expand=True, padx=20, pady=10)
        
        health_info = """
🏥 ASISTENTE DE SALUD FAMILIAR IA

📱 MONITOREO CONTINUO:
• Integración con dispositivos wearables
• Seguimiento de signos vitales
• Análisis de patrones de sueño
• Monitoreo de actividad física
• Detección temprana de anomalías

💊 GESTIÓN DE MEDICAMENTOS:
• Recordatorios automáticos de medicinas
• Verificación de interacciones medicamentosas
• Seguimiento de tratamientos médicos
• Conexión con farmacias locales
• Alertas de reabastecimiento

🏥 INTEGRACIÓN MÉDICA CR:
• Conexión con CCSS (Caja Costarricense)
• Agenda de citas médicas automática
• Historial médico familiar digital
• Vacunación y controles preventivos
• Telemedicina integrada

🍎 NUTRICIÓN INTELIGENTE:
• Planificación de menús familiares
• Análisis nutricional automático
• Sugerencias de comidas saludables
• Lista de compras inteligente
• Recetas costarricenses saludables

🏃‍♂️ ACTIVIDAD FÍSICA FAMILIAR:
• Rutinas personalizadas por edad
• Seguimiento de objetivos fitness
• Competencias familiares divertidas
• Integración con parques locales CR
• Actividades al aire libre sugeridas

🧠 BIENESTAR MENTAL:
• Seguimiento del estado de ánimo
• Técnicas de relajación familiares
• Meditación guiada personalizada
• Actividades anti-estrés
• Detección temprana de problemas

📊 REPORTES DE SALUD:
• Resumen semanal familiar
• Tendencias de mejora/deterioro
• Comparación con estándares CR
• Recomendaciones preventivas
• Alertas médicas importantes

🚨 EMERGENCIAS MÉDICAS:
• Detección automática de emergencias
• Contacto directo con servicios médicos
• Localización GPS para ambulancias
• Información médica crítica familiar
• Protocolos de primeros auxilios IA

🇨🇷 ESPECÍFICO COSTA RICA:
• Integración con hospitales nacionales
• Conocimiento de enfermedades tropicales
• Alertas epidemiológicas nacionales
• Conexión con Ministerio de Salud
• Promoción de medicina preventiva
        """
        
        health_display = scrolledtext.ScrolledText(health_system_frame, height=22, width=100, 
                                                  bg='#1e2328', fg='#cccccc', font=('Arial', 10))
        health_display.pack(pady=10, padx=10, fill='both', expand=True)
        health_display.insert('1.0', health_info)
        
    def create_local_services_tab(self):
        """Tab de servicios locales"""
        services_frame = tk.Frame(self.notebook, bg='#0f1419')
        self.notebook.add(services_frame, text='🇨🇷 Servicios CR')
        
        # Servicios disponibles
        available_services_frame = tk.LabelFrame(services_frame, text="🏪 Servicios Locales Disponibles", 
                                                bg='#0f1419', fg='white', font=('Arial', 12, 'bold'))
        available_services_frame.pack(fill='x', padx=20, pady=10)
        
        services_grid = tk.Frame(available_services_frame, bg='#0f1419')
        services_grid.pack(pady=15, padx=15)
        
        # Servicios costarricenses
        local_services = [
            ("🛒 Supermercados", "AutoMercado, MasXMenos", "Delivery disponible", '#00d4aa'),
            ("🍕 Restaurantes", "Comida típica y internacional", "Pedidos online", '#ff6b6b'),
            ("🚗 Transporte", "Uber, taxi, bus", "Rutas optimizadas", '#4a9eff'),
            ("🏥 Salud", "Clínicas, farmacias", "Telemedicina", '#ffd700'),
            ("💼 Servicios", "Plomería, electricidad", "Profesionales verificados", '#9b59b6'),
            ("🎓 Educación", "Tutorías, cursos", "Modalidad virtual/presencial", '#ff9f43')
        ]
        
        row, col = 0, 0
        for service, providers, feature, color in local_services:
            service_card = tk.Frame(services_grid, bg='#1e2328', relief='raised', bd=2)
            service_card.grid(row=row, column=col, padx=8, pady=8, sticky='nsew')
            
            tk.Label(service_card, text=service, font=('Arial', 11, 'bold'), 
                    fg=color, bg='#1e2328').pack(pady=5)
            
            tk.Label(service_card, text=providers, font=('Arial', 9), 
                    fg='#cccccc', bg='#1e2328', wraplength=150, justify=tk.CENTER).pack(pady=2)
            
            tk.Label(service_card, text=feature, font=('Arial', 8), 
                    fg='#888888', bg='#1e2328').pack(pady=2)
            
            tk.Button(service_card, text="🔍 Explorar", 
                     command=lambda s=service: self.explore_service(s),
                     bg=color, fg='white' if color not in ['#ffd700'] else 'black', 
                     font=('Arial', 8, 'bold')).pack(pady=5)
            
            col += 1
            if col > 2:
                col = 0
                row += 1
                
        # Configurar grid
        for i in range(3):
            services_grid.columnconfigure(i, weight=1)
            
        # Integración con Costa Rica
        cr_integration_frame = tk.LabelFrame(services_frame, text="🇨🇷 Integración Nacional", 
                                            bg='#0f1419', fg='white', font=('Arial', 12, 'bold'))
        cr_integration_frame.pack(fill='both', expand=True, padx=20, pady=10)
        
        cr_info = """
🇨🇷 NEXUSOPTIM IA - INTEGRADO CON COSTA RICA

🏛️ SERVICIOS GUBERNAMENTALES:
• AyA - Monitoreo de agua potable
• ICE - Gestión de electricidad y telecomunicaciones
• CCSS - Servicios de salud integrados
• Ministerio de Educación - Currículo oficial
• MOPT - Información de tránsito en tiempo real
• Registro Nacional - Trámites digitales

🏪 COMERCIO LOCAL:
• SINPE Móvil - Pagos instantáneos
• Facturas electrónicas automáticas
• Comparación de precios en tiempo real
• Promociones y descuentos locales
• Soporte a PYMES costarricenses

🌿 TURISMO Y CULTURA:
• Parques Nacionales - Reservas online
• Eventos culturales locales
• Festivales y celebraciones
• Tours virtuales de Costa Rica
• Promoción del turismo interno

📱 TECNOLOGÍA NACIONAL:
• Integración con startups locales
• Soporte a desarrolladores ticos
• Promoción de talento nacional
• Colaboración con universidades CR
• Impulso a la economía digital

🌍 IMPACTO SOCIAL:
• Programa de inclusión digital
• Acceso gratuito para familias de escasos recursos
• Capacitación tecnológica comunitaria
• Apoyo a adultos mayores
• Reducción de brecha digital

📊 DATOS Y PRIVACIDAD:
• Datos almacenados en territorio nacional
• Cumplimiento con leyes costarricenses
• Transparencia total en uso de información
• Control familiar de privacidad
• Seguridad certificada nacionalmente

🎯 MISIÓN NACIONAL:
"Democratizar el acceso a la inteligencia artificial en todos los hogares 
costarricenses, fortaleciendo la educación, mejorando la calidad de vida 
familiar y promoviendo el desarrollo tecnológico nacional."

💡 VISIÓN 2030:
"Costa Rica como líder centroamericano en adopción de IA doméstica,
con NexusOptim IA presente en el 90% de los hogares nacionales,
contribuyendo al desarrollo humano y la competitividad del país."

🏆 COMPROMISO SOCIAL:
• 100% de escuelas públicas con acceso gratuito
• Programa especial para comunidades rurales
• Soporte técnico en español costarricense
• Respaldo de garantía nacional
• Contribución al PIB tecnológico nacional
        """
        
        cr_display = scrolledtext.ScrolledText(cr_integration_frame, height=25, width=100, 
                                              bg='#1e2328', fg='#cccccc', font=('Arial', 10))
        cr_display.pack(pady=10, padx=10, fill='both', expand=True)
        cr_display.insert('1.0', cr_info)
        
    def create_damage_reports_tab(self):
        """Tab de reportes de averías de infraestructura"""
        reports_frame = tk.Frame(self.notebook, bg='#0f1419')
        self.notebook.add(reports_frame, text='🚨 Reportes Averías')
        
        # Header de emergencia
        emergency_header = tk.Frame(reports_frame, bg='#ff4444', height=60)
        emergency_header.pack(fill='x', pady=0)
        emergency_header.pack_propagate(False)
        
        emergency_label = tk.Label(emergency_header, 
                                  text="🚨 SISTEMA DE REPORTES DE AVERÍAS - INFRAESTRUCTURA NACIONAL 🇨🇷", 
                                  font=('Arial', 14, 'bold'), fg='white', bg='#ff4444')
        emergency_label.pack(expand=True)
        
        # Botones de reporte rápido
        quick_buttons_frame = tk.LabelFrame(reports_frame, text="⚡ Reportes Rápidos de Emergencia", 
                                           bg='#0f1419', fg='white', font=('Arial', 12, 'bold'))
        quick_buttons_frame.pack(fill='x', padx=20, pady=10)
        
        buttons_grid = tk.Frame(quick_buttons_frame, bg='#0f1419')
        buttons_grid.pack(pady=15, padx=15)
        
        # Tipos de averías críticas
        emergency_types = [
            ("⚡", "Transformador Averiado", "Transformador eléctrico dañado o en llamas", '#ff4444'),
            ("🔌", "Cableado Peligroso", "Cables caídos o expuestos peligrosos", '#ff6b00'),
            ("💧", "Fuga de Agua", "Tubería rota o fuga masiva de agua", '#4a9eff'),
            ("🚗", "Choque vs Poste", "Accidente vehicular contra infraestructura", '#ff0066'),
            ("🔥", "Incendio Eléctrico", "Fuego en instalaciones eléctricas", '#cc0000'),
            ("📡", "Torre Comunicaciones", "Daño en antenas o torres telecomunicaciones", '#9b59b6')
        ]
        
        row, col = 0, 0
        for icon, title, desc, color in emergency_types:
            emergency_btn = tk.Button(buttons_grid, 
                                    text=f"{icon}\n{title}", 
                                    command=lambda t=title, d=desc: self.quick_damage_report(t, d),
                                    bg=color, fg='white', 
                                    font=('Arial', 10, 'bold'),
                                    width=18, height=4)
            emergency_btn.grid(row=row, column=col, padx=8, pady=8, sticky='nsew')
            
            col += 1
            if col > 2:
                col = 0
                row += 1
                
        # Configurar grid
        for i in range(3):
            buttons_grid.columnconfigure(i, weight=1)
            
        # Formulario detallado de reporte
        detailed_form_frame = tk.LabelFrame(reports_frame, text="📋 Reporte Detallado de Avería", 
                                           bg='#0f1419', fg='white', font=('Arial', 12, 'bold'))
        detailed_form_frame.pack(fill='both', expand=True, padx=20, pady=10)
        
        form_container = tk.Frame(detailed_form_frame, bg='#0f1419')
        form_container.pack(fill='both', expand=True, padx=15, pady=15)
        
        # Lado izquierdo - Formulario
        left_form = tk.Frame(form_container, bg='#0f1419')
        left_form.pack(side='left', fill='both', expand=True, padx=(0, 10))
        
        # Tipo de avería
        tk.Label(left_form, text="🔧 Tipo de Avería:", bg='#0f1419', fg='white', 
                font=('Arial', 11, 'bold')).pack(anchor='w', pady=(5, 2))
        
        self.damage_type_var = tk.StringVar(value='Transformador')
        damage_types = ['Transformador', 'Cableado Eléctrico', 'Tubería de Agua', 
                       'Poste de Electricidad', 'Semáforo', 'Torre de Comunicaciones',
                       'Alcantarillado', 'Alumbrado Público', 'Otro']
        
        damage_type_combo = ttk.Combobox(left_form, textvariable=self.damage_type_var, 
                                        values=damage_types, width=40)
        damage_type_combo.pack(pady=(0, 10), fill='x')
        
        # Ubicación
        tk.Label(left_form, text="📍 Ubicación Exacta:", bg='#0f1419', fg='white', 
                font=('Arial', 11, 'bold')).pack(anchor='w', pady=(5, 2))
        
        self.location_entry = tk.Entry(left_form, font=('Arial', 10), width=50)
        self.location_entry.pack(pady=(0, 10), fill='x')
        self.location_entry.insert(0, "Ej: 200m sur de la iglesia de San Pedro, Montes de Oca")
        
        # Descripción detallada
        tk.Label(left_form, text="📝 Descripción Detallada:", bg='#0f1419', fg='white', 
                font=('Arial', 11, 'bold')).pack(anchor='w', pady=(5, 2))
        
        self.description_text = scrolledtext.ScrolledText(left_form, height=8, width=50, 
                                                         bg='#1e2328', fg='#cccccc', 
                                                         font=('Arial', 10))
        self.description_text.pack(pady=(0, 10), fill='both', expand=True)
        self.description_text.insert('1.0', "Describa detalladamente el problema observado...")
        
        # Lado derecho - Información del reportante
        right_form = tk.Frame(form_container, bg='#0f1419')
        right_form.pack(side='right', fill='y', padx=(10, 0))
        
        # Información del reportante
        reporter_frame = tk.LabelFrame(right_form, text="👤 Información del Reportante", 
                                      bg='#0f1419', fg='#00d4aa', font=('Arial', 11, 'bold'))
        reporter_frame.pack(fill='x', pady=(0, 15))
        
        tk.Label(reporter_frame, text="Nombre:", bg='#0f1419', fg='white', 
                font=('Arial', 10)).pack(anchor='w', pady=(10, 2), padx=10)
        
        self.reporter_name_entry = tk.Entry(reporter_frame, font=('Arial', 10), width=25)
        self.reporter_name_entry.pack(pady=(0, 5), padx=10, fill='x')
        
        tk.Label(reporter_frame, text="Teléfono:", bg='#0f1419', fg='white', 
                font=('Arial', 10)).pack(anchor='w', pady=(5, 2), padx=10)
        
        self.reporter_phone_entry = tk.Entry(reporter_frame, font=('Arial', 10), width=25)
        self.reporter_phone_entry.pack(pady=(0, 10), padx=10, fill='x')
        
        # Prioridad
        priority_frame = tk.LabelFrame(right_form, text="🚨 Nivel de Urgencia", 
                                      bg='#0f1419', fg='#ff6b6b', font=('Arial', 11, 'bold'))
        priority_frame.pack(fill='x', pady=(0, 15))
        
        self.priority_var = tk.StringVar(value='Media')
        priorities = [
            ('🔴 CRÍTICA - Peligro inmediato', 'Crítica'),
            ('🟡 ALTA - Requiere atención pronto', 'Alta'), 
            ('🟢 MEDIA - No es urgente', 'Media')
        ]
        
        for text, value in priorities:
            tk.Radiobutton(priority_frame, text=text, variable=self.priority_var, 
                          value=value, bg='#0f1419', fg='white', 
                          selectcolor='#1e2328', font=('Arial', 9)).pack(anchor='w', pady=2, padx=10)
        
        # Botones de acción
        action_buttons = tk.Frame(right_form, bg='#0f1419')
        action_buttons.pack(fill='x', pady=(15, 0))
        
        tk.Button(action_buttons, text="📤 ENVIAR REPORTE", 
                 command=self.submit_damage_report,
                 bg='#00d4aa', fg='black', font=('Arial', 11, 'bold')).pack(fill='x', pady=5)
        
        tk.Button(action_buttons, text="📋 Ver Mis Reportes", 
                 command=self.view_my_reports,
                 bg='#4a9eff', fg='white', font=('Arial', 10, 'bold')).pack(fill='x', pady=2)
        
        tk.Button(action_buttons, text="🗂️ Limpiar Formulario", 
                 command=self.clear_form,
                 bg='#666666', fg='white', font=('Arial', 10)).pack(fill='x', pady=2)
        
        # Status de reportes recientes
        status_frame = tk.LabelFrame(reports_frame, text="📊 Estado de Reportes Recientes", 
                                    bg='#0f1419', fg='white', font=('Arial', 12, 'bold'))
        status_frame.pack(fill='x', padx=20, pady=(0, 20))
        
        self.reports_status_text = scrolledtext.ScrolledText(status_frame, height=6, width=100, 
                                                            bg='#1e2328', fg='#cccccc', 
                                                            font=('Arial', 9))
        self.reports_status_text.pack(pady=10, padx=10, fill='x')
        
        # Cargar reportes existentes
        self.load_recent_reports()
        
    def update_education_content(self, event=None):
        """Actualizar contenido educativo según miembro seleccionado"""
        member_name = self.education_member_var.get()
        
        # Buscar miembro
        member = next((m for m in self.family_config['family_members'] if m['name'] == member_name), None)
        if not member:
            return
            
        # Contenido personalizado por edad
        if member['age'] <= 12:  # Niños
            content = f"""
🎓 CONTENIDO EDUCATIVO PERSONALIZADO - {member['name']} ({member['age']} años)

📚 MATERIAS PRINCIPALES:
• Matemáticas: Operaciones básicas, geometría divertida
• Español: Lectura comprensiva, escritura creativa
• Ciencias: Experimentos seguros, naturaleza de CR
• Estudios Sociales: Historia costarricense, geografía
• Inglés: Vocabulario básico, canciones educativas
• Arte: Dibujo digital, manualidades recicladas

🎮 JUEGOS EDUCATIVOS:
• Aventuras Matemáticas en Costa Rica
• Explorador de la Biodiversidad Tica
• Constructor de Oraciones Divertidas
• Geografía Interactiva CR
• Ciencia Experimental Virtual

📖 LECTURAS RECOMENDADAS:
• Cuentos de la tradición costarricense
• Historias de animales del bosque tropical
• Aventuras de niños exploradores
• Fábulas con valores familiares

🎯 OBJETIVOS DE APRENDIZAJE:
• Desarrollar amor por el aprendizaje
• Fortalecer habilidades básicas
• Promover curiosidad científica
• Valorar la cultura costarricense
            """
        elif member['age'] <= 18:  # Adolescentes
            content = f"""
🎓 CONTENIDO EDUCATIVO PERSONALIZADO - {member['name']} ({member['age']} años)

📚 MATERIAS SECUNDARIA:
• Matemáticas: Álgebra, geometría, estadística
• Español: Literatura, análisis de textos, redacción
• Ciencias: Biología, química, física aplicada
• Estudios Sociales: Historia mundial, economía
• Inglés: Conversación avanzada, preparación TOEFL
• Tecnología: Programación, robótica, IA básica

💼 PREPARACIÓN UNIVERSITARIA:
• Orientación vocacional personalizada
• Preparación para exámenes de admisión
• Desarrollo de habilidades de estudio
• Proyectos de investigación científica

🌟 HABILIDADES DEL SIGLO XXI:
• Pensamiento crítico y creatividad
• Colaboración y comunicación
• Competencia digital avanzada
• Liderazgo y emprendimiento

🎯 METAS EDUCATIVAS:
• Excelencia académica
• Preparación universitaria
• Desarrollo personal integral
• Conciencia social y ambiental
            """
        else:  # Adultos
            content = f"""
🎓 EDUCACIÓN CONTINUA - {member['name']} ({member['age']} años)

📈 DESARROLLO PROFESIONAL:
• Cursos de actualización laboral
• Certificaciones tecnológicas
• Habilidades de liderazgo
• Emprendimiento e innovación

🧠 APRENDIZAJE PERSONAL:
• Nuevos idiomas (francés, mandarín)
• Habilidades digitales avanzadas
• Cultura general y arte
• Salud y bienestar personal

👨‍👩‍👧‍👦 EDUCACIÓN FAMILIAR:
• Técnicas de crianza positiva
• Comunicación familiar efectiva
• Gestión financiera del hogar
• Tecnología para la familia

🌱 CRECIMIENTO PERSONAL:
• Inteligencia emocional
• Mindfulness y meditación
• Creatividad y expresión artística
• Propósito de vida y valores
            """
            
        self.education_content.delete('1.0', tk.END)
        self.education_content.insert('1.0', content)
        
    def create_family_lesson(self):
        """Crear lección personalizada para la familia"""
        member = self.education_member_var.get()
        
        messagebox.showinfo("🎓 Lección Personalizada", 
                           f"✨ Creando lección personalizada para {member}\n\n"
                           f"🤖 La IA está analizando:\n"
                           f"• Perfil de aprendizaje individual\n"
                           f"• Intereses y pasatiempos\n"
                           f"• Nivel educativo actual\n"
                           f"• Objetivos familiares\n\n"
                           f"📚 Lección lista en 30 segundos...")
        
        # Log actividad
        self.log_family_activity(member, 'education', f'Lección personalizada creada')
        
    def show_education_progress(self):
        """Mostrar progreso educativo"""
        member = self.education_member_var.get()
        
        progress_window = tk.Toplevel(self.root)
        progress_window.title(f"📊 Progreso Educativo - {member}")
        progress_window.geometry("600x500")
        progress_window.configure(bg='#1e2328')
        
        progress_info = f"""
📊 REPORTE DE PROGRESO EDUCATIVO

👤 Estudiante: {member}
📅 Período: Noviembre 2024

📈 RENDIMIENTO GENERAL: 92%

📚 MATERIAS:
• Matemáticas: 95% - Excelente
• Español: 88% - Muy bien  
• Ciencias: 94% - Excelente
• Inglés: 90% - Muy bien
• Estudios Sociales: 87% - Bien

⭐ FORTALEZAS IDENTIFICADAS:
• Resolución de problemas matemáticos
• Creatividad en escritura
• Curiosidad científica
• Participación activa

🎯 ÁREAS DE MEJORA:
• Concentración en lecturas largas
• Organización de tiempo de estudio
• Participación en actividades grupales

🏆 LOGROS RECIENTES:
• Proyecto de ciencias destacado
• Mejora significativa en inglés
• Liderazgo en actividades familiares

📋 RECOMENDACIONES IA:
• Aumentar tiempo de lectura recreativa
• Implementar técnicas de estudio visual
• Incluir más actividades colaborativas
• Continuar con enfoque práctico en ciencias
        """
        
        progress_label = tk.Label(progress_window, text=progress_info, 
                                 bg='#1e2328', fg='#cccccc', font=('Arial', 11), 
                                 justify=tk.LEFT)
        progress_label.pack(pady=20, padx=20, fill='both', expand=True)
        
    def launch_educational_games(self):
        """Lanzar juegos educativos"""
        games_window = tk.Toplevel(self.root)
        games_window.title("🎮 Juegos Educativos Familiares")
        games_window.geometry("800x600")
        games_window.configure(bg='#1e2328')
        
        games_info = """
🎮 BIBLIOTECA DE JUEGOS EDUCATIVOS

👨‍👩‍👧‍👦 JUEGOS FAMILIARES:
• Quiz Costa Rica - Conocimiento nacional
• Matemáticas en Equipo - Colaborativo
• Geografía Mundial - Exploración virtual
• Historia en Tiempo Real - Simulación

👦 PARA CARLOS (12 años):
• Laboratorio Virtual - Experimentos seguros
• Constructor de Robots - Programación básica  
• Aventura Matemática - RPG educativo
• Explorador Natural CR - Biodiversidad

👧 PARA ANA (16 años):
• Simulador Económico - Microeconomía
• Laboratorio de Química Virtual
• Debate Digital - Habilidades argumentativas
• Programadora Junior - Coding challenges

👨👩 PARA PAPÁS:
• Finanzas Familiares - Simulación
• Idiomas Express - Aprendizaje rápido
• Cultura General - Trivia avanzada
• Manejo del Tiempo - Productividad

🏆 COMPETENCIAS FAMILIARES:
• Torneo semanal de conocimientos
• Desafíos colaborativos mensuales
• Ranking familiar de logros
• Premios y reconocimientos virtuales
        """
        
        games_label = tk.Label(games_window, text=games_info, 
                              bg='#1e2328', fg='#cccccc', font=('Arial', 11), 
                              justify=tk.LEFT)
        games_label.pack(pady=20, padx=20, fill='both', expand=True)
        
    def show_entertainment_category(self, category):
        """Mostrar categoría de entretenimiento"""
        messagebox.showinfo(f"🎬 {category}", 
                           f"🎯 Abriendo recomendaciones de {category}\n\n"
                           f"🤖 Personalizadas para toda la familia\n"
                           f"📊 Basadas en preferencias y edades\n"
                           f"🇨🇷 Contenido costarricense incluido")
        
    def control_device(self, device):
        """Controlar dispositivo del hogar"""
        messagebox.showinfo(f"⚙️ Control {device}", 
                           f"🏠 Panel de control para {device}\n\n"
                           f"✅ Dispositivo conectado\n"
                           f"🔧 Configuraciones disponibles\n"
                           f"📱 Control desde cualquier dispositivo\n"
                           f"🤖 Automatización inteligente activa")
        
    def show_health_details(self, member):
        """Mostrar detalles de salud"""
        health_window = tk.Toplevel(self.root)
        health_window.title(f"💓 Salud - {member}")
        health_window.geometry("500x400")
        health_window.configure(bg='#1e2328')
        
        health_details = f"""
💓 REPORTE DE SALUD DETALLADO

👤 {member}
📅 Última actualización: Hoy

📊 MÉTRICAS VITALES:
• Ritmo cardíaco: 72 bpm (Normal)
• Presión arterial: 120/80 (Óptima)
• Peso: Estable
• Actividad física: Excelente

🏃‍♂️ ACTIVIDAD SEMANAL:
• Pasos diarios: 8,500 promedio
• Ejercicio: 45 min/día
• Descanso: 7.5 horas/noche
• Hidratación: Adecuada

💊 RECORDATORIOS:
• Examen médico anual: En 2 meses
• Vacunas al día: ✅
• Control dental: Programado

🎯 RECOMENDACIONES:
• Continuar rutina actual
• Aumentar consumo de vegetales
• Mantener horario de sueño
• Revisión preventiva próxima
        """
        
        health_label = tk.Label(health_window, text=health_details, 
                               bg='#1e2328', fg='#cccccc', font=('Arial', 11), 
                               justify=tk.LEFT)
        health_label.pack(pady=20, padx=20, fill='both', expand=True)
        
    def explore_service(self, service):
        """Explorar servicio local"""
        messagebox.showinfo(f"🔍 {service}", 
                           f"🇨🇷 Explorando {service} en tu área\n\n"
                           f"📍 Servicios cerca de {self.family_config['location']}\n"
                           f"⭐ Calificaciones y reseñas\n"
                           f"💰 Comparación de precios\n"
                           f"📱 Contacto directo disponible")
        
    def log_family_activity(self, member, activity_type, description):
        """Registrar actividad familiar en BD"""
        try:
            conn = sqlite3.connect(self.db_path)
            cursor = conn.cursor()
            
            cursor.execute('''
                INSERT INTO family_activities (member_name, activity_type, description)
                VALUES (?, ?, ?)
            ''', (member, activity_type, description))
            
            conn.commit()
            conn.close()
            
        except Exception as e:
            print(f"Error logging activity: {e}")
            
    def show_startup_banners(self):
        """Mostrar banners de bienvenida al iniciar"""
        # Banner principal de bienvenida
        banner_window = tk.Toplevel(self.root)
        banner_window.title("🇨🇷 NexusOptim IA - Bienvenida")
        banner_window.geometry("800x600")
        banner_window.configure(bg='#0f1419')
        banner_window.resizable(False, False)
        
        # Centrar ventana
        banner_window.transient(self.root)
        banner_window.grab_set()
        
        # Canvas para animaciones
        canvas = Canvas(banner_window, width=800, height=600, bg='#0f1419', highlightthickness=0)
        canvas.pack(fill='both', expand=True)
        
        # Banner principal animado
        canvas.create_rectangle(0, 0, 800, 150, fill='#00d4aa', outline='')
        canvas.create_text(400, 50, text="🇨🇷 NEXUSOPTIM IA", font=('Arial', 28, 'bold'), fill='black')
        canvas.create_text(400, 90, text="HOGAR INTELIGENTE COSTARRICENSE", font=('Arial', 16, 'bold'), fill='#0f1419')
        canvas.create_text(400, 120, text="¡Pura Vida Tecnológica!", font=('Arial', 12), fill='#0f1419')
        
        # Información de bienvenida
        welcome_text = """
🏠 ¡BIENVENIDA FAMILIA COSTARRICENSE!

✨ Tu hogar ahora es más inteligente con NexusOptim IA
🤖 Asistente familiar personalizado activado
📚 Educación personalizada para toda la familia
🏡 Automatización del hogar configurada
💰 Gestión financiera familiar inteligente
🏥 Monitoreo de salud y bienestar familiar
🇨🇷 Servicios locales de Costa Rica integrados

🆕 NUEVAS CARACTERÍSTICAS:
🚨 Sistema de reportes de averías de infraestructura
⚡ Reporta transformadores, cableado, fugas y más
📞 Conexión directa con servicios de emergencia
🔧 Seguimiento en tiempo real de reparaciones

🎯 MISIÓN: Democratizar la IA en todos los hogares de Costa Rica
🚀 VISIÓN: Costa Rica líder mundial en hogares inteligentes

        """
        
        canvas.create_text(400, 380, text=welcome_text, font=('Arial', 11), fill='white', justify='center')
        
        # Botones de acción
        def close_banner():
            banner_window.destroy()
            
        def show_tour():
            banner_window.destroy()
            self.show_guided_tour()
            
        close_btn = tk.Button(banner_window, text="✅ Continuar al Hogar", 
                             command=close_banner,
                             bg='#00d4aa', fg='black', font=('Arial', 12, 'bold'))
        close_btn.place(x=500, y=550, width=200, height=40)
        
        tour_btn = tk.Button(banner_window, text="🎯 Tour Guiado", 
                            command=show_tour,
                            bg='#4a9eff', fg='white', font=('Arial', 12, 'bold'))
        tour_btn.place(x=100, y=550, width=200, height=40)
        
        # Auto-close después de 8 segundos
        banner_window.after(8000, close_banner)
        
    def show_guided_tour(self):
        """Mostrar tour guiado de características"""
        tour_window = tk.Toplevel(self.root)
        tour_window.title("🎯 Tour Guiado - NexusOptim IA")
        tour_window.geometry("700x500")
        tour_window.configure(bg='#1e2328')
        
        tour_info = """
🎯 TOUR GUIADO - NEXUSOPTIM IA HOGAR INTELIGENTE

📱 NAVEGACIÓN PRINCIPAL:
• 🏠 Casa: Dashboard familiar principal
• 🎓 Educación: Contenido personalizado por edad
• 🎬 Entretenimiento: Recomendaciones familiares
• 🏠 Casa Inteligente: Control de dispositivos
• 💰 Finanzas: Gestión económica familiar
• 🏥 Salud: Bienestar de toda la familia
• 🇨🇷 Servicios CR: Comercios y servicios locales
• 🚨 Reportes Averías: ¡NUEVA FUNCIÓN!

🚨 SISTEMA DE REPORTES DE AVERÍAS:
• Reporta transformadores dañados ⚡
• Cableado peligroso expuesto 🔌
• Fugas de agua masivas 💧
• Choques contra postes 🚗
• Incendios eléctricos 🔥
• Torres de comunicaciones 📡

📞 CONEXIÓN AUTOMÁTICA:
• ICE - Electricidad y telecomunicaciones
• AyA - Servicios de agua
• Municipalidades - Infraestructura local
• Servicios de emergencia - 911
• Tránsito - Accidentes vehiculares

🔄 SEGUIMIENTO EN TIEMPO REAL:
• Estado: Pendiente → En proceso → Resuelto
• Técnico asignado y tiempo estimado
• Notificaciones de progreso
• Historial completo de reportes

💡 CONSEJOS DE USO:
1. Mantén actualizada tu información de contacto
2. Sé específico con las ubicaciones
3. Usa fotos si es posible (próximamente)
4. Reporta solo averías reales para no saturar
5. Prioriza correctamente la urgencia

🆘 EMERGENCIAS CRÍTICAS:
Para peligro inmediato de vida, llama al 911
NexusOptim IA complementa pero no reemplaza emergencias
        """
        
        tour_label = tk.Label(tour_window, text=tour_info, bg='#1e2328', fg='white', 
                             font=('Arial', 10), justify=tk.LEFT)
        tour_label.pack(pady=20, padx=20, fill='both', expand=True)
        
        tk.Button(tour_window, text="✅ Entendido, ¡Empecemos!", 
                 command=tour_window.destroy,
                 bg='#00d4aa', fg='black', font=('Arial', 12, 'bold')).pack(pady=20)
        
    def quick_damage_report(self, damage_type, description):
        """Reporte rápido de avería"""
        # Pre-llenar formulario
        self.damage_type_var.set(damage_type.split(' ')[0])  # Primera palabra
        self.description_text.delete('1.0', tk.END)
        self.description_text.insert('1.0', f"REPORTE RÁPIDO: {description}\n\nDetalle adicional:")
        self.priority_var.set('Crítica')
        
        # Enfocar el notebook en la tab de reportes
        self.notebook.select(7)  # Tab de reportes (índice 7)
        
        messagebox.showinfo("🚨 Reporte Rápido", 
                           f"Formulario pre-configurado para:\n{damage_type}\n\n"
                           f"Por favor complete:\n"
                           f"• Ubicación exacta\n"
                           f"• Sus datos de contacto\n"
                           f"• Detalles adicionales\n\n"
                           f"Luego presione 'ENVIAR REPORTE'")
        
    def submit_damage_report(self):
        """Enviar reporte de avería"""
        # Validar campos obligatorios
        if not self.location_entry.get() or self.location_entry.get().startswith("Ej:"):
            messagebox.showerror("Error", "Por favor ingrese la ubicación exacta")
            return
            
        if not self.reporter_name_entry.get():
            messagebox.showerror("Error", "Por favor ingrese su nombre")
            return
            
        if not self.reporter_phone_entry.get():
            messagebox.showerror("Error", "Por favor ingrese su teléfono")
            return
            
        # Generar ID único de reporte
        report_id = f"CR-{uuid.uuid4().hex[:8].upper()}"
        
        # Datos del reporte
        report_data = {
            'report_id': report_id,
            'report_type': self.damage_type_var.get(),
            'location': self.location_entry.get(),
            'description': self.description_text.get('1.0', tk.END).strip(),
            'priority': self.priority_var.get(),
            'reporter_name': self.reporter_name_entry.get(),
            'contact_info': self.reporter_phone_entry.get(),
            'coordinates': f"{self.family_config['location']} - GPS: Pendiente",  # Simulated
            'status': 'pendiente',
            'estimated_repair_time': self.estimate_repair_time()
        }
        
        # Guardar en base de datos
        try:
            conn = sqlite3.connect(self.db_path)
            cursor = conn.cursor()
            
            cursor.execute('''
                INSERT INTO damage_reports 
                (report_id, report_type, location, description, priority, 
                 reporter_name, contact_info, coordinates, status, estimated_repair_time)
                VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
            ''', (report_data['report_id'], report_data['report_type'], 
                  report_data['location'], report_data['description'], 
                  report_data['priority'], report_data['reporter_name'],
                  report_data['contact_info'], report_data['coordinates'],
                  report_data['status'], report_data['estimated_repair_time']))
            
            conn.commit()
            conn.close()
            
            # Mostrar confirmación
            messagebox.showinfo("✅ Reporte Enviado", 
                               f"Reporte registrado exitosamente\n\n"
                               f"🆔 ID: {report_id}\n"
                               f"🔧 Tipo: {report_data['report_type']}\n"
                               f"📍 Ubicación: {report_data['location'][:50]}...\n"
                               f"🚨 Prioridad: {report_data['priority']}\n"
                               f"⏱️ Tiempo estimado: {report_data['estimated_repair_time']}\n\n"
                               f"📞 Recibirá notificaciones al: {report_data['contact_info']}\n"
                               f"🔄 Estado: En revisión por técnicos\n\n"
                               f"¡Gracias por ayudar a mejorar Costa Rica!")
            
            # Limpiar formulario
            self.clear_form()
            
            # Actualizar lista de reportes
            self.load_recent_reports()
            
            # Simular notificación a autoridades
            self.simulate_authority_notification(report_data)
            
        except Exception as e:
            messagebox.showerror("Error", f"Error al guardar reporte:\n{e}")
            
    def estimate_repair_time(self):
        """Estimar tiempo de reparación según tipo"""
        damage_type = self.damage_type_var.get()
        priority = self.priority_var.get()
        
        repair_times = {
            'Transformador': {'Crítica': '2-4 horas', 'Alta': '4-8 horas', 'Media': '1-2 días'},
            'Cableado Eléctrico': {'Crítica': '1-2 horas', 'Alta': '2-4 horas', 'Media': '4-8 horas'},
            'Tubería de Agua': {'Crítica': '30min-2h', 'Alta': '2-4 horas', 'Media': '4-8 horas'},
            'Poste de Electricidad': {'Crítica': '3-6 horas', 'Alta': '6-12 horas', 'Media': '1-3 días'},
            'Semáforo': {'Crítica': '1-2 horas', 'Alta': '2-4 horas', 'Media': '4-8 horas'},
            'Torre de Comunicaciones': {'Crítica': '4-8 horas', 'Alta': '8-16 horas', 'Media': '1-3 días'},
            'Alcantarillado': {'Crítica': '2-4 horas', 'Alta': '4-8 horas', 'Media': '1-2 días'},
            'Alumbrado Público': {'Crítica': '1-2 horas', 'Alta': '2-6 horas', 'Media': '6-12 horas'},
            'Otro': {'Crítica': '2-4 horas', 'Alta': '4-8 horas', 'Media': '1-2 días'}
        }
        
        return repair_times.get(damage_type, repair_times['Otro']).get(priority, '4-8 horas')
        
    def simulate_authority_notification(self, report_data):
        """Simular notificación a autoridades competentes"""
        authority_map = {
            'Transformador': 'ICE - Electricidad',
            'Cableado Eléctrico': 'ICE - Electricidad', 
            'Tubería de Agua': 'AyA - Acueductos y Alcantarillados',
            'Poste de Electricidad': 'ICE - Electricidad',
            'Semáforo': 'COSEVI - Tránsito',
            'Torre de Comunicaciones': 'ICE - Telecomunicaciones',
            'Alcantarillado': 'AyA - Acueductos y Alcantarillados',
            'Alumbrado Público': 'Municipalidad Local',
            'Otro': 'Servicios de Emergencia'
        }
        
        authority = authority_map.get(report_data['report_type'], 'Servicios Generales')
        
        # Simular envío
        threading.Thread(target=self.async_authority_notification, 
                        args=(report_data, authority), daemon=True).start()
        
    def async_authority_notification(self, report_data, authority):
        """Notificación asíncrona a autoridades"""
        time.sleep(2)  # Simular procesamiento
        
        print(f"\n📡 NOTIFICACIÓN ENVIADA A {authority.upper()}")
        print(f"🆔 Reporte: {report_data['report_id']}")
        print(f"🔧 Tipo: {report_data['report_type']}")
        print(f"📍 Ubicación: {report_data['location']}")
        print(f"🚨 Prioridad: {report_data['priority']}")
        print(f"👤 Reportante: {report_data['reporter_name']}")
        print(f"📞 Contacto: {report_data['contact_info']}")
        print("✅ Técnicos serán despachados según disponibilidad\n")
        
    def view_my_reports(self):
        """Ver reportes del usuario"""
        reports_window = tk.Toplevel(self.root)
        reports_window.title("📋 Mis Reportes de Averías")
        reports_window.geometry("800x600")
        reports_window.configure(bg='#1e2328')
        
        # Cargar reportes
        try:
            conn = sqlite3.connect(self.db_path)
            cursor = conn.cursor()
            
            cursor.execute('''
                SELECT report_id, report_type, location, priority, status, 
                       timestamp, estimated_repair_time
                FROM damage_reports 
                ORDER BY timestamp DESC
                LIMIT 20
            ''')
            
            reports = cursor.fetchall()
            conn.close()
            
            if not reports:
                tk.Label(reports_window, text="📋 No tienes reportes registrados", 
                        bg='#1e2328', fg='white', font=('Arial', 14)).pack(pady=50)
                return
                
            # Mostrar reportes en tabla
            reports_text = scrolledtext.ScrolledText(reports_window, width=90, height=30,
                                                    bg='#0f1419', fg='white', font=('Courier', 10))
            reports_text.pack(pady=20, padx=20, fill='both', expand=True)
            
            header = "ID REPORTE    | TIPO              | UBICACIÓN                    | PRIORIDAD | ESTADO     | FECHA/HORA        | T. ESTIMADO\n"
            header += "=" * 130 + "\n"
            reports_text.insert('1.0', header)
            
            for report in reports:
                report_id, report_type, location, priority, status, timestamp, est_time = report
                
                # Truncar textos largos
                location_short = location[:25] + "..." if len(location) > 25 else location
                
                # Color según estado
                status_display = status.upper()
                if status == 'pendiente':
                    status_display = f"🟡 {status_display}"
                elif status == 'en_proceso':
                    status_display = f"🔵 EN PROCESO"
                elif status == 'resuelto':
                    status_display = f"🟢 RESUELTO"
                    
                line = f"{report_id:<12} | {report_type:<16} | {location_short:<27} | {priority:<9} | {status_display:<10} | {timestamp[:16]:<17} | {est_time}\n"
                reports_text.insert(tk.END, line)
                
        except Exception as e:
            tk.Label(reports_window, text=f"Error cargando reportes: {e}", 
                    bg='#1e2328', fg='red', font=('Arial', 12)).pack(pady=50)
        
    def clear_form(self):
        """Limpiar formulario de reportes"""
        self.damage_type_var.set('Transformador')
        self.location_entry.delete(0, tk.END)
        self.location_entry.insert(0, "Ej: 200m sur de la iglesia de San Pedro, Montes de Oca")
        self.description_text.delete('1.0', tk.END)
        self.description_text.insert('1.0', "Describa detalladamente el problema observado...")
        self.reporter_name_entry.delete(0, tk.END)
        self.reporter_phone_entry.delete(0, tk.END)
        self.priority_var.set('Media')
        
    def load_recent_reports(self):
        """Cargar reportes recientes para mostrar estado"""
        try:
            conn = sqlite3.connect(self.db_path)
            cursor = conn.cursor()
            
            cursor.execute('''
                SELECT report_id, report_type, status, timestamp, estimated_repair_time
                FROM damage_reports 
                ORDER BY timestamp DESC
                LIMIT 10
            ''')
            
            reports = cursor.fetchall()
            conn.close()
            
            self.reports_status_text.delete('1.0', tk.END)
            
            if not reports:
                self.reports_status_text.insert('1.0', "📋 No hay reportes registrados aún.\n¡Sé el primero en reportar una avería para mejorar Costa Rica!")
                return
                
            status_text = "📊 ESTADO DE REPORTES RECIENTES:\n\n"
            
            for report in reports:
                report_id, report_type, status, timestamp, est_time = report
                
                status_emoji = "🟡" if status == 'pendiente' else "🔵" if status == 'en_proceso' else "🟢"
                status_text += f"{status_emoji} {report_id} | {report_type} | {status.upper()} | {timestamp[:16]} | ⏱️{est_time}\n"
                
            self.reports_status_text.insert('1.0', status_text)
            
        except Exception as e:
            self.reports_status_text.delete('1.0', tk.END)
            self.reports_status_text.insert('1.0', f"Error cargando reportes: {e}")
            
    def start_home_services(self):
        """Iniciar servicios del hogar"""
        def services_thread():
            while True:
                try:
                    # Simular actividades del hogar
                    time.sleep(30)
                    
                    activities = [
                        "🤖 IA optimizó temperatura del hogar",
                        "📱 Recordatorio familiar programado", 
                        "🔒 Sistema de seguridad verificado",
                        "💡 Luces ajustadas automáticamente",
                        "📊 Reporte de uso energético actualizado",
                        "🎵 Playlist familiar personalizada lista",
                        "🍽️ Sugerencia de menú saludable generada",
                        "📚 Nuevo contenido educativo disponible"
                    ]
                    
                    activity = random.choice(activities)
                    print(f"[{datetime.now().strftime('%H:%M:%S')}] {activity}")
                    
                    # Actualizar algún estado ocasionalmente
                    if random.random() < 0.3:
                        self.home_status['temperature'] = random.randint(22, 26)
                        self.home_status['energy_usage'] = random.randint(70, 95)
                        
                except Exception as e:
                    print(f"Error in home services: {e}")
                    time.sleep(60)
                    
        threading.Thread(target=services_thread, daemon=True).start()

def main():
    """Función principal de la versión doméstica"""
    try:
        app = NexusOptimHomeEdition()
        app.root.mainloop()
    except Exception as e:
        messagebox.showerror("Error", f"Error launching NexusOptim IA Home Edition:\n{e}")

if __name__ == "__main__":
    main()
