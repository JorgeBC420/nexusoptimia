#!/usr/bin/env python3
"""
NexusOptim IA - Setup Script
Script automatizado para configurar el entorno de desarrollo completo
"""

import os
import sys
import subprocess
import platform
from pathlib import Path

def run_command(command, description=""):
    """Ejecutar comando y manejar errores"""
    print(f"🔧 {description}")
    print(f"   Ejecutando: {command}")
    
    try:
        result = subprocess.run(
            command, 
            shell=True, 
            check=True, 
            capture_output=True, 
            text=True
        )
        print(f"✅ {description} - Completado")
        return result.stdout
    except subprocess.CalledProcessError as e:
        print(f"❌ Error en: {description}")
        print(f"   Comando: {command}")
        print(f"   Error: {e.stderr}")
        return None

def check_python():
    """Verificar instalación de Python"""
    print("🐍 Verificando Python...")
    
    try:
        version = sys.version_info
        if version.major < 3 or (version.major == 3 and version.minor < 8):
            print("❌ Necesitas Python 3.8 o superior")
            print("   Descarga desde: https://python.org/downloads")
            return False
        
        print(f"✅ Python {version.major}.{version.minor}.{version.micro} detectado")
        return True
    except:
        print("❌ Python no encontrado")
        return False

def check_docker():
    """Verificar instalación de Docker"""
    print("🐳 Verificando Docker...")
    
    docker_version = run_command("docker --version", "Verificar Docker")
    if docker_version:
        print(f"✅ {docker_version.strip()}")
        
        # Verificar Docker Compose
        compose_version = run_command("docker-compose --version", "Verificar Docker Compose")
        if compose_version:
            print(f"✅ {compose_version.strip()}")
            return True
        else:
            print("❌ Docker Compose no encontrado")
            return False
    else:
        print("❌ Docker no encontrado")
        print("   Descarga desde: https://docker.com/get-started")
        return False

def setup_virtual_environment():
    """Configurar entorno virtual Python"""
    venv_path = Path("nexusoptim_env")
    
    if venv_path.exists():
        print("📦 Entorno virtual ya existe")
        return True
    
    print("📦 Creando entorno virtual...")
    
    # Crear entorno virtual
    if platform.system() == "Windows":
        create_cmd = "python -m venv nexusoptim_env"
        activate_cmd = "nexusoptim_env\\Scripts\\activate"
        pip_cmd = "nexusoptim_env\\Scripts\\pip"
    else:
        create_cmd = "python3 -m venv nexusoptim_env"
        activate_cmd = "source nexusoptim_env/bin/activate"
        pip_cmd = "nexusoptim_env/bin/pip"
    
    if run_command(create_cmd, "Crear entorno virtual"):
        print(f"✅ Entorno virtual creado")
        print(f"   Para activar: {activate_cmd}")
        
        # Actualizar pip
        run_command(f"{pip_cmd} install --upgrade pip", "Actualizar pip")
        
        return True
    else:
        return False

def install_python_dependencies():
    """Instalar dependencias Python"""
    print("📚 Instalando dependencias Python...")
    
    if platform.system() == "Windows":
        pip_cmd = "nexusoptim_env\\Scripts\\pip"
    else:
        pip_cmd = "nexusoptim_env/bin/pip"
    
    # Instalar requirements
    if Path("requirements.txt").exists():
        success = run_command(
            f"{pip_cmd} install -r requirements.txt", 
            "Instalar dependencias desde requirements.txt"
        )
        if success:
            print("✅ Todas las dependencias instaladas")
            return True
        else:
            print("❌ Error instalando dependencias")
            return False
    else:
        print("❌ Archivo requirements.txt no encontrado")
        return False

def create_directories():
    """Crear estructura de directorios"""
    print("📁 Creando estructura de directorios...")
    
    directories = [
        "data",
        "models", 
        "logs",
        "config",
        "tests",
        "sql",
        "scripts"
    ]
    
    for directory in directories:
        Path(directory).mkdir(exist_ok=True)
        print(f"   📁 {directory}/")
    
    print("✅ Estructura de directorios creada")

def setup_git():
    """Configurar Git para el proyecto"""
    print("🔧 Configurando Git...")
    
    if not Path(".git").exists():
        run_command("git init", "Inicializar repositorio Git")
    
    # Crear .gitignore si no existe
    gitignore_content = """
# Python
__pycache__/
*.py[cod]
*$py.class
*.so
.Python
build/
develop-eggs/
dist/
downloads/
eggs/
.eggs/
lib/
lib64/
parts/
sdist/
var/
wheels/
*.egg-info/
.installed.cfg
*.egg

# Virtual Environment
nexusoptim_env/
venv/
ENV/

# Environment Variables
.env
.env.local
.env.production

# IDE
.vscode/
.idea/
*.swp
*.swo

# Logs
logs/
*.log

# Data
data/
*.csv
*.pkl
*.h5

# Models
models/*.tflite
models/*.onnx
models/*.pkl

# Docker
.dockerignore

# OS
.DS_Store
Thumbs.db

# NexusOptim Specific
config/secrets.yml
ssl/
certificates/
"""
    
    with open(".gitignore", "w") as f:
        f.write(gitignore_content.strip())
    
    print("✅ Git configurado")

def main():
    """Función principal del setup"""
    print("="*60)
    print("🚀 NexusOptim IA - Setup Automatizado")
    print("   Edge AI para Optimización Eléctrica")
    print("   Desarrollado por: OpenNexus")
    print("="*60)
    
    # Verificaciones previas
    if not check_python():
        print("\n❌ Setup cancelado - Instala Python primero")
        sys.exit(1)
    
    # Setup paso a paso
    steps = [
        ("Crear directorios", create_directories),
        ("Configurar entorno virtual", setup_virtual_environment),
        ("Instalar dependencias", install_python_dependencies),
        ("Configurar Git", setup_git),
    ]
    
    print(f"\n📋 Ejecutando {len(steps)} pasos...")
    
    for i, (description, function) in enumerate(steps, 1):
        print(f"\n[{i}/{len(steps)}] {description}")
        try:
            if not function():
                print(f"❌ Fallo en paso: {description}")
                sys.exit(1)
        except Exception as e:
            print(f"❌ Error en {description}: {e}")
            sys.exit(1)
    
    # Verificación opcional de Docker
    print(f"\n[Opcional] Verificando Docker...")
    docker_ok = check_docker()
    
    # Resumen final
    print("\n" + "="*60)
    print("✅ SETUP COMPLETADO EXITOSAMENTE")
    print("="*60)
    print("📦 Entorno virtual: nexusoptim_env/")
    print("📚 Dependencias instaladas desde requirements.txt")
    print("📁 Estructura de directorios creada")
    print("🔧 Git configurado con .gitignore")
    
    if docker_ok:
        print("🐳 Docker listo para usar")
    else:
        print("⚠️  Docker no disponible (opcional)")
    
    print("\n🚀 PRÓXIMOS PASOS:")
    
    if platform.system() == "Windows":
        print("1. Activar entorno: nexusoptim_env\\Scripts\\activate")
    else:
        print("1. Activar entorno: source nexusoptim_env/bin/activate")
    
    print("2. Ejecutar aplicación: python src/main.py")
    print("3. Abrir navegador: http://localhost:8000")
    print("4. Ver documentación: http://localhost:8000/docs")
    
    if docker_ok:
        print("5. Usar Docker: docker-compose up -d")
    
    print("\n🎉 ¡NexusOptim IA listo para desarrollar!")
    print("="*60)

if __name__ == "__main__":
    main()
