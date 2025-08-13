@echo off
REM NexusOptim IA - Windows Setup Script
REM Script de configuracion rapida para Windows

echo ========================================
echo 🚀 NexusOptim IA - Setup Windows
echo    Edge AI para Optimizacion Electrica
echo ========================================

REM Verificar Python
echo 🐍 Verificando Python...
python --version >nul 2>&1
if %errorlevel% neq 0 (
    echo ❌ Python no encontrado
    echo    Descarga desde: https://python.org/downloads
    echo    IMPORTANTE: Marcar "Add Python to PATH" durante instalacion
    pause
    exit /b 1
) else (
    echo ✅ Python encontrado
    python --version
)

REM Crear entorno virtual
echo.
echo 📦 Creando entorno virtual...
if exist "nexusoptim_env" (
    echo ✅ Entorno virtual ya existe
) else (
    python -m venv nexusoptim_env
    echo ✅ Entorno virtual creado
)

REM Activar entorno virtual e instalar dependencias
echo.
echo 📚 Instalando dependencias...
call nexusoptim_env\Scripts\activate
python -m pip install --upgrade pip
pip install -r requirements.txt

if %errorlevel% neq 0 (
    echo ❌ Error instalando dependencias
    echo    Verifica que requirements.txt existe
    pause
    exit /b 1
) else (
    echo ✅ Dependencias instaladas correctamente
)

REM Crear directorios
echo.
echo 📁 Creando estructura de directorios...
mkdir data 2>nul
mkdir models 2>nul
mkdir logs 2>nul
mkdir config 2>nul
mkdir tests 2>nul
mkdir sql 2>nul
mkdir scripts 2>nul
echo ✅ Directorios creados

REM Verificar Docker (opcional)
echo.
echo 🐳 Verificando Docker (opcional)...
docker --version >nul 2>&1
if %errorlevel% neq 0 (
    echo ⚠️  Docker no encontrado (opcional)
    echo    Descarga desde: https://docker.com/get-started
) else (
    echo ✅ Docker encontrado
    docker --version
    docker-compose --version
)

echo.
echo ========================================
echo ✅ SETUP COMPLETADO EXITOSAMENTE
echo ========================================
echo.
echo 🚀 PARA EMPEZAR:
echo 1. Activar entorno: nexusoptim_env\Scripts\activate
echo 2. Ejecutar app: python src\main.py
echo 3. Abrir: http://localhost:8000
echo 4. Docs API: http://localhost:8000/docs
echo.
echo 🐳 CON DOCKER:
echo   docker-compose up -d
echo.
echo 🎉 ¡NexusOptim IA listo para Costa Rica!
echo ========================================

pause
