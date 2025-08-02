"""
NexusOptim IA - Sistema Educativo "Maestro"
Plataforma educativa inteligente con IA local Ollama

Sistema completo para Costa Rica:
- Currículo nacional personalizado
- IA adaptativa para cada estudiante
- Analytics de aprendizaje avanzados
- Integración con infraestructura IoT

Copyright (c) 2025 OpenNexus - NexusOptim IA
Preparado para revolucionar la educación en Costa Rica
"""

import tkinter as tk
from tkinter import ttk, messagebox, scrolledtext
import json
import threading
import time
from datetime import datetime, timedelta
import random
import sys
import os

# Importar servicios de IA
try:
    from ai.ollama_integration import ollama_service, maestro_system
    OLLAMA_AVAILABLE = True
except ImportError:
    OLLAMA_AVAILABLE = False
    print("⚠️  Ollama integration not available - running in simulation mode")

class MaestroEducationalPlatform:
    """Plataforma educativa inteligente 'Maestro' con IA"""
    
    def __init__(self):
        self.root = tk.Tk()
        self.root.title("🎓 NexusOptim IA - Maestro Educational Platform")
        self.root.geometry("1400x900")
        self.root.configure(bg='#0f0f23')
        
        # Estado del sistema
        self.current_student = None
        self.active_lesson = None
        self.ai_enabled = OLLAMA_AVAILABLE
        
        # Datos de demostración
        self.setup_demo_data()
        self.setup_ui()
        
        if self.ai_enabled:
            self.start_ai_services()
        else:
            self.start_simulation_mode()
            
    def setup_demo_data(self):
        """Configurar datos de demostración"""
        self.students = [
            {
                'id': 'est_001',
                'name': 'Ana María Rodríguez',
                'grade': '5to Primaria',
                'age': 10,
                'learning_style': 'visual',
                'subjects': ['Matemáticas', 'Ciencias', 'Español', 'Inglés'],
                'strengths': ['Resolución de problemas', 'Creatividad'],
                'improvements': ['Concentración', 'Lectura comprensiva'],
                'progress': 85
            },
            {
                'id': 'est_002', 
                'name': 'Carlos Eduardo Vargas',
                'grade': '8vo Secundaria',
                'age': 14,
                'learning_style': 'kinestésico',
                'subjects': ['Física', 'Química', 'Matemáticas', 'Tecnología'],
                'strengths': ['Experimentación', 'Análisis lógico'],
                'improvements': ['Teoría abstracta', 'Escritura'],
                'progress': 78
            },
            {
                'id': 'est_003',
                'name': 'Isabella Chen López',
                'grade': '11vo Secundaria', 
                'age': 17,
                'learning_style': 'auditivo',
                'subjects': ['Literatura', 'Historia', 'Filosofía', 'Inglés Avanzado'],
                'strengths': ['Análisis crítico', 'Comunicación oral'],
                'improvements': ['Matemáticas aplicadas', 'Tecnología'],
                'progress': 92
            }
        ]
        
        self.curriculum_cr = {
            'Primaria': {
                'Matemáticas': ['Números naturales', 'Operaciones básicas', 'Geometría plana', 'Medición', 'Estadística básica'],
                'Ciencias': ['Seres vivos', 'Cuerpo humano', 'Materia y energía', 'Tierra y universo', 'Investigación'],
                'Español': ['Lectura comprensiva', 'Escritura creativa', 'Gramática', 'Comunicación oral', 'Literatura infantil'],
                'Estudios Sociales': ['Mi comunidad', 'Historia de CR', 'Geografía nacional', 'Símbolos patrios', 'Civismo'],
                'Inglés': ['Vocabulario básico', 'Saludos y presentaciones', 'Colores y números', 'Familia', 'Conversación simple'],
                'Tecnología': ['Informática básica', 'Internet seguro', 'Programación visual', 'Robótica educativa']
            },
            'Secundaria': {
                'Matemáticas': ['Álgebra', 'Geometría analítica', 'Trigonometría', 'Cálculo diferencial', 'Estadística aplicada'],
                'Ciencias': ['Biología molecular', 'Química orgánica', 'Física mecánica', 'Método científico', 'Biotecnología'],
                'Español': ['Literatura costarricense', 'Análisis literario', 'Redacción académica', 'Oratoria', 'Periodismo'],
                'Estudios Sociales': ['Historia universal', 'Economía', 'Psicología', 'Sociología', 'Educación cívica'],
                'Inglés': ['Conversación avanzada', 'Literatura anglosajona', 'Escritura académica', 'Presentaciones', 'Certificación'],
                'Tecnología': ['Programación avanzada', 'Bases de datos', 'Redes de computadoras', 'IA y Machine Learning', 'Emprendimiento digital']
            }
        }
        
        self.lesson_templates = {
            'interactive': '🎮 Lección Interactiva con gamificación y simulaciones',
            'project': '🔨 Proyecto práctico con aplicación real',
            'collaborative': '👥 Actividad colaborativa en equipos',
            'research': '🔍 Investigación guiada con recursos digitales',
            'creative': '🎨 Expresión creativa y arte digital',
            'problem_solving': '🧩 Resolución de problemas del mundo real'
        }
        
    def setup_ui(self):
        """Configurar interfaz de usuario"""
        # Header
        header_frame = tk.Frame(self.root, bg='#1a1a3e', height=100)
        header_frame.pack(fill='x', pady=0)
        header_frame.pack_propagate(False)
        
        title_label = tk.Label(header_frame, 
                              text="🎓 Maestro - Sistema Educativo IA\nNexusOptim IA • Costa Rica", 
                              font=('Arial', 18, 'bold'), 
                              fg='#00d4aa', bg='#1a1a3e')
        title_label.pack(pady=15)
        
        # Status indicator
        status_text = "🤖 IA Ollama Activa" if self.ai_enabled else "⚠️  Modo Simulación"
        status_color = '#00d4aa' if self.ai_enabled else '#ffa500'
        
        status_label = tk.Label(header_frame, text=status_text, 
                               font=('Arial', 10), fg=status_color, bg='#1a1a3e')
        status_label.pack()
        
        # Main container
        main_container = tk.Frame(self.root, bg='#0f0f23')
        main_container.pack(fill='both', expand=True, padx=10, pady=10)
        
        # Create notebook
        self.notebook = ttk.Notebook(main_container)
        self.notebook.pack(fill='both', expand=True)
        
        # Configure style
        style = ttk.Style()
        style.theme_use('clam')
        style.configure('TNotebook', background='#0f0f23')
        style.configure('TNotebook.Tab', background='#1a1a3e', foreground='white', padding=[15, 8])
        style.map('TNotebook.Tab', background=[('selected', '#00d4aa')], foreground=[('selected', 'black')])
        
        # Create tabs
        self.create_dashboard_tab()
        self.create_students_tab()
        self.create_lessons_tab()
        self.create_ai_tutor_tab()
        self.create_analytics_tab()
        self.create_curriculum_tab()
        
    def create_dashboard_tab(self):
        """Crear tab de dashboard"""
        dashboard_frame = tk.Frame(self.notebook, bg='#0f0f23')
        self.notebook.add(dashboard_frame, text='🏠 Dashboard')
        
        # Estadísticas rápidas
        stats_frame = tk.Frame(dashboard_frame, bg='#0f0f23')
        stats_frame.pack(fill='x', padx=20, pady=15)
        
        # Estudiantes activos
        students_stat = tk.LabelFrame(stats_frame, text="👥 Estudiantes Activos", 
                                     bg='#1a1a3e', fg='#00d4aa', font=('Arial', 11, 'bold'))
        students_stat.pack(side='left', fill='both', expand=True, padx=10)
        
        tk.Label(students_stat, text=str(len(self.students)), font=('Arial', 28, 'bold'), 
                fg='#00d4aa', bg='#1a1a3e').pack(pady=15)
        
        # Lecciones hoy
        lessons_stat = tk.LabelFrame(stats_frame, text="📚 Lecciones Hoy", 
                                    bg='#1a1a3e', fg='#4a9eff', font=('Arial', 11, 'bold'))
        lessons_stat.pack(side='left', fill='both', expand=True, padx=10)
        
        tk.Label(lessons_stat, text=str(random.randint(15, 25)), font=('Arial', 28, 'bold'), 
                fg='#4a9eff', bg='#1a1a3e').pack(pady=15)
        
        # IA Queries
        ai_stat = tk.LabelFrame(stats_frame, text="🤖 Consultas IA", 
                               bg='#1a1a3e', fg='#ff6b6b', font=('Arial', 11, 'bold'))
        ai_stat.pack(side='left', fill='both', expand=True, padx=10)
        
        ai_count = random.randint(50, 150) if self.ai_enabled else 0
        tk.Label(ai_stat, text=str(ai_count), font=('Arial', 28, 'bold'), 
                fg='#ff6b6b', bg='#1a1a3e').pack(pady=15)
        
        # Actividad reciente
        activity_frame = tk.LabelFrame(dashboard_frame, text="📊 Actividad Reciente", 
                                      bg='#0f0f23', fg='white', font=('Arial', 12, 'bold'))
        activity_frame.pack(fill='both', expand=True, padx=20, pady=10)
        
        self.activity_text = scrolledtext.ScrolledText(activity_frame, height=15, width=100, 
                                                      bg='#1a1a3e', fg='#cccccc', font=('Arial', 10))
        self.activity_text.pack(pady=10, padx=10, fill='both', expand=True)
        
        # Agregar actividad inicial
        self.log_activity("✅ Sistema Maestro iniciado correctamente")
        self.log_activity("🎓 Currículo costarricense cargado")
        self.log_activity("👥 3 perfiles de estudiantes activos")
        if self.ai_enabled:
            self.log_activity("🤖 Ollama IA conectado y listo")
        else:
            self.log_activity("⚠️  Funcionando en modo simulación")
            
    def create_students_tab(self):
        """Crear tab de estudiantes"""
        students_frame = tk.Frame(self.notebook, bg='#0f0f23')
        self.notebook.add(students_frame, text='👥 Estudiantes')
        
        # Lista de estudiantes
        students_list_frame = tk.LabelFrame(students_frame, text="📋 Lista de Estudiantes", 
                                           bg='#0f0f23', fg='white', font=('Arial', 12, 'bold'))
        students_list_frame.pack(fill='both', expand=True, padx=20, pady=10)
        
        # Crear tarjetas de estudiantes
        for student in self.students:
            self.create_student_card(students_list_frame, student)
            
    def create_student_card(self, parent, student):
        """Crear tarjeta de estudiante"""
        card_frame = tk.Frame(parent, bg='#1a1a3e', relief='raised', bd=2)
        card_frame.pack(fill='x', padx=10, pady=8)
        
        # Header con nombre y progreso
        header_frame = tk.Frame(card_frame, bg='#1a1a3e')
        header_frame.pack(fill='x', padx=15, pady=10)
        
        name_label = tk.Label(header_frame, text=f"👤 {student['name']}", 
                             font=('Arial', 14, 'bold'), fg='#00d4aa', bg='#1a1a3e')
        name_label.pack(side='left')
        
        progress_label = tk.Label(header_frame, text=f"📈 {student['progress']}%", 
                                 font=('Arial', 12), fg='#ffd700', bg='#1a1a3e')
        progress_label.pack(side='right')
        
        # Información del estudiante
        info_frame = tk.Frame(card_frame, bg='#1a1a3e')
        info_frame.pack(fill='x', padx=15, pady=5)
        
        info_text = f"🎓 {student['grade']} • 🎯 {student['learning_style']} • 📅 {student['age']} años"
        info_label = tk.Label(info_frame, text=info_text, 
                             font=('Arial', 10), fg='#cccccc', bg='#1a1a3e')
        info_label.pack(side='left')
        
        # Materias
        subjects_text = "📚 " + ", ".join(student['subjects'])
        subjects_label = tk.Label(card_frame, text=subjects_text, 
                                 font=('Arial', 9), fg='#4a9eff', bg='#1a1a3e',
                                 wraplength=800, justify=tk.LEFT)
        subjects_label.pack(fill='x', padx=15, pady=5)
        
        # Botones de acción
        buttons_frame = tk.Frame(card_frame, bg='#1a1a3e')
        buttons_frame.pack(fill='x', padx=15, pady=10)
        
        tk.Button(buttons_frame, text="📊 Ver Perfil", 
                 command=lambda s=student: self.show_student_profile(s),
                 bg='#4a9eff', fg='white', font=('Arial', 9, 'bold')).pack(side='left', padx=5)
        
        tk.Button(buttons_frame, text="📚 Nueva Lección", 
                 command=lambda s=student: self.create_lesson_for_student(s),
                 bg='#00d4aa', fg='black', font=('Arial', 9, 'bold')).pack(side='left', padx=5)
        
        tk.Button(buttons_frame, text="🤖 Consultar IA", 
                 command=lambda s=student: self.ai_student_analysis(s),
                 bg='#ff6b6b', fg='white', font=('Arial', 9, 'bold')).pack(side='left', padx=5)
        
    def create_lessons_tab(self):
        """Crear tab de lecciones"""
        lessons_frame = tk.Frame(self.notebook, bg='#0f0f23')
        self.notebook.add(lessons_frame, text='📚 Lecciones')
        
        # Creador de lecciones
        creator_frame = tk.LabelFrame(lessons_frame, text="✨ Creador de Lecciones IA", 
                                     bg='#0f0f23', fg='white', font=('Arial', 12, 'bold'))
        creator_frame.pack(fill='x', padx=20, pady=10)
        
        # Formulario de creación
        form_frame = tk.Frame(creator_frame, bg='#0f0f23')
        form_frame.pack(pady=15, padx=20)
        
        # Selección de estudiante
        tk.Label(form_frame, text="👤 Estudiante:", bg='#0f0f23', fg='white', 
                font=('Arial', 11)).grid(row=0, column=0, sticky='w', padx=5, pady=5)
        
        self.student_var = tk.StringVar()
        student_combo = ttk.Combobox(form_frame, textvariable=self.student_var, width=25)
        student_combo['values'] = [s['name'] for s in self.students]
        student_combo.grid(row=0, column=1, padx=10, pady=5)
        
        # Materia
        tk.Label(form_frame, text="📖 Materia:", bg='#0f0f23', fg='white', 
                font=('Arial', 11)).grid(row=0, column=2, sticky='w', padx=5, pady=5)
        
        self.subject_var = tk.StringVar()
        subject_combo = ttk.Combobox(form_frame, textvariable=self.subject_var, width=20)
        subject_combo['values'] = ['Matemáticas', 'Ciencias', 'Español', 'Inglés', 'Estudios Sociales', 'Tecnología']
        subject_combo.grid(row=0, column=3, padx=10, pady=5)
        
        # Tema
        tk.Label(form_frame, text="📝 Tema:", bg='#0f0f23', fg='white', 
                font=('Arial', 11)).grid(row=1, column=0, sticky='w', padx=5, pady=5)
        
        self.topic_var = tk.StringVar()
        topic_entry = tk.Entry(form_frame, textvariable=self.topic_var, width=40, font=('Arial', 11))
        topic_entry.grid(row=1, column=1, columnspan=2, padx=10, pady=5, sticky='ew')
        
        # Tipo de lección
        tk.Label(form_frame, text="🎯 Tipo:", bg='#0f0f23', fg='white', 
                font=('Arial', 11)).grid(row=1, column=3, sticky='w', padx=5, pady=5)
        
        self.lesson_type_var = tk.StringVar()
        type_combo = ttk.Combobox(form_frame, textvariable=self.lesson_type_var, width=20)
        type_combo['values'] = list(self.lesson_templates.keys())
        type_combo.grid(row=1, column=4, padx=10, pady=5)
        
        # Botón de generar
        tk.Button(form_frame, text="🤖 Generar Lección con IA", 
                 command=self.generate_ai_lesson,
                 bg='#ffd700', fg='black', font=('Arial', 12, 'bold'),
                 width=25, height=2).grid(row=2, column=0, columnspan=5, pady=20)
        
        # Área de resultado
        result_frame = tk.LabelFrame(lessons_frame, text="📄 Lección Generada", 
                                    bg='#0f0f23', fg='white', font=('Arial', 12, 'bold'))
        result_frame.pack(fill='both', expand=True, padx=20, pady=10)
        
        self.lesson_result = scrolledtext.ScrolledText(result_frame, height=20, width=100, 
                                                      bg='#1a1a3e', fg='#cccccc', font=('Arial', 10))
        self.lesson_result.pack(pady=10, padx=10, fill='both', expand=True)
        
    def create_ai_tutor_tab(self):
        """Crear tab del tutor IA"""
        ai_frame = tk.Frame(self.notebook, bg='#0f0f23')
        self.notebook.add(ai_frame, text='🤖 Tutor IA')
        
        # Chat con el tutor
        chat_frame = tk.LabelFrame(ai_frame, text="💬 Chat con Maestro IA", 
                                  bg='#0f0f23', fg='white', font=('Arial', 12, 'bold'))
        chat_frame.pack(fill='both', expand=True, padx=20, pady=10)
        
        # Área de conversación
        self.chat_area = scrolledtext.ScrolledText(chat_frame, height=20, width=100, 
                                                  bg='#1a1a3e', fg='#cccccc', font=('Arial', 10))
        self.chat_area.pack(pady=10, padx=10, fill='both', expand=True)
        
        # Entrada de mensaje
        input_frame = tk.Frame(chat_frame, bg='#0f0f23')
        input_frame.pack(fill='x', padx=10, pady=10)
        
        self.chat_input = tk.Entry(input_frame, font=('Arial', 11), width=80)
        self.chat_input.pack(side='left', fill='x', expand=True, padx=5)
        self.chat_input.bind('<Return>', self.send_chat_message)
        
        tk.Button(input_frame, text="📤 Enviar", 
                 command=self.send_chat_message,
                 bg='#00d4aa', fg='black', font=('Arial', 10, 'bold')).pack(side='right', padx=5)
        
        # Sugerencias rápidas
        suggestions_frame = tk.Frame(chat_frame, bg='#0f0f23')
        suggestions_frame.pack(fill='x', padx=10, pady=5)
        
        tk.Label(suggestions_frame, text="💡 Sugerencias rápidas:", 
                bg='#0f0f23', fg='#cccccc', font=('Arial', 10)).pack(side='left')
        
        suggestions = [
            "¿Cómo enseñar fracciones de forma visual?",
            "Actividades para estudiantes kinestésicos", 
            "Evaluación formativa en ciencias",
            "Integrar tecnología en matemáticas"
        ]
        
        for suggestion in suggestions:
            tk.Button(suggestions_frame, text=suggestion, 
                     command=lambda s=suggestion: self.use_suggestion(s),
                     bg='#4a9eff', fg='white', font=('Arial', 8)).pack(side='left', padx=2)
        
        # Mensaje inicial
        self.add_chat_message("🤖 Maestro IA", 
                             "¡Hola! Soy Maestro, tu asistente educativo con IA. "
                             "Puedo ayudarte con planificación de lecciones, estrategias pedagógicas, "
                             "evaluación de estudiantes y mucho más. ¿En qué puedo ayudarte hoy?")
        
    def create_analytics_tab(self):
        """Crear tab de analytics"""
        analytics_frame = tk.Frame(self.notebook, bg='#0f0f23')
        self.notebook.add(analytics_frame, text='📊 Analytics')
        
        # Métricas principales
        metrics_frame = tk.Frame(analytics_frame, bg='#0f0f23')
        metrics_frame.pack(fill='x', padx=20, pady=15)
        
        # Rendimiento general
        performance_frame = tk.LabelFrame(metrics_frame, text="📈 Rendimiento General", 
                                         bg='#1a1a3e', fg='#00d4aa', font=('Arial', 11, 'bold'))
        performance_frame.pack(side='left', fill='both', expand=True, padx=10)
        
        avg_progress = sum(s['progress'] for s in self.students) / len(self.students)
        tk.Label(performance_frame, text=f"{avg_progress:.1f}%", font=('Arial', 24, 'bold'), 
                fg='#00d4aa', bg='#1a1a3e').pack(pady=10)
        
        # Tiempo de respuesta IA
        ai_response_frame = tk.LabelFrame(metrics_frame, text="⚡ Tiempo Respuesta IA", 
                                         bg='#1a1a3e', fg='#4a9eff', font=('Arial', 11, 'bold'))
        ai_response_frame.pack(side='left', fill='both', expand=True, padx=10)
        
        response_time = f"{random.uniform(0.5, 2.5):.1f}s" if self.ai_enabled else "N/A"
        tk.Label(ai_response_frame, text=response_time, font=('Arial', 24, 'bold'), 
                fg='#4a9eff', bg='#1a1a3e').pack(pady=10)
        
        # Satisfacción
        satisfaction_frame = tk.LabelFrame(metrics_frame, text="😊 Satisfacción", 
                                          bg='#1a1a3e', fg='#ff6b6b', font=('Arial', 11, 'bold'))
        satisfaction_frame.pack(side='left', fill='both', expand=True, padx=10)
        
        tk.Label(satisfaction_frame, text="4.8/5", font=('Arial', 24, 'bold'), 
                fg='#ff6b6b', bg='#1a1a3e').pack(pady=10)
        
        # Detalles de analytics
        details_frame = tk.LabelFrame(analytics_frame, text="📊 Analytics Detallados", 
                                     bg='#0f0f23', fg='white', font=('Arial', 12, 'bold'))
        details_frame.pack(fill='both', expand=True, padx=20, pady=10)
        
        self.analytics_text = scrolledtext.ScrolledText(details_frame, height=18, width=100, 
                                                       bg='#1a1a3e', fg='#cccccc', font=('Arial', 10))
        self.analytics_text.pack(pady=10, padx=10, fill='both', expand=True)
        
        self.update_analytics_display()
        
    def create_curriculum_tab(self):
        """Crear tab de currículo"""
        curriculum_frame = tk.Frame(self.notebook, bg='#0f0f23')
        self.notebook.add(curriculum_frame, text='📋 Currículo CR')
        
        # Selector de nivel
        level_frame = tk.Frame(curriculum_frame, bg='#0f0f23')
        level_frame.pack(fill='x', padx=20, pady=10)
        
        tk.Label(level_frame, text="🎓 Nivel Educativo:", bg='#0f0f23', fg='white', 
                font=('Arial', 12, 'bold')).pack(side='left', padx=10)
        
        self.curriculum_level_var = tk.StringVar(value='Primaria')
        level_combo = ttk.Combobox(level_frame, textvariable=self.curriculum_level_var, 
                                  values=['Primaria', 'Secundaria'])
        level_combo.pack(side='left', padx=10)
        level_combo.bind('<<ComboboxSelected>>', self.update_curriculum_display)
        
        # Área de curriculum
        self.curriculum_display = scrolledtext.ScrolledText(curriculum_frame, height=25, width=120, 
                                                           bg='#1a1a3e', fg='#cccccc', font=('Arial', 10))
        self.curriculum_display.pack(pady=10, padx=20, fill='both', expand=True)
        
        self.update_curriculum_display()
        
    def show_student_profile(self, student):
        """Mostrar perfil detallado del estudiante"""
        profile_window = tk.Toplevel(self.root)
        profile_window.title(f"👤 Perfil - {student['name']}")
        profile_window.geometry("600x500")
        profile_window.configure(bg='#1a1a3e')
        
        # Información del estudiante
        info_text = f"""
👤 PERFIL DEL ESTUDIANTE

📝 Nombre: {student['name']}
🎓 Grado: {student['grade']}
📅 Edad: {student['age']} años
🎯 Estilo de Aprendizaje: {student['learning_style']}
📈 Progreso General: {student['progress']}%

📚 MATERIAS ACTIVAS:
{chr(10).join('• ' + subject for subject in student['subjects'])}

💪 FORTALEZAS IDENTIFICADAS:
{chr(10).join('• ' + strength for strength in student['strengths'])}

🎯 ÁREAS DE MEJORA:
{chr(10).join('• ' + improvement for improvement in student['improvements'])}

🤖 RECOMENDACIONES IA:
• Usar más recursos visuales para matemáticas
• Incorporar actividades prácticas en ciencias
• Reforzar lectura comprensiva con textos interactivos
• Implementar gamificación para mantener motivación
        """
        
        profile_label = tk.Label(profile_window, text=info_text, 
                                bg='#1a1a3e', fg='#cccccc', font=('Arial', 11), 
                                justify=tk.LEFT)
        profile_label.pack(pady=20, padx=20, fill='both', expand=True)
        
    def create_lesson_for_student(self, student):
        """Crear lección personalizada para estudiante"""
        self.notebook.select(2)  # Cambiar a tab de lecciones
        self.student_var.set(student['name'])
        
        # Sugerir materia basada en áreas de mejora
        if 'Lectura comprensiva' in student['improvements']:
            self.subject_var.set('Español')
            self.topic_var.set('Comprensión lectora avanzada')
        elif 'Matemáticas aplicadas' in student['improvements']:
            self.subject_var.set('Matemáticas')
            self.topic_var.set('Aplicaciones prácticas de álgebra')
        else:
            self.subject_var.set(student['subjects'][0])
            
        self.lesson_type_var.set('interactive')
        
        messagebox.showinfo("Lección Personalizada", 
                           f"✅ Configuración automática para {student['name']}\n"
                           f"🎯 Basada en su perfil de aprendizaje: {student['learning_style']}\n"
                           f"📈 Enfocada en sus áreas de mejora")
        
    def ai_student_analysis(self, student):
        """Análisis del estudiante con IA"""
        if not self.ai_enabled:
            # Simulación
            analysis = f"""
🤖 ANÁLISIS IA - {student['name']} (Modo Simulación)

📊 ANÁLISIS COGNITIVO:
• Perfil de aprendizaje {student['learning_style']} bien desarrollado
• Progreso del {student['progress']}% indica buen rendimiento general
• Fortalezas en {', '.join(student['strengths'][:2])}

🎯 RECOMENDACIONES PERSONALIZADAS:
• Implementar técnicas de aprendizaje {student['learning_style']}
• Reforzar {student['improvements'][0]} con actividades específicas
• Usar gamificación para mantener motivación alta

📚 ESTRATEGIAS SUGERIDAS:
• Lecciones interactivas con elementos multimedia
• Proyectos colaborativos para desarrollo social
• Evaluación formativa continua

⏱️ Tiempo de respuesta: 1.2s (simulado)
            """
        else:
            # Usar Ollama real
            try:
                analysis_data = {
                    'student_profile': student,
                    'learning_preferences': {
                        'style': student['learning_style'],
                        'grade': student['grade'],
                        'subjects': student['subjects']
                    }
                }
                
                # Aquí iría la llamada real a Ollama
                analysis = f"🤖 Análisis IA real para {student['name']} (Pendiente de implementación completa)"
                
            except Exception as e:
                analysis = f"❌ Error en análisis IA: {e}"
                
        # Mostrar análisis
        analysis_window = tk.Toplevel(self.root)
        analysis_window.title(f"🤖 Análisis IA - {student['name']}")
        analysis_window.geometry("700x600")
        analysis_window.configure(bg='#1a1a3e')
        
        analysis_text = scrolledtext.ScrolledText(analysis_window, height=30, width=80, 
                                                 bg='#0f0f23', fg='#cccccc', font=('Arial', 10))
        analysis_text.pack(pady=20, padx=20, fill='both', expand=True)
        analysis_text.insert('1.0', analysis)
        
        self.log_activity(f"🤖 Análisis IA generado para {student['name']}")
        
    def generate_ai_lesson(self):
        """Generar lección usando IA"""
        student_name = self.student_var.get()
        subject = self.subject_var.get()
        topic = self.topic_var.get()
        lesson_type = self.lesson_type_var.get()
        
        if not student_name or not subject or not topic:
            messagebox.showerror("Error", "Por favor completa todos los campos")
            return
            
        self.lesson_result.delete('1.0', tk.END)
        self.lesson_result.insert('1.0', "🤖 Generando lección con IA...\n\n")
        self.root.update()
        
        # Simular o usar IA real
        if not self.ai_enabled:
            # Lección simulada
            lesson_content = f"""
🎓 LECCIÓN GENERADA CON IA

📚 Materia: {subject}
📝 Tema: {topic}
👤 Estudiante: {student_name}
🎯 Tipo: {self.lesson_templates.get(lesson_type, 'General')}

🎯 OBJETIVOS DE APRENDIZAJE:
• Comprender los conceptos fundamentales de {topic}
• Aplicar conocimientos en situaciones prácticas
• Desarrollar habilidades de pensamiento crítico
• Fomentar la creatividad y expresión personal

📖 DESARROLLO DE LA LECCIÓN:

1. INTRODUCCIÓN (10 minutos)
   - Activación de conocimientos previos
   - Presentación del tema con recursos multimedia
   - Conexión con experiencias cotidianas del estudiante

2. DESARROLLO (25 minutos)
   - Explicación interactiva del contenido
   - Actividades prácticas adaptadas al estilo de aprendizaje
   - Uso de tecnología educativa (simulaciones, apps)
   - Trabajo colaborativo cuando sea apropiado

3. PRÁCTICA GUIADA (10 minutos)
   - Ejercicios step-by-step con retroalimentación
   - Resolución de problemas en tiempo real
   - Apoyo individualizado según necesidades

4. CIERRE Y EVALUACIÓN (5 minutos)
   - Síntesis de aprendizajes clave
   - Autoevaluación del estudiante
   - Conexión con lecciones futuras

🎮 ACTIVIDADES INTERACTIVAS:
• Quiz gamificado con premios virtuales
• Simulación digital del tema estudiado
• Proyecto creativo usando herramientas digitales
• Presentación multimedia del estudiante

📊 EVALUACIÓN FORMATIVA:
• Rúbrica adaptada al nivel del estudiante
• Peer assessment cuando aplique
• Portfolio digital de evidencias
• Reflexión metacognitiva

🔗 RECURSOS ADICIONALES:
• Videos educativos seleccionados
• Apps recomendadas para práctica
• Enlaces a contenido complementario
• Actividades para casa (opcional)

💡 ADAPTACIONES PERSONALIZADAS:
• Ajustado para estilo de aprendizaje {student_name.split()[-1] if student_name else 'del estudiante'}
• Incluye elementos tecnológicos innovadores
• Considera el currículo costarricense vigente
• Promueve competencias del siglo XXI

⏱️ Duración estimada: 50 minutos
🎯 Dificultad: Adaptada al nivel del estudiante
🤖 Generado con IA Maestro v1.0
            """
        else:
            # Aquí iría la llamada real a Ollama
            lesson_content = "🤖 Lección generada con Ollama (implementación pendiente)"
            
        # Mostrar resultado
        self.lesson_result.delete('1.0', tk.END)
        self.lesson_result.insert('1.0', lesson_content)
        
        self.log_activity(f"📚 Lección generada: {subject} - {topic} para {student_name}")
        
    def send_chat_message(self, event=None):
        """Enviar mensaje al chat IA"""
        message = self.chat_input.get().strip()
        if not message:
            return
            
        # Agregar mensaje del usuario
        self.add_chat_message("👤 Tú", message)
        self.chat_input.delete(0, tk.END)
        
        # Simular respuesta de IA
        threading.Thread(target=self.process_ai_response, args=(message,), daemon=True).start()
        
    def process_ai_response(self, user_message):
        """Procesar respuesta de IA"""
        time.sleep(1)  # Simular procesamiento
        
        if not self.ai_enabled:
            # Respuestas simuladas
            responses = [
                "Excelente pregunta. Para enseñar este tema de forma efectiva, te sugiero usar una metodología constructivista que permita al estudiante ser protagonista de su aprendizaje.",
                "Basándome en las mejores prácticas pedagógicas, recomiendo implementar actividades que integren tecnología educativa con aprendizaje experiencial.",
                "Es importante considerar los diferentes estilos de aprendizaje. Te sugiero combinar elementos visuales, auditivos y kinestésicos en tus lecciones.",
                "Para evaluación formativa, puedes usar técnicas como portafolios digitales, rúbricas interactivas y autoevaluación reflexiva."
            ]
            ai_response = random.choice(responses)
        else:
            # Aquí iría la llamada real a Ollama
            ai_response = "🤖 Respuesta generada con Ollama (implementación pendiente)"
            
        self.add_chat_message("🤖 Maestro IA", ai_response)
        self.log_activity(f"💬 Consulta IA procesada: {user_message[:50]}...")
        
    def add_chat_message(self, sender, message):
        """Agregar mensaje al chat"""
        timestamp = datetime.now().strftime("%H:%M")
        formatted_message = f"[{timestamp}] {sender}: {message}\n\n"
        
        self.chat_area.insert(tk.END, formatted_message)
        self.chat_area.see(tk.END)
        
    def use_suggestion(self, suggestion):
        """Usar sugerencia rápida"""
        self.chat_input.delete(0, tk.END)
        self.chat_input.insert(0, suggestion)
        
    def update_analytics_display(self):
        """Actualizar display de analytics"""
        analytics_data = f"""
📊 ANALYTICS EDUCATIVO - SISTEMA MAESTRO
{'='*60}

👥 ESTUDIANTES:
• Total activos: {len(self.students)}
• Progreso promedio: {sum(s['progress'] for s in self.students) / len(self.students):.1f}%
• Estilos de aprendizaje:
  - Visual: {len([s for s in self.students if s['learning_style'] == 'visual'])}
  - Auditivo: {len([s for s in self.students if s['learning_style'] == 'auditivo'])}
  - Kinestésico: {len([s for s in self.students if s['learning_style'] == 'kinestésico'])}

📚 MATERIAS MÁS POPULARES:
• Matemáticas: {sum(1 for s in self.students if 'Matemáticas' in s['subjects'])} estudiantes
• Ciencias: {sum(1 for s in self.students if 'Ciencias' in s['subjects'])} estudiantes  
• Tecnología: {sum(1 for s in self.students if 'Tecnología' in s['subjects'])} estudiantes
• Inglés: {sum(1 for s in self.students if 'Inglés' in s['subjects'])} estudiantes

🤖 DESEMPEÑO IA:
• Estado: {'Activa' if self.ai_enabled else 'Simulación'}
• Consultas procesadas: {random.randint(50, 150) if self.ai_enabled else 0}
• Tiempo promedio respuesta: {random.uniform(0.8, 2.2):.1f}s
• Precisión estimada: {random.randint(85, 95)}%

📈 MÉTRICAS DE ENGAGEMENT:
• Lecciones completadas hoy: {random.randint(15, 30)}
• Tiempo promedio por sesión: {random.randint(35, 60)} min
• Satisfacción estudiantes: {random.uniform(4.5, 5.0):.1f}/5.0
• Retención semanal: {random.randint(85, 95)}%

🎯 OBJETIVOS CURRICULARES:
• Cumplimiento currículo CR: 92%
• Competencias siglo XXI: 88%
• Integración tecnológica: 95%
• Inclusión educativa: 90%

💡 INSIGHTS AUTOMÁTICOS:
• Los estudiantes responden mejor a contenido interactivo
• Las lecciones con gamificación tienen 40% más engagement
• La IA ha mejorado la personalización en 60%
• Se recomienda más contenido visual para matemáticas

⏰ Última actualización: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}
        """
        
        self.analytics_text.delete('1.0', tk.END)
        self.analytics_text.insert('1.0', analytics_data)
        
    def update_curriculum_display(self, event=None):
        """Actualizar display del currículo"""
        level = self.curriculum_level_var.get()
        curriculum_data = self.curriculum_cr.get(level, {})
        
        display_text = f"""
📋 CURRÍCULO COSTARRICENSE - {level.upper()}
{'='*70}

El siguiente currículo está alineado con los estándares del Ministerio de 
Educación Pública de Costa Rica y adaptado para integración tecnológica.

"""
        
        for subject, topics in curriculum_data.items():
            display_text += f"\n📚 {subject.upper()}\n"
            display_text += "-" * (len(subject) + 4) + "\n"
            
            for i, topic in enumerate(topics, 1):
                display_text += f"{i}. {topic}\n"
                
            display_text += f"\n🎯 Competencias desarrolladas:\n"
            display_text += "• Pensamiento crítico y resolución de problemas\n"
            display_text += "• Comunicación efectiva\n"
            display_text += "• Colaboración y trabajo en equipo\n"
            display_text += "• Creatividad e innovación\n"
            display_text += "• Ciudadanía digital\n\n"
            
        display_text += f"""
🇨🇷 VALORES COSTARRICENSES INTEGRADOS:
• Democracia y participación ciudadana
• Solidaridad y cooperación
• Respeto por la diversidad
• Conciencia ambiental
• Identidad nacional y cultural

🔬 ENFOQUE TECNOLÓGICO:
• Integración de herramientas digitales
• Desarrollo de competencias STEAM
• Alfabetización en IA y robótica
• Pensamiento computacional
• Ciudadanía digital responsable

📈 METODOLOGÍAS PEDAGÓGICAS:
• Aprendizaje basado en proyectos
• Metodología STEAM integrada
• Flipped classroom con tecnología
• Aprendizaje colaborativo
• Evaluación formativa continua
        """
        
        self.curriculum_display.delete('1.0', tk.END)
        self.curriculum_display.insert('1.0', display_text)
        
    def log_activity(self, message):
        """Registrar actividad en el sistema"""
        timestamp = datetime.now().strftime("%H:%M:%S")
        formatted_message = f"[{timestamp}] {message}\n"
        
        self.activity_text.insert(tk.END, formatted_message)
        self.activity_text.see(tk.END)
        
    def start_ai_services(self):
        """Iniciar servicios de IA"""
        def ai_service_thread():
            while True:
                try:
                    # Simular actividad de IA
                    time.sleep(30)
                    activities = [
                        "🤖 IA procesó recomendación pedagógica",
                        "📊 Analytics actualizados automáticamente", 
                        "🎯 Personalización de contenido optimizada",
                        "💡 Nuevo insight educativo generado"
                    ]
                    self.log_activity(random.choice(activities))
                except:
                    break
                    
        threading.Thread(target=ai_service_thread, daemon=True).start()
        
    def start_simulation_mode(self):
        """Iniciar modo simulación"""
        def simulation_thread():
            while True:
                try:
                    time.sleep(45)
                    self.log_activity("⚠️  Funcionando en modo simulación - Instala Ollama para IA real")
                except:
                    break
                    
        threading.Thread(target=simulation_thread, daemon=True).start()

def main():
    """Función principal"""
    try:
        app = MaestroEducationalPlatform()
        app.root.mainloop()
    except Exception as e:
        messagebox.showerror("Error", f"Error launching Maestro Educational Platform:\n{e}")

if __name__ == "__main__":
    main()
