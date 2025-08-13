# Lista de Archivos para Deployment - countercorehazardav.com
# NeXOptimIA (Producto estrella de OPNeXOX Hardware y Software) - Producción Web

## 📁 ARCHIVOS ESENCIALES (subir al servidor):

### 🔧 APLICACIÓN PRINCIPAL:
src/main_simple.py                    # ✅ Aplicación FastAPI principal
src/core/config_simple.py             # ✅ Configuración básica
demo_launcher.py                      # ✅ Sistema de demos

### 📄 DOCUMENTACIÓN Y PRESENTACIONES:
PRESENTACION_MVP.md                   # ✅ Presentación ejecutiva
GUIA_DEMOS.md                        # ✅ Guía de demos personalizadas
PLAN_FABRICACION_HARDWARE.md         # ✅ Plan de hardware (OPNeXOX Chips)
readme.txt                           # ✅ Documentación principal

### 🏗️ ARQUITECTURA COMPLETA:
src/opnexox-core/                 # ✅ Algoritmos Edge AI
├── __init__.py
├── lstm_predictor.py
├── anomaly_detector.py
└── optimization_engine.py

src/water-management/                # ✅ Gestión hídrica
├── __init__.py
├── leak_detection.py
├── network_simulator.py
└── emergency_response.py

src/environmental-monitoring/        # ✅ Monitoreo ambiental
└── __init__.py

src/smart-transportation/           # ✅ Transporte inteligente
└── __init__.py

src/smart-agriculture/              # ✅ Agricultura inteligente
└── __init__.py

### ⚙️ CONFIGURACIÓN:
requirements.txt                     # ✅ Dependencias Python
.env                                # ⚠️ Variables de entorno (crear)
hardware-design/README.md           # ✅ Especificaciones hardware

### 🎬 ASSETS ADICIONALES:
static/                             # 📁 Crear para CSS/JS/imágenes
templates/                          # 📁 Crear para HTML templates

## 🚫 NO SUBIR (archivos locales):
*.bat                               # Scripts Windows
*.log                               # Logs locales
__pycache__/                        # Cache Python
.git/                              # Repositorio Git (opcional)
opnexox.db                      # Base datos local
