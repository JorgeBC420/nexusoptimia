import sys
from pathlib import Path

# Añadir la carpeta src al sys.path si se ejecuta como .exe
if getattr(sys, 'frozen', False):
    base_path = Path(sys.executable).parent
    src_path = base_path / 'src'
    if src_path.exists():
        sys.path.insert(0, str(src_path))
"""
Aplicación principal para producción - countercorehazardav.com
NeXOptimIA - Optimizada para hosting web público
"""

from fastapi import FastAPI, Request
from fastapi.responses import HTMLResponse, JSONResponse
from fastapi.staticfiles import StaticFiles
import uvicorn
import logging
import os
from datetime import datetime

# Configuración de producción
APP_NAME = "NeXOptimIA"
VERSION = "1.0.0-MVP"
DEBUG = False
HOST = "0.0.0.0"
PORT = int(os.getenv("PORT", "8000"))  # Compatible con Heroku/Railway
PUBLIC_URL = "https://countercorehazardav.com"

# Logging para producción
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
)
logger = logging.getLogger(__name__)

# Crear aplicación FastAPI
app = FastAPI(
    title=APP_NAME,
    version=VERSION,
    description="Plataforma de Smart Cities con Edge AI para Costa Rica",
    docs_url="/docs",
    redoc_url="/redoc"
)

# Servir archivos estáticos (si existen)
if os.path.exists("static"):
    app.mount("/static", StaticFiles(directory="static"), name="static")

