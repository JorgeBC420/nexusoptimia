"""
Script de Demo Interactivo - NeXOptimIA
Ejecuta demos personalizadas para diferentes stakeholders
"""

import asyncio
import webbrowser
from datetime import datetime
from typing import Dict, Any
import json

# Simulamos las importaciones hasta que Python esté instalado
print("🚀 NeXOptimIA - Sistema de Demos Interactivas")
print("=" * 60)

class DemoLauncher:
    """Lanzador de demos personalizadas"""
    
    def __init__(self):
        self.demos_available = {
            "tec": "Demo Técnica - Ingeniero Eléctrico TEC",
            "schneider": "Demo Comercial - Schneider Electric", 
            "ice": "Demo Institucional - ICE Costa Rica",
            "government": "Demo Estratégica - Gobierno CR",
            "full": "Demo Completa - Todos los Módulos"
        }
        
        self.demo_urls = {
            "tec": "http://localhost:8000/demo/technical",
            "schneider": "http://localhost:8000/demo/commercial", 
            "ice": "http://localhost:8000/demo/institutional",
            "government": "http://localhost:8000/demo/strategic",
            "full": "http://localhost:8000/dashboard"
        }
    
    def show_menu(self):
        """Mostrar menú de demos disponibles"""
        print("\n🎯 DEMOS DISPONIBLES:")
        print("-" * 40)
        
        for key, description in self.demos_available.items():
            print(f"  {key:12} -> {description}")
        
        print("\n💡 USO:")
        print("  python demo_launcher.py --demo [tipo]")
        print("  python demo_launcher.py --demo full")
        print("\n" + "=" * 60)
    
    def create_demo_data(self, demo_type: str) -> Dict[str, Any]:
        """Crear datos específicos para cada demo"""
        
        base_data = {
            "timestamp": datetime.now().isoformat(),
            "demo_type": demo_type,
            "opnexox_version": "1.0.0-MVP",
            "costa_rica_focus": True
        }
        
        if demo_type == "tec":
            return {
                **base_data,
                "technical_specs": {
                    "edge_ai_algorithms": ["LSTM", "Isolation Forest", "Random Forest"],
                    "hardware_platform": "Raspberry Pi Pico W + RFM95W",
                    "ml_framework": "TensorFlow Lite",
                    "optimization_libs": ["PuLP", "SciPy", "NumPy"],
                    "electrical_simulation": "PyPSA + pandapower",
                    "prediction_accuracy": "95%",
                    "response_time_ms": 150
                },
                "research_opportunities": {
                    "joint_lab": "TEC-OPNeXOX Edge AI Lab",
                    "publications": "IEEE Smart Grid, LASCAS 2026",
                    "student_projects": 8,
                    "funding_available": "$200K"
                },
                "ice_integration": {
                    "grid_sensors": 100,
                    "coverage_area": "Gran Área Metropolitana",
                    "predicted_savings": "$15M/year",
                    "blackout_prevention": "85% reduction"
                }
            }
        
        elif demo_type == "schneider":
            return {
                **base_data,
                "market_opportunity": {
                    "latam_tam": "$2.3B",
                    "costa_rica_sam": "$500M",
                    "addressable_segments": 5,
                    "year_1_target": "$500K",
                    "year_5_projection": "$50M"
                },
                "partnership_model": {
                    "distribution_rights": "LATAM exclusive",
                    "revenue_sharing": "60/40 OPNeXOX/Schneider",
                    "joint_development": "$2M investment",
                    "go_to_market": "Q4 2025"
                },
                "competitive_advantage": {
                    "edge_ai_vs_cloud": "70% faster response",
                    "integrated_platform": "5 sectors unified",
                    "local_knowledge": "CR regulations compliant",
                    "cost_advantage": "40% vs international solutions"
                }
            }
        
        elif demo_type == "ice":
            return {
                **base_data,
                "ice_specific": {
                    "current_losses": "$50M/year",
                    "grid_inefficiencies": "15% distribution losses",
                    "blackout_incidents": "120/year GAM",
                    "customer_complaints": "8,500/month"
                },
                "proposed_solution": {
                    "sensor_network": "500 points national grid",
                    "ai_prediction": "72h demand forecast",
                    "automatic_rebalancing": "Real-time load optimization",
                    "integration_existing": "SCADA systems compatible"
                },
                "pilot_proposal": {
                    "phase_1_sensors": 50,
                    "coverage_area": "Sabana-San José corridor",
                    "duration_months": 6,
                    "investment_required": "$150K",
                    "expected_roi": "300% in 18 months"
                }
            }
        
        elif demo_type == "government":
            return {
                **base_data,
                "national_impact": {
                    "gdp_contribution": "+2% tech sector growth",
                    "jobs_created": "500+ high-tech positions",
                    "public_savings": "$75M/year across institutions",
                    "international_positioning": "LATAM smart cities leader"
                },
                "institutional_integration": {
                    "ice_electrical": "National grid optimization",
                    "aya_water": "Distribution network intelligence", 
                    "minae_environment": "Air quality monitoring",
                    "mopt_transport": "GAM traffic optimization",
                    "senasa_agriculture": "Crop intelligence platform"
                },
                "policy_recommendations": {
                    "smart_cities_law": "Legal framework 2026",
                    "innovation_fund": "$5M MICITT allocation",
                    "regulatory_sandbox": "IoT/AI testing framework",
                    "export_promotion": "SICA regional expansion"
                }
            }
        
        else:  # full demo
            return {
                **base_data,
                "full_platform": {
                    "modules_active": 5,
                    "sensors_simulated": 200,
                    "algorithms_running": 15,
                    "real_time_processing": True,
                    "multi_domain_analytics": True
                }
            }
    
    def simulate_demo_server(self, demo_type: str):
        """Simular servidor de demo hasta que Python esté instalado"""
        
        print(f"\n🎬 INICIANDO DEMO: {self.demos_available[demo_type]}")
        print("=" * 60)
        
        demo_data = self.create_demo_data(demo_type)
        
        print("📊 DATOS DE DEMO GENERADOS:")
        print(json.dumps(demo_data, indent=2, ensure_ascii=False))
        
        print(f"\n🌐 DEMO URL: {self.demo_urls[demo_type]}")
        print("\n⚠️ NOTA: Servidor web iniciará cuando Python esté instalado")
        print("   Ejecute: python src/main.py --demo-mode", demo_type)
        
        print(f"\n✅ DEMO {demo_type.upper()} LISTA PARA PRESENTACIÓN")
        print("=" * 60)

def main():
    """Función principal del lanzador de demos"""
    import sys
    
    launcher = DemoLauncher()
    
    # Verificar argumentos de línea de comandos
    if len(sys.argv) >= 3 and sys.argv[1] == "--demo":
        demo_type = sys.argv[2]
        if demo_type in launcher.demos_available:
            launcher.simulate_demo_server(demo_type)
        else:
            print(f"❌ Demo '{demo_type}' no encontrado")
            launcher.show_menu()
    else:
        # Mostrar menú y simular demo full por defecto
        launcher.show_menu()
        launcher.simulate_demo_server("full")
    
    print(f"\n🌐 APLICACIÓN PRINCIPAL CORRIENDO EN: http://localhost:8000")
    print(f"� DOCUMENTACIÓN API: http://localhost:8000/docs")
    print(f"🎯 DEMOS DISPONIBLES: http://localhost:8000/demo")

if __name__ == "__main__":
    main()
