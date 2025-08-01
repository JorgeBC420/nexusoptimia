@echo off
REM NexusOptim IA - Quick Development Launcher
REM Script para desarrollo rapido y testing

title NexusOptim IA - Development Environment

:menu
cls
echo ===============================================================
echo 🚀 NexusOptim IA - Entorno de Desarrollo
echo    Edge AI para Optimizacion Electrica - Costa Rica
echo ===============================================================
echo.
echo Selecciona una opcion:
echo.
echo 1. 🔄 Activar entorno y ejecutar aplicacion principal
echo 2. 🧪 Ejecutar simulacion de red electrica
echo 3. 🔍 Ejecutar pruebas automatizadas
echo 4. 📊 Generar reporte de estado del sistema
echo 5. 🐳 Levantar stack Docker completo
echo 6. 🔧 Abrir shell de desarrollo
echo 7. 📖 Abrir documentacion en navegador
echo 8. 🛠️ Reinstalar dependencias
echo 9. ❌ Salir
echo.
set /p choice="Ingresa tu opcion (1-9): "

if "%choice%"=="1" goto :run_main
if "%choice%"=="2" goto :run_simulation
if "%choice%"=="3" goto :run_tests
if "%choice%"=="4" goto :system_report
if "%choice%"=="5" goto :docker_stack
if "%choice%"=="6" goto :dev_shell
if "%choice%"=="7" goto :open_docs
if "%choice%"=="8" goto :reinstall_deps
if "%choice%"=="9" goto :exit

echo Opcion invalida. Presiona cualquier tecla para continuar...
pause >nul
goto :menu

:run_main
cls
echo 🚀 Iniciando NexusOptim IA...
echo ===============================================================
call nexusoptim_env\Scripts\activate
echo ✅ Entorno activado
echo 🔧 Configurando variables de entorno...
set ENVIRONMENT=development
set LOG_LEVEL=DEBUG
echo 🌐 Iniciando servidor FastAPI...
echo.
echo    API disponible en: http://localhost:8000
echo    Documentacion en:   http://localhost:8000/docs
echo    Health check:       http://localhost:8000/health
echo.
echo Presiona Ctrl+C para detener el servidor
echo ===============================================================
python src\main.py
pause
goto :menu

:run_simulation
cls
echo 🧮 Ejecutando Simulacion de Red Electrica de Costa Rica...
echo ===============================================================
call nexusoptim_env\Scripts\activate
python -c "
print('🇨🇷 Simulando red electrica de Costa Rica...')
import sys
sys.path.append('src')

try:
    from simulation_models import ElectricalGridSimulator, ScenarioManager
    
    # Crear simulador
    simulator = ElectricalGridSimulator()
    print('✅ Simulador inicializado')
    
    # Ejecutar simulacion basica
    print('🔄 Ejecutando simulacion de 24 horas...')
    result = simulator.simulate_grid_scenario('desarrollo_test', days=1)
    
    print(f'📊 RESULTADOS DE SIMULACION:')
    print(f'   🔋 Demanda pico: {result[\"peak_demand\"]:.1f} MW')
    print(f'   ⚡ Eficiencia total: {result[\"efficiency\"]*100:.2f}%%')
    print(f'   📉 Perdidas totales: {result[\"total_losses\"]:.2f} MW')
    print(f'   📈 Energia demandada: {result[\"total_energy_demand\"]:.1f} MWh')
    
    # Ejecutar optimizacion
    print('')
    print('🎯 Ejecutando optimizacion...')
    optimization = simulator.optimize_network(result)
    
    print(f'📈 OPTIMIZACION:')
    print(f'   🔺 Mejora eficiencia: +{optimization[\"improvement\"]*100:.2f}%%')
    print(f'   💰 Ahorro proyectado: {optimization[\"projected_savings_mw\"]:.1f} MW')
    print(f'   💵 ROI anual: ${optimization[\"roi_estimate\"][\"annual_savings_usd\"]:,.0f}')
    
    print('')
    print('✅ Simulacion completada exitosamente')
    
except Exception as e:
    print(f'❌ Error en simulacion: {e}')
    import traceback
    traceback.print_exc()
"
echo.
echo ===============================================================
pause
goto :menu

:run_tests
cls
echo 🧪 Ejecutando Pruebas Automatizadas...
echo ===============================================================
call nexusoptim_env\Scripts\activate

echo 🔍 Verificando configuracion de pruebas...
if not exist "tests" (
    echo 📁 Creando directorio de pruebas...
    mkdir tests
    
    echo # Pruebas basicas de NexusOptim IA> tests\test_basic.py
    echo.>> tests\test_basic.py
    echo import pytest>> tests\test_basic.py
    echo from src.core.config import settings>> tests\test_basic.py
    echo.>> tests\test_basic.py
    echo def test_config_loading():>> tests\test_basic.py
    echo     assert settings.LORA_FREQUENCY == 915000000>> tests\test_basic.py
    echo     assert settings.TIMEZONE == "America/Costa_Rica">> tests\test_basic.py
    echo.>> tests\test_basic.py
    echo def test_basic_imports():>> tests\test_basic.py
    echo     import numpy>> tests\test_basic.py
    echo     import pandas>> tests\test_basic.py
    echo     import tensorflow>> tests\test_basic.py
    echo     assert True>> tests\test_basic.py
)

echo 🏃 Ejecutando pytest...
pytest -v --tb=short
echo.
echo ===============================================================
pause
goto :menu

:system_report
cls
echo 📊 Generando Reporte de Estado del Sistema...
echo ===============================================================
call nexusoptim_env\Scripts\activate

