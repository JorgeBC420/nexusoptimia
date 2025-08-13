"""
Configuración específica para gestión de agua en Costa Rica
Parámetros optimizados para infraestructura hídrica nacional
"""

# Configuración de sensores hídricos
WATER_SENSOR_CONFIG = {
    # Umbrales de detección de fugas
    "pressure_thresholds": {
        "minor_drop": 0.3,      # bar - caída menor
        "moderate_drop": 0.8,   # bar - caída moderada  
        "major_drop": 1.5,      # bar - caída mayor
        "critical_drop": 3.0    # bar - caída crítica
    },
    
    "flow_thresholds": {
        "minor_increase": 8,     # L/s - aumento menor
        "moderate_increase": 20, # L/s - aumento moderado
        "major_increase": 50,    # L/s - aumento mayor
        "critical_increase": 100 # L/s - aumento crítico
    },
    
    # Configuración de muestreo
    "sampling_interval": 60,     # segundos entre lecturas
    "analysis_window": 300,      # ventana de análisis (5 min)
    "trend_samples": 5,          # muestras para análisis de tendencia
}

# Configuración de equipos de respuesta
EMERGENCY_RESPONSE_CONFIG = {
    "response_times": {
        "gam": 45,          # minutos - Gran Área Metropolitana
        "urban": 60,        # minutos - centros urbanos
        "rural": 90,        # minutos - zonas rurales
        "remote": 120       # minutos - zonas remotas
    },
    
    "isolation_radius": 2.0,    # km - radio de búsqueda de válvulas
    "notification_timeout": 30, # segundos - timeout de notificaciones
    
    "severity_actions": {
        "minor": ["monitor", "schedule_inspection"],
        "moderate": ["send_team", "prepare_materials"],
        "major": ["emergency_dispatch", "isolate_section"],
        "critical": ["immediate_response", "auto_isolate", "media_alert"]
    }
}

# Configuración de sistemas de agua por región
WATER_SYSTEMS_CONFIG = {
    "aya": {
        "coverage_percentage": 65,
        "primary_sources": ["orosi", "tres_rios", "puente_mulas"],
        "main_treatment_plants": 12,
        "distribution_pressure": {"min": 1.5, "max": 4.0, "optimal": 2.5},
        "service_population": 2800000
    },
    
    "municipal": {
        "coverage_percentage": 25,
        "municipalities": ["Alajuela", "Cartago", "Heredia", "Puntarenas"],
        "independent_systems": 45,
        "distribution_pressure": {"min": 1.2, "max": 3.5, "optimal": 2.2},
        "service_population": 1200000
    },
    
    "asada": {
        "coverage_percentage": 10,
        "active_asadas": 1547,
        "rural_communities": 850,
        "distribution_pressure": {"min": 1.0, "max": 3.0, "optimal": 1.8},
        "service_population": 500000
    }
}

# Parámetros de pérdida de agua en Costa Rica
WATER_LOSS_PARAMETERS = {
    "national_average_loss": 52,  # % pérdidas promedio nacional
    "target_loss_reduction": 25,  # % objetivo de reducción
    
    "loss_by_system": {
        "aya": 48,          # % pérdidas AyA
        "municipal": 55,    # % pérdidas municipales
        "asada": 62         # % pérdidas ASADAS
    },
    
    "economic_impact": {
        "cost_per_m3": 350,         # colones por m³
        "daily_loss_m3": 850000,    # m³ perdidos diariamente
        "annual_loss_value": 108000000000  # colones anuales perdidos
    }
}

# Configuración de notificaciones
NOTIFICATION_CONFIG = {
    "whatsapp_api": {
        "enabled": True,
        "business_account": "opnexoxia_cr",
        "template_language": "es_CR"
    },
    
    "email_config": {
        "smtp_server": "smtp.gmail.com",
        "smtp_port": 587, 
        "sender_email": "alertas@opnexoxia.cr",
        "emergency_template": "emergency_leak_alert"
    },
    
    "sms_config": {
        "provider": "twilio",
        "country_code": "+506",
        "max_length": 160
    },
    
    "escalation_rules": {
        "no_response_timeout": 900,  # 15 minutos
        "auto_escalate_severity": ["major", "critical"],
        "backup_contacts": True
    }
}

# Integración con sistemas existentes
INTEGRATION_CONFIG = {
    "aya_scada": {
        "enabled": False,  # Pendiente de integración
        "api_endpoint": "https://scada.aya.go.cr/api/v1",
        "authentication": "oauth2"
    },
    
    "municipal_systems": {
        "alajuela": {"enabled": False, "contact": "sistemas@alajuela.go.cr"},
        "cartago": {"enabled": False, "contact": "acueductos@cartago.go.cr"},
        "heredia": {"enabled": False, "contact": "agua@heredia.go.cr"}
    },
    
    "external_apis": {
        "google_maps": True,
        "weather_service": "imn.ac.cr",
        "emergency_911": {"integration": False, "future": True}
    }
}

# Configuración de base de datos hídrica
DATABASE_CONFIG = {
    "water_sensors_table": "water_sensors",
    "leak_alerts_table": "leak_alerts", 
    "response_teams_table": "response_teams",
    "valve_controllers_table": "valve_controllers",
    "water_quality_table": "water_quality",
    
    "retention_policy": {
        "sensor_data": "2 years",
        "alerts": "5 years", 
        "emergency_records": "10 years"
    },
    
    "backup_frequency": "daily",
    "replication": "enabled"
}

# Métricas y KPIs del sistema hídrico
METRICS_CONFIG = {
    "performance_kpis": [
        "detection_accuracy",
        "false_positive_rate", 
        "response_time_avg",
        "water_loss_reduction",
        "system_uptime"
    ],
    
    "water_kpis": [
        "daily_production_m3",
        "daily_consumption_m3", 
        "distribution_efficiency",
        "pressure_stability",
        "quality_compliance"
    ],
    
    "business_kpis": [
        "cost_savings_annual",
        "loss_prevention_m3",
        "maintenance_reduction",
        "customer_satisfaction",
        "regulatory_compliance"
    ],
    
    "reporting_frequency": {
        "real_time": ["alerts", "sensor_status"],
        "hourly": ["consumption", "pressure"],
        "daily": ["loss_calculation", "efficiency"],
        "weekly": ["performance_summary"],
        "monthly": ["business_report"]
    }
}
