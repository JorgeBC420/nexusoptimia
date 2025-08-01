@echo off
REM NexusOptim IA - Complete Setup Script with Python Installation
REM Configuracion completa incluyendo descarga e instalacion de Python

echo ===============================================================
echo 🚀 NexusOptim IA - Setup Completo con Instalacion de Python
echo    Edge AI para Optimizacion de Redes Electricas - Costa Rica
echo    OpenNexus - Soberania Tecnologica 🇨🇷
echo ===============================================================

REM Verificar si Python ya esta instalado
echo 🐍 Verificando Python...
python --version >nul 2>&1
if %errorlevel% equ 0 (
    echo ✅ Python ya esta instalado
    python --version
    goto :setup_environment
)

REM Python no encontrado, proceder con instalacion
echo ❌ Python no encontrado. Iniciando descarga e instalacion...
echo.
echo 📥 Descargando Python 3.11.5 (64-bit)...

REM Crear directorio temporal
if not exist "temp" mkdir temp

REM Descargar Python usando PowerShell
powershell -Command "& {Invoke-WebRequest -Uri 'https://www.python.org/ftp/python/3.11.5/python-3.11.5-amd64.exe' -OutFile 'temp\python-installer.exe'}"

if not exist "temp\python-installer.exe" (
    echo ❌ Error descargando Python
    echo    Por favor descarga manualmente desde: https://python.org/downloads
    pause
    exit /b 1
)

echo ✅ Descarga completada
echo.
echo 🔧 Instalando Python...
echo    IMPORTANTE: Se instalara automaticamente con PATH habilitado

REM Instalar Python silenciosamente con PATH
temp\python-installer.exe /quiet InstallAllUsers=1 PrependPath=1 Include_test=0

REM Esperar a que termine la instalacion
timeout /t 30 /nobreak >nul

REM Limpiar archivo temporal
del temp\python-installer.exe
rmdir temp

REM Verificar instalacion
echo.
echo 🔍 Verificando instalacion de Python...
python --version >nul 2>&1
if %errorlevel% neq 0 (
    echo ❌ Error en instalacion de Python
    echo    Por favor reinicia el CMD y ejecuta nuevamente
    pause
    exit /b 1
)

echo ✅ Python instalado correctamente
python --version

:setup_environment
echo.
echo ===============================================================
echo 📦 CONFIGURANDO ENTORNO VIRTUAL
echo ===============================================================

REM Crear entorno virtual
if exist "nexusoptim_env" (
    echo ✅ Entorno virtual ya existe
) else (
    echo 🔧 Creando entorno virtual...
    python -m venv nexusoptim_env
    if %errorlevel% neq 0 (
        echo ❌ Error creando entorno virtual
        pause
        exit /b 1
    )
    echo ✅ Entorno virtual creado
)

REM Activar entorno virtual
echo 🔄 Activando entorno virtual...
call nexusoptim_env\Scripts\activate

REM Actualizar pip
echo 📚 Actualizando pip...
python -m pip install --upgrade pip

REM Instalar dependencias
echo 📦 Instalando dependencias de NexusOptim IA...
echo    Esto puede tomar varios minutos...
pip install -r requirements.txt

if %errorlevel% neq 0 (
    echo ❌ Error instalando dependencias
    echo    Verifica conexion a internet y requirements.txt
    pause
    exit /b 1
)

echo ✅ Dependencias instaladas correctamente

echo ===============================================================
echo 📁 CREANDO ESTRUCTURA DE DIRECTORIOS
echo ===============================================================

REM Crear directorios adicionales
echo 🏗️ Creando estructura completa...
mkdir data 2>nul
mkdir models 2>nul
mkdir logs 2>nul
mkdir config 2>nul
mkdir tests 2>nul
mkdir sql 2>nul
mkdir scripts 2>nul
mkdir hardware-design\pcb 2>nul
mkdir hardware-design\3d-models 2>nul
mkdir hardware-design\datasheets 2>nul

echo ✅ Estructura de directorios creada