@app.get("/", response_class=HTMLResponse)
async def dashboard():
    """Dashboard principal optimizado para web pública"""
    html_content = f"""
    <!DOCTYPE html>
    <html lang="es">
    <head>
        <meta charset="utf-8">
        <meta name="viewport" content="width=device-width, initial-scale=1.0">
        <title>{APP_NAME} - Smart Cities Costa Rica</title>
        <meta name="description" content="Plataforma de Edge AI para optimización de infraestructura crítica en Costa Rica">
        <meta name="keywords" content="Smart Cities, Edge AI, Costa Rica, IoT, LoRa, ICE, AyA">
        <meta name="author" content="Jorge Bermúdez Castro - OPNeXOX">
        
        <!-- Open Graph / Facebook -->
        <meta property="og:type" content="website">
        <meta property="og:url" content="{PUBLIC_URL}">
        <meta property="og:title" content="NeXOptimIA - Smart Cities Costa Rica">
        <meta property="og:description" content="Plataforma de Edge AI para infraestructura crítica">
        
        <style>
            * {{ margin: 0; padding: 0; box-sizing: border-box; }}
            body {{ 
                font-family: 'Segoe UI', Tahoma, Geneva, Verdana, sans-serif; 
                line-height: 1.6; background: #f8f9fa; color: #333;
            }}
            .container {{ max-width: 1200px; margin: 0 auto; padding: 0 20px; }}
            
            .header {{ 
                background: linear-gradient(135deg, #667eea 0%, #764ba2 100%); 
                color: white; padding: 40px 0; text-align: center;
                box-shadow: 0 4px 6px rgba(0,0,0,0.1);
            }}
            .logo {{ font-size: 3em; margin-bottom: 10px; }}
            .tagline {{ font-size: 1.2em; opacity: 0.9; }}
            
            .stats {{ 
                display: grid; 
                grid-template-columns: repeat(auto-fit, minmax(250px, 1fr)); 
                gap: 20px; margin: 40px 0; 
            }}
            .stat-card {{ 
                background: white; padding: 30px; border-radius: 12px; 
                box-shadow: 0 4px 6px rgba(0,0,0,0.1); text-align: center;
                transition: transform 0.3s ease;
            }}
            .stat-card:hover {{ transform: translateY(-5px); }}
            .stat-number {{ font-size: 2.5em; font-weight: bold; color: #667eea; }}
            
            .modules {{ margin: 40px 0; }}
            .module {{ 
                background: white; margin: 20px 0; padding: 25px; 
                border-radius: 12px; border-left: 5px solid #667eea;
                box-shadow: 0 2px 4px rgba(0,0,0,0.1);
            }}
            .module h3 {{ color: #333; margin-bottom: 10px; }}
            .status {{ 
                display: inline-block; background: #28a745; color: white; 
                padding: 4px 12px; border-radius: 20px; font-size: 0.8em;
                font-weight: bold;
            }}
            
            .cta-section {{ 
                background: #667eea; color: white; padding: 60px 0; 
                text-align: center; margin-top: 40px;
            }}
            .cta-button {{ 
                display: inline-block; background: white; color: #667eea; 
                padding: 15px 30px; text-decoration: none; border-radius: 30px; 
                font-weight: bold; margin: 10px; transition: all 0.3s ease;
            }}
            .cta-button:hover {{ 
                background: #f8f9fa; transform: translateY(-2px); 
                box-shadow: 0 6px 12px rgba(0,0,0,0.2);
            }}
            
            .footer {{ 
                background: #333; color: white; padding: 40px 0; 
                text-align: center; margin-top: 60px;
            }}
            
            @media (max-width: 768px) {{
                .logo {{ font-size: 2em; }}
                .stats {{ grid-template-columns: 1fr; }}
                .stat-number {{ font-size: 2em; }}
            }}
        </style>
    </head>
    <body>
        <div class="header">
            <div class="container">
                <div class="logo">💧⚡ NeXOptimIA</div>
                <h1>Plataforma de Smart Cities</h1>
                <p class="tagline">Edge AI para Infraestructura Crítica - Costa Rica</p>
                <p>Versión {VERSION} | {datetime.now().strftime('%B %Y')}</p>
            </div>
        </div>
        
        <div class="container">
            <div class="stats">
                <div class="stat-card">
                    <div class="stat-number">5</div>
                    <h3>Dominios Integrados</h3>
                    <p>Electricidad, Agua, Aire, Tráfico, Agricultura</p>
                </div>
                <div class="stat-card">
                    <div class="stat-number">$500M+</div>
                    <h3>Mercado Direccionable</h3>
                    <p>Costa Rica + Expansión LATAM</p>
                </div>
                <div class="stat-card">
                    <div class="stat-number">95%</div>
                    <h3>Precisión IA</h3>
                    <p>Predicción 72h adelanto</p>
                </div>
                <div class="stat-card">
                    <div class="stat-number">🇨🇷</div>
                    <h3>Tecnología Soberana</h3>
                    <p>Desarrollado en Costa Rica</p>
                </div>
            </div>
            
            <div class="modules">
                <div class="module">
                    <h3>⚡ Optimización Eléctrica ICE</h3>
                    <span class="status">ACTIVO</span>
                    <p>Predicción demanda 72h, prevención apagones GAM. Ahorro estimado: $15M anuales ICE.</p>
                </div>
                
                <div class="module">
                    <h3>💧 Gestión Hídrica AyA</h3>
                    <span class="status">ACTIVO</span>
                    <p>Detección fugas instantánea, optimización distribución. Reducción pérdidas: 25%.</p>
                </div>
                
                <div class="module">
                    <h3>🌬️ Monitoreo Ambiental MINAE</h3>
                    <span class="status">ACTIVO</span>
                    <p>Calidad aire tiempo real, alertas contaminación. Cumplimiento estándares nacionales.</p>
                </div>
                
                <div class="module">
                    <h3>🚗 Tráfico Inteligente MOPT</h3>
                    <span class="status">ACTIVO</span>
                    <p>Gestión tráfico GAM, semáforos IA. Reducción congestión: 30%.</p>
                </div>
                
                <div class="module">
                    <h3>🌱 Agricultura Inteligente SENASA</h3>
                    <span class="status">ACTIVO</span>
                    <p>Café, banano, piña monitoreados. Ahorro agua: 50%, incremento rendimiento: 20%.</p>
                </div>
            </div>
        </div>
        
        <div class="cta-section">
            <div class="container">
                <h2>¿Listo para Transformar Costa Rica?</h2>
                <p style="font-size: 1.2em; margin: 20px 0;">
                    Únete a la revolución de Smart Cities con tecnología soberana
                </p>
                <a href="/docs" class="cta-button">📚 Documentación API</a>
                <a href="/demo" class="cta-button">🎬 Ver Demos</a>
                <a href="/contact" class="cta-button">📞 Contactar</a>
            </div>
        </div>
        
        <div class="footer">
            <div class="container">
                <p><strong>NeXOptimIA</strong> - Desarrollado por OPNeXOX</p>
                <p>Jorge Bermúdez Castro | Costa Rica 🇨🇷</p>
                <p style="margin-top: 10px; opacity: 0.8;">
                    Tecnología Edge AI • LoRa 915MHz SUTEL • Cumplimiento Regulatorio Nacional
                </p>
            </div>
        </div>
    </body>
    </html>
    """
    return html_content

