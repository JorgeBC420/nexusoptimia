"""
NexusOptim IA - Smart Tourism Platform
Plataforma de Turismo Tecnológico con IA para Costa Rica

Características:
- Recomendaciones personalizadas con IA
- Tours interactivos basados en ubicación
- Hoteles con ranking inteligente
- Integración con infraestructura IoT
- Pagos premium para visibilidad
- Analytics en tiempo real

Copyright (c) 2025 OpenNexus
Licensed under MIT License
"""

import tkinter as tk
from tkinter import ttk, messagebox
import json
import random
import math
from datetime import datetime, timedelta
import threading
import time

class SmartTourismPlatform:
    """Plataforma de Turismo Tecnológico con IA"""
    
    def __init__(self):
        self.root = tk.Tk()
        self.root.title("NexusOptim IA - Smart Tourism Costa Rica")
        self.root.geometry("1200x800")
        self.root.configure(bg='#1a1a2e')
        
        # Datos de turismo
        self.user_location = {"lat": 9.748917, "lng": -83.753428}  # San José
        self.user_preferences = {
            "adventure": 0.7,
            "culture": 0.5,
            "nature": 0.9,
            "luxury": 0.3,
            "tech": 0.8,
            "budget": "medium"
        }
        
        self.setup_data()
        self.setup_ui()
        self.start_ai_recommendations()
        
    def setup_data(self):
        """Setup tourism data for Costa Rica"""
        self.tours = [
            {
                "id": 1,
                "name": "Volcán Arenal + Aguas Termales IoT",
                "location": {"lat": 10.463056, "lng": -84.703333},
                "price": 85,
                "duration": "8 horas",
                "category": ["nature", "tech", "adventure"],
                "premium": True,
                "rating": 4.8,
                "description": "Tour al volcán con sensores IoT que monitorean actividad sísmica en tiempo real",
                "tech_features": ["Sensores sísmicos", "Monitoreo de gases", "App realidad aumentada"],
                "availability": 12,
                "images": ["arenal1.jpg", "arenal2.jpg"]
            },
            {
                "id": 2,
                "name": "Monteverde Cloud Forest + Drones",
                "location": {"lat": 10.300000, "lng": -84.783333},
                "price": 95,
                "duration": "10 horas",
                "category": ["nature", "tech", "culture"],
                "premium": True,
                "rating": 4.9,
                "description": "Bosque nuboso explorado con drones 4K y análisis de biodiversidad IA",
                "tech_features": ["Drones de exploración", "IA identificación especies", "Realidad virtual"],
                "availability": 8,
                "images": ["monteverde1.jpg", "monteverde2.jpg"]
            },
            {
                "id": 3,
                "name": "Playas de Guanacaste Smart Beach",
                "location": {"lat": 10.633333, "lng": -85.433333},
                "price": 65,
                "duration": "6 horas",
                "category": ["adventure", "tech", "nature"],
                "premium": False,
                "rating": 4.6,
                "description": "Playas inteligentes con monitoreo de calidad del agua y predicción de olas",
                "tech_features": ["Sensores de agua", "Predicción olas IA", "App navegación"],
                "availability": 15,
                "images": ["guanacaste1.jpg", "guanacaste2.jpg"]
            },
            {
                "id": 4,
                "name": "San José Tech City Tour",
                "location": {"lat": 9.748917, "lng": -83.753428},
                "price": 45,
                "duration": "4 horas",
                "category": ["tech", "culture"],
                "premium": False,
                "rating": 4.3,
                "description": "Tour por el distrito tecnológico con visitas a startups e incubadoras",
                "tech_features": ["Visitas startups", "Labs de innovación", "Networking events"],
                "availability": 20,
                "images": ["sanjose1.jpg", "sanjose2.jpg"]
            },
            {
                "id": 5,
                "name": "Manuel Antonio AI Wildlife Tracking",
                "location": {"lat": 9.390000, "lng": -84.140000},
                "price": 75,
                "duration": "7 horas",
                "category": ["nature", "tech", "adventure"],
                "premium": True,
                "rating": 4.7,
                "description": "Parque nacional con tracking de fauna mediante IA y cámaras inteligentes",
                "tech_features": ["Cámaras IA", "Tracking GPS animales", "Bioacústica"],
                "availability": 10,
                "images": ["manuel1.jpg", "manuel2.jpg"]
            }
        ]
        
        self.hotels = [
            {
                "id": 101,
                "name": "Hotel Presidente Smart San José",
                "location": {"lat": 9.748917, "lng": -83.753428},
                "price_per_night": 120,
                "category": ["tech", "luxury"],
                "premium": True,
                "rating": 4.5,
                "description": "Hotel inteligente en el centro con IoT, domótica y conectividad 5G",
                "tech_features": ["IoT room control", "5G WiFi", "Smart mirrors", "AI concierge"],
                "rooms_available": 15,
                "images": ["presidente1.jpg", "presidente2.jpg"]
            },
            {
                "id": 102,
                "name": "Tabacón Thermal Resort & Spa Tech",
                "location": {"lat": 10.463056, "lng": -84.703333},
                "price_per_night": 280,
                "category": ["luxury", "nature", "tech"],
                "premium": True,
                "rating": 4.9,
                "description": "Resort de lujo con aguas termales monitoreadas por sensores IoT",
                "tech_features": ["Sensores termales", "Spa IA personalizado", "Smart wellness"],
                "rooms_available": 5,
                "images": ["tabacon1.jpg", "tabacon2.jpg"]
            },
            {
                "id": 103,
                "name": "Eco Lodge Monteverde Connected",
                "location": {"lat": 10.300000, "lng": -84.783333},
                "price_per_night": 95,
                "category": ["nature", "tech"],
                "premium": False,
                "rating": 4.4,
                "description": "Lodge ecológico con energía solar inteligente y monitoreo ambiental",
                "tech_features": ["Solar smart grid", "Environmental sensors", "Wildlife cams"],
                "rooms_available": 8,
                "images": ["monteverde_lodge1.jpg", "monteverde_lodge2.jpg"]
            },
            {
                "id": 104,
                "name": "Guanacaste Beach Smart Resort",
                "location": {"lat": 10.633333, "lng": -85.433333},
                "price_per_night": 160,
                "category": ["luxury", "adventure", "tech"],
                "premium": True,
                "rating": 4.6,
                "description": "Resort playero con tecnología marina y deportes acuáticos inteligentes",
                "tech_features": ["Marine tech", "Smart water sports", "Beach monitoring"],
                "rooms_available": 12,
                "images": ["guanacaste_resort1.jpg", "guanacaste_resort2.jpg"]
            }
        ]
        
    def setup_ui(self):
        """Setup the main user interface"""
        # Header
        header_frame = tk.Frame(self.root, bg='#16213e', height=80)
        header_frame.pack(fill='x', padx=0, pady=0)
        header_frame.pack_propagate(False)
        
        title_label = tk.Label(header_frame, text="🇨🇷 Smart Tourism Costa Rica", 
                              font=('Arial', 24, 'bold'), 
                              fg='#00d4aa', bg='#16213e')
        title_label.pack(pady=20)
        
        # Main container with notebook
        main_container = tk.Frame(self.root, bg='#1a1a2e')
        main_container.pack(fill='both', expand=True, padx=10, pady=10)
        
        # Create notebook for tabs
        self.notebook = ttk.Notebook(main_container)
        self.notebook.pack(fill='both', expand=True)
        
        # Configure notebook style
        style = ttk.Style()
        style.theme_use('clam')
        style.configure('TNotebook', background='#1a1a2e')
        style.configure('TNotebook.Tab', background='#16213e', foreground='white', padding=[20, 10])
        style.map('TNotebook.Tab', background=[('selected', '#00d4aa')], foreground=[('selected', 'black')])
        
        # Create tabs
        self.create_dashboard_tab()
        self.create_tours_tab()
        self.create_hotels_tab()
        self.create_ai_recommendations_tab()
        self.create_admin_tab()
        
    def create_dashboard_tab(self):
        """Create dashboard tab"""
        dashboard_frame = tk.Frame(self.notebook, bg='#1a1a2e')
        self.notebook.add(dashboard_frame, text='🏠 Dashboard')
        
        # Location info
        location_frame = tk.LabelFrame(dashboard_frame, text="Tu Ubicación Actual", 
                                      bg='#1a1a2e', fg='white', font=('Arial', 12, 'bold'))
        location_frame.pack(fill='x', padx=20, pady=10)
        
        location_info = tk.Label(location_frame, 
                               text=f"📍 San José, Costa Rica\n🌡️ 24°C - Soleado\n⏰ {datetime.now().strftime('%H:%M')}",
                               bg='#1a1a2e', fg='#cccccc', font=('Arial', 11), justify=tk.LEFT)
        location_info.pack(pady=10, padx=10)
        
        # Quick stats
        stats_frame = tk.Frame(dashboard_frame, bg='#1a1a2e')
        stats_frame.pack(fill='x', padx=20, pady=10)
        
        # Tours disponibles
        tours_stat = tk.LabelFrame(stats_frame, text="Tours Disponibles", 
                                  bg='#16213e', fg='#00d4aa', font=('Arial', 10, 'bold'))
        tours_stat.pack(side='left', fill='both', expand=True, padx=5)
        
        tours_count = sum(1 for tour in self.tours if tour['availability'] > 0)
        tk.Label(tours_stat, text=f"{tours_count}", font=('Arial', 24, 'bold'), 
                fg='#00d4aa', bg='#16213e').pack(pady=10)
        
        # Hoteles disponibles
        hotels_stat = tk.LabelFrame(stats_frame, text="Hoteles Disponibles", 
                                   bg='#16213e', fg='#ff6b6b', font=('Arial', 10, 'bold'))
        hotels_stat.pack(side='left', fill='both', expand=True, padx=5)
        
        hotels_count = sum(1 for hotel in self.hotels if hotel['rooms_available'] > 0)
        tk.Label(hotels_stat, text=f"{hotels_count}", font=('Arial', 24, 'bold'), 
                fg='#ff6b6b', bg='#16213e').pack(pady=10)
        
        # Recommendations preview
        rec_frame = tk.LabelFrame(dashboard_frame, text="🤖 Recomendaciones IA", 
                                 bg='#1a1a2e', fg='white', font=('Arial', 12, 'bold'))
        rec_frame.pack(fill='both', expand=True, padx=20, pady=10)
        
        self.recommendations_text = tk.Text(rec_frame, height=8, width=80, 
                                          bg='#16213e', fg='#cccccc', font=('Arial', 10))
        self.recommendations_text.pack(pady=10, padx=10)
        
    def create_tours_tab(self):
        """Create tours tab"""
        tours_frame = tk.Frame(self.notebook, bg='#1a1a2e')
        self.notebook.add(tours_frame, text='🗺️ Tours')
        
        # Search and filters
        search_frame = tk.Frame(tours_frame, bg='#1a1a2e')
        search_frame.pack(fill='x', padx=20, pady=10)
        
        tk.Label(search_frame, text="🔍 Buscar Tours:", bg='#1a1a2e', fg='white', 
                font=('Arial', 11, 'bold')).pack(side='left', padx=5)
        
        self.search_var = tk.StringVar()
        search_entry = tk.Entry(search_frame, textvariable=self.search_var, 
                               font=('Arial', 11), width=30)
        search_entry.pack(side='left', padx=10)
        
        search_btn = tk.Button(search_frame, text="Buscar", command=self.search_tours,
                              bg='#00d4aa', fg='black', font=('Arial', 10, 'bold'))
        search_btn.pack(side='left', padx=5)
        
        # Tours list
        tours_list_frame = tk.Frame(tours_frame, bg='#1a1a2e')
        tours_list_frame.pack(fill='both', expand=True, padx=20, pady=10)
        
        # Scrollable frame
        canvas = tk.Canvas(tours_list_frame, bg='#1a1a2e')
        scrollbar = ttk.Scrollbar(tours_list_frame, orient="vertical", command=canvas.yview)
        self.tours_scrollable = tk.Frame(canvas, bg='#1a1a2e')
        
        self.tours_scrollable.bind("<Configure>", lambda e: canvas.configure(scrollregion=canvas.bbox("all")))
        canvas.create_window((0, 0), window=self.tours_scrollable, anchor="nw")
        canvas.configure(yscrollcommand=scrollbar.set)
        
        canvas.pack(side="left", fill="both", expand=True)
        scrollbar.pack(side="right", fill="y")
        
        self.display_tours()
        
    def create_hotels_tab(self):
        """Create hotels tab"""
        hotels_frame = tk.Frame(self.notebook, bg='#1a1a2e')
        self.notebook.add(hotels_frame, text='🏨 Hoteles')
        
        # Search and filters
        search_frame = tk.Frame(hotels_frame, bg='#1a1a2e')
        search_frame.pack(fill='x', padx=20, pady=10)
        
        tk.Label(search_frame, text="🔍 Buscar Hoteles:", bg='#1a1a2e', fg='white', 
                font=('Arial', 11, 'bold')).pack(side='left', padx=5)
        
        self.hotel_search_var = tk.StringVar()
        hotel_search_entry = tk.Entry(search_frame, textvariable=self.hotel_search_var, 
                                     font=('Arial', 11), width=30)
        hotel_search_entry.pack(side='left', padx=10)
        
        hotel_search_btn = tk.Button(search_frame, text="Buscar", command=self.search_hotels,
                                    bg='#ff6b6b', fg='white', font=('Arial', 10, 'bold'))
        hotel_search_btn.pack(side='left', padx=5)
        
        # Hotels list
        hotels_list_frame = tk.Frame(hotels_frame, bg='#1a1a2e')
        hotels_list_frame.pack(fill='both', expand=True, padx=20, pady=10)
        
        # Scrollable frame
        canvas = tk.Canvas(hotels_list_frame, bg='#1a1a2e')
        scrollbar = ttk.Scrollbar(hotels_list_frame, orient="vertical", command=canvas.yview)
        self.hotels_scrollable = tk.Frame(canvas, bg='#1a1a2e')
        
        self.hotels_scrollable.bind("<Configure>", lambda e: canvas.configure(scrollregion=canvas.bbox("all")))
        canvas.create_window((0, 0), window=self.hotels_scrollable, anchor="nw")
        canvas.configure(yscrollcommand=scrollbar.set)
        
        canvas.pack(side="left", fill="both", expand=True)
        scrollbar.pack(side="right", fill="y")
        
        self.display_hotels()
        
    def create_ai_recommendations_tab(self):
        """Create AI recommendations tab"""
        ai_frame = tk.Frame(self.notebook, bg='#1a1a2e')
        self.notebook.add(ai_frame, text='🤖 IA Recomendaciones')
        
        # User preferences
        prefs_frame = tk.LabelFrame(ai_frame, text="Configura tus Preferencias", 
                                   bg='#1a1a2e', fg='white', font=('Arial', 12, 'bold'))
        prefs_frame.pack(fill='x', padx=20, pady=10)
        
        prefs_grid = tk.Frame(prefs_frame, bg='#1a1a2e')
        prefs_grid.pack(pady=10, padx=10)
        
        self.pref_vars = {}
        preferences = [
            ("🏔️ Aventura", "adventure"),
            ("🏛️ Cultura", "culture"),
            ("🌿 Naturaleza", "nature"),
            ("💎 Lujo", "luxury"),
            ("🔬 Tecnología", "tech")
        ]
        
        for i, (label, key) in enumerate(preferences):
            tk.Label(prefs_grid, text=label, bg='#1a1a2e', fg='white', font=('Arial', 10)).grid(row=i, column=0, sticky='w', padx=5)
            
            var = tk.DoubleVar(value=self.user_preferences[key])
            self.pref_vars[key] = var
            
            scale = tk.Scale(prefs_grid, from_=0, to=1, resolution=0.1, orient='horizontal',
                           variable=var, bg='#16213e', fg='white', highlightthickness=0)
            scale.grid(row=i, column=1, padx=10, pady=2)
            
        # Budget selection
        budget_frame = tk.Frame(prefs_frame, bg='#1a1a2e')
        budget_frame.pack(pady=10)
        
        tk.Label(budget_frame, text="💰 Presupuesto:", bg='#1a1a2e', fg='white', font=('Arial', 10, 'bold')).pack(side='left')
        
        self.budget_var = tk.StringVar(value=self.user_preferences['budget'])
        budget_options = [("💵 Económico", "low"), ("💴 Medio", "medium"), ("💎 Alto", "high")]
        
        for text, value in budget_options:
            tk.Radiobutton(budget_frame, text=text, variable=self.budget_var, value=value,
                          bg='#1a1a2e', fg='white', selectcolor='#16213e').pack(side='left', padx=10)
            
        # Update button
        update_btn = tk.Button(prefs_frame, text="🔄 Actualizar Recomendaciones", 
                              command=self.update_preferences,
                              bg='#00d4aa', fg='black', font=('Arial', 11, 'bold'), pady=10)
        update_btn.pack(pady=15)
        
        # AI recommendations display
        ai_rec_frame = tk.LabelFrame(ai_frame, text="🎯 Recomendaciones Personalizadas", 
                                    bg='#1a1a2e', fg='white', font=('Arial', 12, 'bold'))
        ai_rec_frame.pack(fill='both', expand=True, padx=20, pady=10)
        
        self.ai_recommendations_text = tk.Text(ai_rec_frame, height=15, width=80, 
                                             bg='#16213e', fg='#cccccc', font=('Arial', 10))
        ai_scrollbar = ttk.Scrollbar(ai_rec_frame, orient="vertical", command=self.ai_recommendations_text.yview)
        self.ai_recommendations_text.configure(yscrollcommand=ai_scrollbar.set)
        
        self.ai_recommendations_text.pack(side="left", fill="both", expand=True, pady=10, padx=10)
        ai_scrollbar.pack(side="right", fill="y", pady=10)
        
    def create_admin_tab(self):
        """Create admin tab for premium listings management"""
        admin_frame = tk.Frame(self.notebook, bg='#1a1a2e')
        self.notebook.add(admin_frame, text='⚙️ Admin Premium')
        
        # Premium services info
        premium_info = tk.LabelFrame(admin_frame, text="💎 Servicios Premium", 
                                    bg='#1a1a2e', fg='#ffd700', font=('Arial', 12, 'bold'))
        premium_info.pack(fill='x', padx=20, pady=10)
        
        info_text = """
🏆 POSICIONAMIENTO PREMIUM
• Aparece primero en búsquedas
• Destacado con insignia dorada
• Recomendaciones IA prioritarias
• Analytics detallados

💰 PRECIOS PREMIUM
• Tours: $50/mes por posición top
• Hoteles: $100/mes por posición top
• Análisis IA personalizado incluido
        """
        
        tk.Label(premium_info, text=info_text, bg='#1a1a2e', fg='#cccccc', 
                font=('Arial', 10), justify=tk.LEFT).pack(pady=10, padx=10)
        
        # Premium management
        management_frame = tk.LabelFrame(admin_frame, text="🎛️ Gestión Premium", 
                                        bg='#1a1a2e', fg='white', font=('Arial', 12, 'bold'))
        management_frame.pack(fill='both', expand=True, padx=20, pady=10)
        
        # Current premium listings
        current_premium_text = tk.Text(management_frame, height=10, width=80, 
                                      bg='#16213e', fg='#cccccc', font=('Arial', 10))
        current_premium_text.pack(pady=10, padx=10)
        
        # Display current premium listings
        self.update_premium_display(current_premium_text)
        
        # Control buttons
        controls_frame = tk.Frame(management_frame, bg='#1a1a2e')
        controls_frame.pack(pady=10)
        
        tk.Button(controls_frame, text="💎 Activar Premium Tour", 
                 command=lambda: self.toggle_premium('tour'),
                 bg='#ffd700', fg='black', font=('Arial', 10, 'bold')).pack(side='left', padx=5)
        
        tk.Button(controls_frame, text="🏨 Activar Premium Hotel", 
                 command=lambda: self.toggle_premium('hotel'),
                 bg='#ffd700', fg='black', font=('Arial', 10, 'bold')).pack(side='left', padx=5)
        
        tk.Button(controls_frame, text="📊 Ver Analytics", 
                 command=self.show_analytics,
                 bg='#4a9eff', fg='white', font=('Arial', 10, 'bold')).pack(side='left', padx=5)
        
    def display_tours(self):
        """Display tours list"""
        # Clear previous tours
        for widget in self.tours_scrollable.winfo_children():
            widget.destroy()
            
        # Sort tours: premium first, then by rating
        sorted_tours = sorted(self.tours, key=lambda x: (-x['premium'], -x['rating']))
        
        for tour in sorted_tours:
            self.create_tour_card(tour)
            
    def create_tour_card(self, tour):
        """Create a tour card widget"""
        card_frame = tk.Frame(self.tours_scrollable, bg='#16213e', relief='raised', bd=2)
        card_frame.pack(fill='x', pady=10, padx=5)
        
        # Header with premium badge
        header_frame = tk.Frame(card_frame, bg='#16213e')
        header_frame.pack(fill='x', padx=10, pady=5)
        
        title_text = tour['name']
        if tour['premium']:
            title_text = f"💎 {title_text} (PREMIUM)"
            
        title_label = tk.Label(header_frame, text=title_text, 
                              font=('Arial', 14, 'bold'), 
                              fg='#ffd700' if tour['premium'] else '#00d4aa', 
                              bg='#16213e')
        title_label.pack(side='left')
        
        # Price and rating
        price_label = tk.Label(header_frame, text=f"${tour['price']} | ⭐{tour['rating']}", 
                              font=('Arial', 12), fg='#cccccc', bg='#16213e')
        price_label.pack(side='right')
        
        # Description
        desc_label = tk.Label(card_frame, text=tour['description'], 
                             font=('Arial', 10), fg='#cccccc', bg='#16213e',
                             wraplength=800, justify=tk.LEFT)
        desc_label.pack(fill='x', padx=10, pady=5)
        
        # Tech features
        tech_text = "🔬 Tech: " + ", ".join(tour['tech_features'])
        tech_label = tk.Label(card_frame, text=tech_text, 
                             font=('Arial', 9), fg='#4a9eff', bg='#16213e',
                             wraplength=800, justify=tk.LEFT)
        tech_label.pack(fill='x', padx=10, pady=2)
        
        # Bottom info and buttons
        bottom_frame = tk.Frame(card_frame, bg='#16213e')
        bottom_frame.pack(fill='x', padx=10, pady=10)
        
        info_label = tk.Label(bottom_frame, 
                             text=f"⏰ {tour['duration']} | 👥 {tour['availability']} disponibles", 
                             font=('Arial', 9), fg='#888888', bg='#16213e')
        info_label.pack(side='left')
        
        book_btn = tk.Button(bottom_frame, text="🎫 Reservar", 
                            command=lambda t=tour: self.book_tour(t),
                            bg='#00d4aa', fg='black', font=('Arial', 10, 'bold'))
        book_btn.pack(side='right', padx=5)
        
        details_btn = tk.Button(bottom_frame, text="📋 Detalles", 
                               command=lambda t=tour: self.show_tour_details(t),
                               bg='#4a9eff', fg='white', font=('Arial', 10))
        details_btn.pack(side='right')
        
    def display_hotels(self):
        """Display hotels list"""
        # Clear previous hotels
        for widget in self.hotels_scrollable.winfo_children():
            widget.destroy()
            
        # Sort hotels: premium first, then by rating
        sorted_hotels = sorted(self.hotels, key=lambda x: (-x['premium'], -x['rating']))
        
        for hotel in sorted_hotels:
            self.create_hotel_card(hotel)
            
    def create_hotel_card(self, hotel):
        """Create a hotel card widget"""
        card_frame = tk.Frame(self.hotels_scrollable, bg='#16213e', relief='raised', bd=2)
        card_frame.pack(fill='x', pady=10, padx=5)
        
        # Header with premium badge
        header_frame = tk.Frame(card_frame, bg='#16213e')
        header_frame.pack(fill='x', padx=10, pady=5)
        
        title_text = hotel['name']
        if hotel['premium']:
            title_text = f"💎 {title_text} (PREMIUM)"
            
        title_label = tk.Label(header_frame, text=title_text, 
                              font=('Arial', 14, 'bold'), 
                              fg='#ffd700' if hotel['premium'] else '#ff6b6b', 
                              bg='#16213e')
        title_label.pack(side='left')
        
        # Price and rating
        price_label = tk.Label(header_frame, text=f"${hotel['price_per_night']}/noche | ⭐{hotel['rating']}", 
                              font=('Arial', 12), fg='#cccccc', bg='#16213e')
        price_label.pack(side='right')
        
        # Description
        desc_label = tk.Label(card_frame, text=hotel['description'], 
                             font=('Arial', 10), fg='#cccccc', bg='#16213e',
                             wraplength=800, justify=tk.LEFT)
        desc_label.pack(fill='x', padx=10, pady=5)
        
        # Tech features
        tech_text = "🔬 Tech: " + ", ".join(hotel['tech_features'])
        tech_label = tk.Label(card_frame, text=tech_text, 
                             font=('Arial', 9), fg='#4a9eff', bg='#16213e',
                             wraplength=800, justify=tk.LEFT)
        tech_label.pack(fill='x', padx=10, pady=2)
        
        # Bottom info and buttons
        bottom_frame = tk.Frame(card_frame, bg='#16213e')
        bottom_frame.pack(fill='x', padx=10, pady=10)
        
        info_label = tk.Label(bottom_frame, 
                             text=f"🛏️ {hotel['rooms_available']} habitaciones disponibles", 
                             font=('Arial', 9), fg='#888888', bg='#16213e')
        info_label.pack(side='left')
        
        book_btn = tk.Button(bottom_frame, text="🏨 Reservar", 
                            command=lambda h=hotel: self.book_hotel(h),
                            bg='#ff6b6b', fg='white', font=('Arial', 10, 'bold'))
        book_btn.pack(side='right', padx=5)
        
        details_btn = tk.Button(bottom_frame, text="📋 Detalles", 
                               command=lambda h=hotel: self.show_hotel_details(h),
                               bg='#4a9eff', fg='white', font=('Arial', 10))
        details_btn.pack(side='right')
        
    def calculate_distance(self, lat1, lng1, lat2, lng2):
        """Calculate distance between two points"""
        R = 6371  # Earth's radius in kilometers
        
        lat1_rad = math.radians(lat1)
        lat2_rad = math.radians(lat2)
        delta_lat = math.radians(lat2 - lat1)
        delta_lng = math.radians(lng2 - lng1)
        
        a = (math.sin(delta_lat/2) * math.sin(delta_lat/2) +
             math.cos(lat1_rad) * math.cos(lat2_rad) *
             math.sin(delta_lng/2) * math.sin(delta_lng/2))
        
        c = 2 * math.atan2(math.sqrt(a), math.sqrt(1-a))
        distance = R * c
        
        return distance
        
    def generate_ai_recommendations(self):
        """Generate AI-based recommendations"""
        recommendations = []
        
        user_lat = self.user_location["lat"]
        user_lng = self.user_location["lng"]
        
        # Score tours based on preferences
        tour_scores = []
        for tour in self.tours:
            score = 0
            
            # Preference matching
            for category in tour['category']:
                if category in self.user_preferences:
                    score += self.user_preferences[category] * 100
                    
            # Distance factor (closer is better)
            distance = self.calculate_distance(
                user_lat, user_lng,
                tour['location']['lat'], tour['location']['lng']
            )
            distance_score = max(0, 100 - distance * 2)  # Penalty for distance
            score += distance_score * 0.3
            
            # Rating factor
            score += tour['rating'] * 20
            
            # Availability factor
            if tour['availability'] > 0:
                score += 10
                
            # Premium boost
            if tour['premium']:
                score += 25
                
            tour_scores.append((tour, score))
            
        # Sort by score
        tour_scores.sort(key=lambda x: x[1], reverse=True)
        
        # Generate recommendations text
        recommendations.append("🤖 RECOMENDACIONES IA PERSONALIZADAS")
        recommendations.append("=" * 50)
        recommendations.append("")
        
        # Top 3 tours
        recommendations.append("🗺️ TOURS RECOMENDADOS:")
        for i, (tour, score) in enumerate(tour_scores[:3]):
            distance = self.calculate_distance(
                user_lat, user_lng,
                tour['location']['lat'], tour['location']['lng']
            )
            
            recommendations.append(f"{i+1}. {tour['name']}")
            recommendations.append(f"   💯 Puntuación IA: {score:.1f}/100")
            recommendations.append(f"   📍 Distancia: {distance:.1f} km")
            recommendations.append(f"   💰 Precio: ${tour['price']}")
            recommendations.append(f"   ⭐ Rating: {tour['rating']}")
            recommendations.append("")
            
        # Hotel recommendations
        hotel_scores = []
        for hotel in self.hotels:
            score = 0
            
            # Preference matching
            for category in hotel['category']:
                if category in self.user_preferences:
                    score += self.user_preferences[category] * 100
                    
            # Distance factor
            distance = self.calculate_distance(
                user_lat, user_lng,
                hotel['location']['lat'], hotel['location']['lng']
            )
            distance_score = max(0, 100 - distance * 2)
            score += distance_score * 0.3
            
            # Rating factor
            score += hotel['rating'] * 20
            
            # Availability factor
            if hotel['rooms_available'] > 0:
                score += 10
                
            # Premium boost
            if hotel['premium']:
                score += 25
                
            hotel_scores.append((hotel, score))
            
        hotel_scores.sort(key=lambda x: x[1], reverse=True)
        
        recommendations.append("🏨 HOTELES RECOMENDADOS:")
        for i, (hotel, score) in enumerate(hotel_scores[:3]):
            distance = self.calculate_distance(
                user_lat, user_lng,
                hotel['location']['lat'], hotel['location']['lng']
            )
            
            recommendations.append(f"{i+1}. {hotel['name']}")
            recommendations.append(f"   💯 Puntuación IA: {score:.1f}/100")
            recommendations.append(f"   📍 Distancia: {distance:.1f} km")
            recommendations.append(f"   💰 Precio: ${hotel['price_per_night']}/noche")
            recommendations.append(f"   ⭐ Rating: {hotel['rating']}")
            recommendations.append("")
            
        # Personalized tips
        recommendations.append("💡 CONSEJOS PERSONALIZADOS:")
        
        if self.user_preferences['tech'] > 0.7:
            recommendations.append("• Te encantan las experiencias tecnológicas")
            recommendations.append("• Considera tours con IoT y realidad aumentada")
            
        if self.user_preferences['nature'] > 0.8:
            recommendations.append("• Eres amante de la naturaleza")
            recommendations.append("• Recomendamos parques nacionales con monitoreo ambiental")
            
        if self.user_preferences['adventure'] > 0.6:
            recommendations.append("• Buscas aventura y adrenalina")
            recommendations.append("• Volcanes y deportes extremos son perfectos para ti")
            
        recommendations.append("")
        recommendations.append(f"🕒 Actualizado: {datetime.now().strftime('%H:%M:%S')}")
        
        return "\n".join(recommendations)
        
    def start_ai_recommendations(self):
        """Start AI recommendations in background"""
        def update_recommendations():
            while True:
                try:
                    recommendations = self.generate_ai_recommendations()
                    
                    # Update dashboard
                    if hasattr(self, 'recommendations_text'):
                        self.recommendations_text.delete('1.0', tk.END)
                        self.recommendations_text.insert('1.0', recommendations[:500] + "...")
                        
                    # Update AI tab
                    if hasattr(self, 'ai_recommendations_text'):
                        self.ai_recommendations_text.delete('1.0', tk.END)
                        self.ai_recommendations_text.insert('1.0', recommendations)
                        
                    time.sleep(30)  # Update every 30 seconds
                except Exception as e:
                    print(f"Error updating recommendations: {e}")
                    time.sleep(60)
                    
        thread = threading.Thread(target=update_recommendations, daemon=True)
        thread.start()
        
    def search_tours(self):
        """Search tours"""
        query = self.search_var.get().lower()
        if not query:
            self.display_tours()
            return
            
        # Filter tours
        filtered_tours = []
        for tour in self.tours:
            if (query in tour['name'].lower() or 
                query in tour['description'].lower() or
                any(query in feature.lower() for feature in tour['tech_features'])):
                filtered_tours.append(tour)
                
        # Clear and display filtered tours
        for widget in self.tours_scrollable.winfo_children():
            widget.destroy()
            
        for tour in filtered_tours:
            self.create_tour_card(tour)
            
    def search_hotels(self):
        """Search hotels"""
        query = self.hotel_search_var.get().lower()
        if not query:
            self.display_hotels()
            return
            
        # Filter hotels
        filtered_hotels = []
        for hotel in self.hotels:
            if (query in hotel['name'].lower() or 
                query in hotel['description'].lower() or
                any(query in feature.lower() for feature in hotel['tech_features'])):
                filtered_hotels.append(hotel)
                
        # Clear and display filtered hotels
        for widget in self.hotels_scrollable.winfo_children():
            widget.destroy()
            
        for hotel in filtered_hotels:
            self.create_hotel_card(hotel)
            
    def update_preferences(self):
        """Update user preferences"""
        for key, var in self.pref_vars.items():
            self.user_preferences[key] = var.get()
            
        self.user_preferences['budget'] = self.budget_var.get()
        
        messagebox.showinfo("Preferencias Actualizadas", 
                           "✅ Tus preferencias han sido actualizadas.\n"
                           "🤖 La IA generará nuevas recomendaciones personalizadas.")
        
    def book_tour(self, tour):
        """Book a tour"""
        if tour['availability'] <= 0:
            messagebox.showerror("No Disponible", "Este tour no tiene cupos disponibles")
            return
            
        result = messagebox.askyesno("Confirmar Reserva", 
                                   f"¿Confirmar reserva para:\n\n"
                                   f"🗺️ {tour['name']}\n"
                                   f"💰 ${tour['price']}\n"
                                   f"⏰ {tour['duration']}\n\n"
                                   f"¿Proceder con la reserva?")
        
        if result:
            # Simulate booking
            tour['availability'] -= 1
            messagebox.showinfo("Reserva Confirmada", 
                               f"✅ Reserva confirmada para {tour['name']}\n\n"
                               f"📧 Recibirás detalles por email\n"
                               f"📱 Descarga nuestra app para seguimiento GPS")
            self.display_tours()
            
    def book_hotel(self, hotel):
        """Book a hotel"""
        if hotel['rooms_available'] <= 0:
            messagebox.showerror("No Disponible", "Este hotel no tiene habitaciones disponibles")
            return
            
        result = messagebox.askyesno("Confirmar Reserva", 
                                   f"¿Confirmar reserva para:\n\n"
                                   f"🏨 {hotel['name']}\n"
                                   f"💰 ${hotel['price_per_night']}/noche\n\n"
                                   f"¿Proceder con la reserva?")
        
        if result:
            # Simulate booking
            hotel['rooms_available'] -= 1
            messagebox.showinfo("Reserva Confirmada", 
                               f"✅ Reserva confirmada en {hotel['name']}\n\n"
                               f"📧 Recibirás detalles por email\n"
                               f"🔑 Check-in con tecnología IoT disponible")
            self.display_hotels()
            
    def show_tour_details(self, tour):
        """Show tour details"""
        details = f"""
🗺️ DETALLES DEL TOUR

📍 Nombre: {tour['name']}
💰 Precio: ${tour['price']}
⏰ Duración: {tour['duration']}
⭐ Rating: {tour['rating']}/5
👥 Disponibles: {tour['availability']}

📝 Descripción:
{tour['description']}

🔬 Características Tecnológicas:
{chr(10).join('• ' + feature for feature in tour['tech_features'])}

📍 Ubicación:
Lat: {tour['location']['lat']:.4f}
Lng: {tour['location']['lng']:.4f}

🎯 Categorías:
{', '.join(tour['category'])}
        """
        
        messagebox.showinfo("Detalles del Tour", details)
        
    def show_hotel_details(self, hotel):
        """Show hotel details"""
        details = f"""
🏨 DETALLES DEL HOTEL

📍 Nombre: {hotel['name']}
💰 Precio: ${hotel['price_per_night']}/noche
⭐ Rating: {hotel['rating']}/5
🛏️ Habitaciones: {hotel['rooms_available']} disponibles

📝 Descripción:
{hotel['description']}

🔬 Características Tecnológicas:
{chr(10).join('• ' + feature for feature in hotel['tech_features'])}

📍 Ubicación:
Lat: {hotel['location']['lat']:.4f}
Lng: {hotel['location']['lng']:.4f}

🎯 Categorías:
{', '.join(hotel['category'])}
        """
        
        messagebox.showinfo("Detalles del Hotel", details)
        
    def toggle_premium(self, service_type):
        """Toggle premium status for services"""
        if service_type == 'tour':
            # Simple premium toggle for demo
            for tour in self.tours:
                if not tour['premium'] and random.random() < 0.3:
                    tour['premium'] = True
                    messagebox.showinfo("Premium Activado", 
                                       f"✅ {tour['name']} ahora es Premium\n"
                                       f"💎 Aparecerá primero en búsquedas\n"
                                       f"🤖 Prioridad en recomendaciones IA")
                    break
            self.display_tours()
        else:
            for hotel in self.hotels:
                if not hotel['premium'] and random.random() < 0.3:
                    hotel['premium'] = True
                    messagebox.showinfo("Premium Activado", 
                                       f"✅ {hotel['name']} ahora es Premium\n"
                                       f"💎 Aparecerá primero en búsquedas\n"
                                       f"🤖 Prioridad en recomendaciones IA")
                    break
            self.display_hotels()
            
    def update_premium_display(self, text_widget):
        """Update premium listings display"""
        premium_info = []
        premium_info.append("💎 SERVICIOS PREMIUM ACTIVOS")
        premium_info.append("=" * 40)
        premium_info.append("")
        
        premium_info.append("🗺️ TOURS PREMIUM:")
        for tour in self.tours:
            if tour['premium']:
                premium_info.append(f"• {tour['name']} - ${tour['price']}")
                
        premium_info.append("")
        premium_info.append("🏨 HOTELES PREMIUM:")
        for hotel in self.hotels:
            if hotel['premium']:
                premium_info.append(f"• {hotel['name']} - ${hotel['price_per_night']}/noche")
                
        premium_info.append("")
        premium_info.append("📊 BENEFICIOS PREMIUM:")
        premium_info.append("• Posición #1 en búsquedas")
        premium_info.append("• Insignia dorada visible")
        premium_info.append("• Prioridad en IA recomendaciones")
        premium_info.append("• Analytics detallados")
        premium_info.append("• Soporte 24/7")
        
        text_widget.delete('1.0', tk.END)
        text_widget.insert('1.0', '\n'.join(premium_info))
        
    def show_analytics(self):
        """Show analytics dashboard"""
        analytics = f"""
📊 ANALYTICS DASHBOARD

🎯 MÉTRICAS GENERALES:
• Total tours: {len(self.tours)}
• Tours premium: {sum(1 for t in self.tours if t['premium'])}
• Total hoteles: {len(self.hotels)}
• Hoteles premium: {sum(1 for h in self.hotels if h['premium'])}

👥 ENGAGEMENT:
• Búsquedas por día: {random.randint(150, 300)}
• Reservas por día: {random.randint(25, 50)}
• Conversión: {random.randint(15, 25)}%

🤖 IA PERFORMANCE:
• Recomendaciones generadas: {random.randint(500, 1000)}/día
• Precisión IA: {random.randint(85, 95)}%
• Satisfacción usuario: {random.randint(4, 5):.1f}/5

💰 REVENUE:
• Revenue tours: ${random.randint(5000, 15000)}/mes
• Revenue hoteles: ${random.randint(8000, 20000)}/mes
• Premium subscriptions: ${random.randint(2000, 5000)}/mes

🔄 Actualizado: {datetime.now().strftime('%Y-%m-%d %H:%M')}
        """
        
        messagebox.showinfo("📊 Analytics Dashboard", analytics)
        
def main():
    """Main application entry point"""
    try:
        app = SmartTourismPlatform()
        app.root.mainloop()
    except Exception as e:
        messagebox.showerror("Error", f"Error launching Smart Tourism Platform:\n{e}")

if __name__ == "__main__":
    main()