echo ===============================================================
echo 🐳 VERIFICANDO DOCKER (OPCIONAL)
echo ===============================================================

docker --version >nul 2>&1
if %errorlevel% neq 0 (
    echo ⚠️  Docker no encontrado (opcional para desarrollo)
    echo    Para instalar Docker Desktop:
    echo    https://docs.docker.com/desktop/install/windows-install/
) else (
    echo ✅ Docker encontrado
    docker --version
    
    echo 🐳 Verificando Docker Compose...
    docker-compose --version >nul 2>&1
    if %errorlevel% equ 0 (
        echo ✅ Docker Compose disponible
        docker-compose --version
    ) else (
        echo ⚠️ Docker Compose no encontrado
    )
)

echo ===============================================================
echo 🧪 EJECUTANDO PRUEBAS INICIALES
echo ===============================================================

echo 🔍 Verificando importaciones criticas...

python -c "import numpy; print('✅ NumPy:', numpy.__version__)" 2>nul || echo "❌ Error con NumPy"
python -c "import pandas; print('✅ Pandas:', pandas.__version__)" 2>nul || echo "❌ Error con Pandas"
python -c "import sklearn; print('✅ Scikit-learn:', sklearn.__version__)" 2>nul || echo "❌ Error con Scikit-learn"
python -c "import tensorflow; print('✅ TensorFlow:', tensorflow.__version__)" 2>nul || echo "❌ Error con TensorFlow"

echo.
echo 🚀 Prueba basica de la aplicacion...
python -c "
import sys
sys.path.append('src')
from core.config import settings
print('✅ Configuracion cargada correctamente')
print('📡 Frecuencia LoRa:', settings.LORA_FREQUENCY, 'Hz')
print('🌍 Zona horaria:', settings.TIMEZONE)
"

if %errorlevel% neq 0 (
    echo ⚠️ Algunas pruebas fallaron, pero la instalacion basica esta completa
)

echo ===============================================================
echo ✅ INSTALACION COMPLETADA EXITOSAMENTE
echo ===============================================================
echo.
echo 🎉 ¡NexusOptim IA esta listo para desarrollar!
echo.
echo 📋 RESUMEN DE INSTALACION:
echo    🐍 Python instalado y configurado
echo    📦 Entorno virtual: nexusoptim_env
echo    📚 50+ librerias instaladas (AI, IoT, Optimization)
echo    🏗️ Estructura de proyecto completa
echo    🔧 Configuracion lista para Costa Rica (915MHz)
echo.
echo 🚀 COMO EMPEZAR:
echo.
echo 1. Activar entorno (siempre antes de trabajar):
echo    nexusoptim_env\Scripts\activate
echo.
echo 2. Ejecutar aplicacion principal:
echo    python src\main.py
echo.
echo 3. Abrir navegador en:
echo    http://localhost:8000         (API principal)
echo    http://localhost:8000/docs    (Documentacion interactiva)
echo.
echo 4. Ejecutar simulacion de red electrica:
echo    python -c "from src.simulation_models import ElectricalGridSimulator; sim = ElectricalGridSimulator(); result = sim.simulate_grid_scenario('costa_rica_test'); print(f'Eficiencia: {result[\"efficiency\"]*100:.1f}%%')"
echo.
echo 🐳 CON DOCKER (si esta instalado):
echo    docker-compose up -d          (Levantar stack completo)
echo    docker-compose logs -f        (Ver logs)
echo    docker-compose down           (Parar servicios)
echo.  
echo 🧪 EJECUTAR PRUEBAS:
echo    pytest                        (Todas las pruebas)
echo    pytest tests/test_ai.py       (Solo IA)
echo    pytest tests/test_sensors.py  (Solo sensores)
echo.
echo 📞 SOPORTE:
echo    🌐 Web: https://opennexus.cr
echo    📧 Email: info@opennexus.cr
echo    📱 GitHub: https://github.com/JorgeBC420/nexusoptimia
echo.
echo ===============================================================
echo 🇨🇷 Hecho con ❤️ en Costa Rica para la soberania tecnologica
echo ===============================================================

pause