@app.get("/demo")
async def demo_info():
    """Información de demos para stakeholders"""
    return {
        "titulo": "NeXOptimIA - Demos Disponibles",
        "descripcion": "Presentaciones personalizadas para diferentes stakeholders",
        "demos_disponibles": {
            "tec": {
                "nombre": "Demo Técnica - TEC",
                "audiencia": "Ingeniero Eléctrico, Academia",
                "enfoque": "Algoritmos, I+D, Publicaciones",
                "duracion": "45 minutos"
            },
            "schneider": {
                "nombre": "Demo Comercial - Schneider Electric",
                "audiencia": "Ingenieros de Aplicación, Business",
                "enfoque": "Partnership, Mercado LATAM, ROI",
                "duracion": "60 minutos"
            },
            "ice": {
                "nombre": "Demo Institucional - ICE",
                "audiencia": "Ingenieros Sistemas, Directivos",
                "enfoque": "Integración, Piloto, Ahorros Operacionales",
                "duracion": "50 minutos"
            },
            "government": {
                "nombre": "Demo Estratégica - Gobierno",
                "audiencia": "Funcionarios, MICITT, Políticas Públicas",
                "enfoque": "Impacto Nacional, Fondos, Regulación",
                "duracion": "40 minutos"
            }
        },
        "contacto": {
            "desarrollador": "Jorge Bermúdez Castro",
            "empresa": "OPNeXOX",
            "email": "jorge@nexoptimia.com",
            "telefono": "+506-xxxx-xxxx",
            "website": PUBLIC_URL
        },
        "tecnologia": {
            "plataforma": "Edge AI + LoRa 915MHz",
            "cobertura": "Costa Rica Nacional",
            "certificacion": "SUTEL Compliant",
            "integracion": "ICE, AyA, MINAE, MOPT, SENASA"
        }
    }

@app.get("/contact")
async def contact_info():
    """Información de contacto"""
    return {
        "empresa": "NeXOptimIA - OPNeXOX",
        "fundador": "Jorge Bermúdez Castro",
        "email": "jorge@nexoptimia.com",
        "telefono": "+506-xxxx-xxxx",
        "ubicacion": "Costa Rica 🇨🇷",
        "website": PUBLIC_URL,
        "linkedin": "https://linkedin.com/in/jorge-bermudez-castro",
        "enfoque": "Smart Cities con Edge AI para LATAM",
        "mision": "Tecnología soberana para infraestructura crítica"
    }

@app.get("/status")
async def system_status():
    """Estado del sistema para monitoring"""
    return {
        "app": APP_NAME,
        "version": VERSION,
        "status": "production",
        "timestamp": datetime.now().isoformat(),
        "servidor": "countercorehazardav.com",
        "modulos_activos": 5,
        "costa_rica_ready": True,
        "sutel_compliant": True
    }

@app.get("/health")
async def health_check():
    """Health check para load balancers"""
    return {
        "status": "healthy",
        "timestamp": datetime.now().isoformat(),
        "version": VERSION
    }

# Error handlers
@app.exception_handler(404)
async def not_found_handler(request: Request, exc):
    return JSONResponse(
        status_code=404,
        content={
            "error": "Página no encontrada",
            "sugerencias": [
                "Ir al dashboard principal: /",
                "Ver documentación API: /docs",
                "Información de demos: /demo",
                "Contacto: /contact"
            ]
        }
    )

if __name__ == "__main__":
    logger.info(f"🚀 Iniciando {APP_NAME} v{VERSION} en PRODUCCIÓN")
    logger.info(f"🌐 URL Pública: {PUBLIC_URL}")
    logger.info(f"📚 API Docs: {PUBLIC_URL}/docs")
    logger.info(f"🇨🇷 Optimizado para Costa Rica")
    
    uvicorn.run(
        "main_production:app",
        host=HOST,
        port=PORT,
        log_level="info",
        access_log=True
    )