python -c "
import sys, os
from datetime import datetime
import pkg_resources

print('📋 REPORTE DE ESTADO - NexusOptim IA')
print('=' * 60)
print(f'🕐 Fecha: {datetime.now().strftime(\"%%Y-%%m-%%d %%H:%%M:%%S\")}')  
print(f'🐍 Python: {sys.version.split()[0]}')
print(f'💻 Sistema: {os.name}')
print()

print('📦 DEPENDENCIAS CRITICAS:')
critical_packages = ['numpy', 'pandas', 'tensorflow', 'scikit-learn', 'fastapi']
for package in critical_packages:
    try:
        version = pkg_resources.get_distribution(package).version
        print(f'   ✅ {package}: {version}')
    except:
        print(f'   ❌ {package}: NO INSTALADO')

print()
print('🔧 CONFIGURACION:')
sys.path.append('src')
try:
    from core.config import settings
    print(f'   📡 LoRa Frequency: {settings.LORA_FREQUENCY} Hz')
    print(f'   🌍 Timezone: {settings.TIMEZONE}')
    print(f'   🔍 Environment: {settings.ENVIRONMENT}')
    print(f'   📊 Log Level: {settings.LOG_LEVEL}')
except Exception as e:
    print(f'   ❌ Error cargando config: {e}')

print()
print('📁 ESTRUCTURA DE ARCHIVOS:')
key_files = ['src/main.py', 'requirements.txt', 'docker-compose.yml', '.env']
for file in key_files:
    status = '✅' if os.path.exists(file) else '❌'
    print(f'   {status} {file}')

print()
print('🚀 SERVICIOS:')
print('   🌐 API Server: http://localhost:8000')
print('   📖 Docs: http://localhost:8000/docs')
print('   ❤️ Health: http://localhost:8000/health')

print()
print('=' * 60)
"

echo ===============================================================
pause
goto :menu

:docker_stack
cls
echo 🐳 Levantando Stack Docker Completo...
echo ===============================================================

docker --version >nul 2>&1
if %errorlevel% neq 0 (
    echo ❌ Docker no esta instalado o no esta en PATH
    echo    Instala Docker Desktop desde: https://docker.com/get-started
    pause
    goto :menu
)

echo 🔧 Verificando docker-compose.yml...
if not exist "docker-compose.yml" (
    echo ❌ docker-compose.yml no encontrado
    pause
    goto :menu
)

echo 🚀 Ejecutando docker-compose up -d...
docker-compose up -d

if %errorlevel% equ 0 (
    echo ✅ Stack Docker iniciado correctamente
    echo.
    echo 🌐 Servicios disponibles:
    echo    📊 NexusOptim IA:    http://localhost:8000
    echo    📈 Grafana:          http://localhost:3000
    echo    🔧 Node-RED:         http://localhost:1880
    echo    💾 TimescaleDB:      localhost:5432
    echo    📡 MQTT Broker:      localhost:1883
    echo.
    echo 📋 Para ver logs: docker-compose logs -f
    echo 🛑 Para parar: docker-compose down
) else (
    echo ❌ Error iniciando stack Docker
)

echo ===============================================================
pause
goto :menu

:dev_shell
cls
echo 🔧 Abriendo Shell de Desarrollo...
echo ===============================================================
echo 🐍 Activando entorno Python...
call nexusoptim_env\Scripts\activate
echo ✅ Entorno activado
echo.
echo 💡 COMANDOS UTILES:
echo    python src\main.py                    # Ejecutar aplicacion
echo    pytest                                # Ejecutar pruebas  
echo    pip install nombre_paquete            # Instalar dependencia
echo    python -c "import modulo; help(modulo)" # Ayuda de modulo
echo.
echo Escribe 'exit' para volver al menu principal
echo ===============================================================
cmd /k
goto :menu

:open_docs
cls
echo 📖 Abriendo Documentacion...
echo ===============================================================

REM Verificar si el servidor esta corriendo
echo 🔍 Verificando si API esta corriendo...
netstat -an | find "8000" >nul
if %errorlevel% equ 0 (
    echo ✅ API detectada en puerto 8000
    echo 🌐 Abriendo documentacion interactiva...
    start http://localhost:8000/docs
    start http://localhost:8000
) else (
    echo ⚠️ API no esta corriendo
    echo 🚀 Iniciando servidor para documentacion...
    call nexusoptim_env\Scripts\activate
    start /b python src\main.py
    timeout /t 5 /nobreak >nul
    echo 🌐 Abriendo documentacion...
    start http://localhost:8000/docs
)

echo 📚 Documentacion adicional:
echo    📋 README: https://github.com/JorgeBC420/nexusoptimia
echo    🔧 Hardware: Revisar hardware-design\README.md
echo ===============================================================
pause
goto :menu

:reinstall_deps
cls
echo 🛠️ Reinstalando Dependencias...
echo ===============================================================
call nexusoptim_env\Scripts\activate
echo 🔄 Actualizando pip...
python -m pip install --upgrade pip
echo 📦 Reinstalando requirements.txt...
pip install --upgrade -r requirements.txt
echo ✅ Dependencias actualizadas
echo ===============================================================
pause
goto :menu

:exit
cls
echo 👋 Gracias por usar NexusOptim IA
echo    Desarrollando soberania tecnologica para Costa Rica 🇨🇷
echo.
echo 📞 Soporte: info@opennexus.cr
echo 🌐 Web: https://opennexus.cr
exit /b 0
