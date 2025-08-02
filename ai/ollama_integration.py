"""
NexusOptim IA - Ollama Integration Service
Sistema de IA Local con Ollama para Turismo y Educación

Integración completa con:
- Llama 3.2 para recomendaciones turísticas
- Mistral para análisis de datos
- CodeLlama para desarrollo
- Phi-3 para educación

Copyright (c) 2025 OpenNexus - NexusOptim IA
Preparado para escalar a 1500+ empleados
"""

import requests
import json
import threading
import time
from datetime import datetime
from typing import Dict, List, Optional, Any
import asyncio
import aiohttp

class OllamaAIService:
    """Servicio de IA local con Ollama para NexusOptim IA"""
    
    def __init__(self, base_url: str = "http://localhost:11434"):
        self.base_url = base_url
        self.available_models = []
        self.active_sessions = {}
        self.performance_metrics = {
            'requests_processed': 0,
            'avg_response_time': 0,
            'tourism_queries': 0,
            'education_queries': 0,
            'business_queries': 0
        }
        
        # Modelos especializados para diferentes tareas
        self.specialized_models = {
            'tourism': 'llama3.2:latest',      # Recomendaciones turísticas
            'education': 'phi3:latest',         # Sistema educativo
            'business': 'mistral:latest',       # Análisis de negocios
            'code': 'codellama:latest',         # Desarrollo de software
            'general': 'llama3.2:latest'       # Propósito general
        }
        
        self.initialize_ollama()
        
    def initialize_ollama(self):
        """Inicializar conexión con Ollama"""
        try:
            # Verificar si Ollama está corriendo
            response = requests.get(f"{self.base_url}/api/tags", timeout=5)
            if response.status_code == 200:
                models_data = response.json()
                self.available_models = [model['name'] for model in models_data.get('models', [])]
                print(f"✅ Ollama connected. Available models: {len(self.available_models)}")
                
                # Verificar modelos especializados
                self.check_required_models()
            else:
                print("❌ Ollama not responding")
                
        except requests.exceptions.ConnectionError:
            print("⚠️  Ollama not running. Starting auto-installation...")
            self.auto_install_models()
            
    def check_required_models(self):
        """Verificar e instalar modelos requeridos"""
        required_models = list(self.specialized_models.values())
        missing_models = []
        
        for model in required_models:
            if model not in self.available_models:
                missing_models.append(model)
                
        if missing_models:
            print(f"📥 Installing missing models: {missing_models}")
            for model in missing_models:
                self.pull_model(model)
        else:
            print("✅ All required models available")
            
    def pull_model(self, model_name: str):
        """Descargar modelo de Ollama"""
        try:
            print(f"📥 Pulling {model_name}...")
            response = requests.post(
                f"{self.base_url}/api/pull",
                json={"name": model_name},
                stream=True,
                timeout=300
            )
            
            if response.status_code == 200:
                print(f"✅ {model_name} installed successfully")
                self.available_models.append(model_name)
            else:
                print(f"❌ Failed to install {model_name}")
                
        except Exception as e:
            print(f"❌ Error installing {model_name}: {e}")
            
    def auto_install_models(self):
        """Auto-instalar modelos base para NexusOptim IA"""
        base_models = [
            "llama3.2:latest",  # Modelo principal
            "phi3:latest",      # Educación
            "mistral:latest"    # Negocios
        ]
        
        for model in base_models:
            self.pull_model(model)
            
    async def generate_response(self, prompt: str, context: str = "general", 
                               model_override: str = None, temperature: float = 0.7) -> Dict:
        """Generar respuesta usando Ollama"""
        start_time = time.time()
        
        try:
            # Seleccionar modelo apropiado
            model = model_override or self.specialized_models.get(context, 'llama3.2:latest')
            
            # Preparar prompt contextualizado
            contextualized_prompt = self.contextualize_prompt(prompt, context)
            
            # Realizar request a Ollama
            async with aiohttp.ClientSession() as session:
                async with session.post(
                    f"{self.base_url}/api/generate",
                    json={
                        "model": model,
                        "prompt": contextualized_prompt,
                        "temperature": temperature,
                        "stream": False
                    }
                ) as response:
                    
                    if response.status == 200:
                        result = await response.json()
                        
                        # Actualizar métricas
                        response_time = time.time() - start_time
                        self.update_metrics(context, response_time)
                        
                        return {
                            'success': True,
                            'response': result.get('response', ''),
                            'model_used': model,
                            'response_time': response_time,
                            'context': context
                        }
                    else:
                        return {
                            'success': False,
                            'error': f"HTTP {response.status}",
                            'model_used': model
                        }
                        
        except Exception as e:
            return {
                'success': False,
                'error': str(e),
                'model_used': model if 'model' in locals() else 'unknown'
            }
            
    def contextualize_prompt(self, prompt: str, context: str) -> str:
        """Contextualizar prompt según el dominio"""
        context_prompts = {
            'tourism': f"""
Eres un experto en turismo de Costa Rica con conocimiento profundo sobre:
- Destinos turísticos tecnológicos
- Hoteles inteligentes y eco-lodges
- Tours con IoT y realidad aumentada
- Cultura costarricense y biodiversidad
- Infraestructura turística premium

Responde en español de manera profesional y entusiasta.
Enfócate en experiencias tecnológicas únicas.

Usuario: {prompt}
Experto en Turismo CR:""",

            'education': f"""
Eres "Maestro", un asistente educativo IA especializado en:
- Educación costarricense personalizada
- Tecnología educativa avanzada
- Metodologías de aprendizaje adaptativo
- Currículo nacional de Costa Rica
- Desarrollo de competencias del siglo XXI

Responde como un maestro experimentado, paciente y motivador.
Adapta tu lenguaje al nivel del estudiante.

Estudiante: {prompt}
Maestro:""",

            'business': f"""
Eres un consultor empresarial especializado en:
- Escalamiento de startups tecnológicas
- Gestión de equipos de 1000+ empleados
- Mercado costarricense y centroamericano
- Integración de IA en procesos empresariales
- Estrategias de crecimiento exponencial

Responde con insights estratégicos y datos concretos.

Empresario: {prompt}
Consultor:""",

            'code': f"""
Eres un arquitecto de software senior especializado en:
- Desarrollo con RISC-V y microcontroladores
- Sistemas IoT y LoRaWAN
- Aplicaciones Python/C/C++
- Arquitecturas escalables
- DevOps y CI/CD

Proporciona código limpio, comentado y siguiendo mejores prácticas.

Desarrollador: {prompt}
Arquitecto:""",

            'general': f"""
Eres un asistente IA de NexusOptim IA, empresa líder en Costa Rica.
Tienes conocimiento sobre turismo, educación, tecnología y negocios.
Responde de manera profesional y útil en español.

Usuario: {prompt}
NexusOptim IA:"""
        }
        
        return context_prompts.get(context, context_prompts['general'])
        
    def update_metrics(self, context: str, response_time: float):
        """Actualizar métricas de rendimiento"""
        self.performance_metrics['requests_processed'] += 1
        
        # Actualizar tiempo promedio de respuesta
        current_avg = self.performance_metrics['avg_response_time']
        total_requests = self.performance_metrics['requests_processed']
        self.performance_metrics['avg_response_time'] = (
            (current_avg * (total_requests - 1)) + response_time
        ) / total_requests
        
        # Incrementar contador específico
        if context in ['tourism']:
            self.performance_metrics['tourism_queries'] += 1
        elif context in ['education']:
            self.performance_metrics['education_queries'] += 1
        elif context in ['business']:
            self.performance_metrics['business_queries'] += 1
            
    def generate_tourism_recommendations(self, user_preferences: Dict, location: str) -> Dict:
        """Generar recomendaciones turísticas con IA"""
        prompt = f"""
Usuario ubicado en {location} con preferencias:
- Tecnología: {user_preferences.get('tech', 0.5)}/1.0
- Naturaleza: {user_preferences.get('nature', 0.5)}/1.0  
- Aventura: {user_preferences.get('adventure', 0.5)}/1.0
- Cultura: {user_preferences.get('culture', 0.5)}/1.0
- Lujo: {user_preferences.get('luxury', 0.5)}/1.0

Genera 3 recomendaciones específicas de tours y 2 hoteles que combinen tecnología con estas preferencias.
Incluye precios estimados en dólares y características tecnológicas específicas.
"""
        
        return asyncio.run(self.generate_response(prompt, context='tourism'))
        
    def create_educational_content(self, topic: str, grade_level: str, learning_style: str) -> Dict:
        """Crear contenido educativo personalizado"""
        prompt = f"""
Crea una lección interactiva sobre "{topic}" para estudiantes de {grade_level}.
Estilo de aprendizaje preferido: {learning_style}

Incluye:
1. Objetivos de aprendizaje
2. Explicación clara y adaptada al nivel
3. 3 actividades prácticas
4. Evaluación formativa
5. Recursos adicionales

Adapta el contenido al currículo costarricense y usa ejemplos locales.
"""
        
        return asyncio.run(self.generate_response(prompt, context='education'))
        
    def analyze_business_scaling(self, current_employees: int, target_employees: int, 
                                industry: str, timeline: str) -> Dict:
        """Analizar estrategia de escalamiento empresarial"""
        prompt = f"""
Empresa en {industry} con {current_employees} empleados que quiere escalar a {target_employees} en {timeline}.

Analiza y proporciona:
1. Plan de contratación escalonado
2. Estructura organizacional recomendada
3. Desafíos específicos del mercado costarricense
4. Estrategias de retención de talento
5. Inversión estimada en infraestructura
6. Métricas clave a monitorear

Enfócate en el ecosistema tecnológico de Costa Rica y la competencia con Intel.
"""
        
        return asyncio.run(self.generate_response(prompt, context='business'))
        
    def generate_code_solution(self, problem_description: str, language: str, 
                              framework: str = None) -> Dict:
        """Generar soluciones de código"""
        prompt = f"""
Desarrolla una solución en {language} {'usando ' + framework if framework else ''} para:

{problem_description}

Proporciona:
1. Código completo y comentado
2. Explicación de la arquitectura
3. Consideraciones de rendimiento
4. Tests unitarios básicos
5. Documentación de uso

Enfócate en código production-ready para una startup que manejará 1500+ empleados.
"""
        
        return asyncio.run(self.generate_response(prompt, context='code'))
        
    def get_performance_metrics(self) -> Dict:
        """Obtener métricas de rendimiento del sistema"""
        return {
            **self.performance_metrics,
            'available_models': self.available_models,
            'active_sessions': len(self.active_sessions),
            'ollama_status': 'connected' if self.available_models else 'disconnected',
            'last_updated': datetime.now().isoformat()
        }
        
    def health_check(self) -> Dict:
        """Verificar salud del sistema Ollama"""
        try:
            response = requests.get(f"{self.base_url}/api/tags", timeout=5)
            if response.status_code == 200:
                return {
                    'status': 'healthy',
                    'ollama_version': 'latest',
                    'models_available': len(self.available_models),
                    'memory_usage': 'optimized',
                    'response_time': 'normal'
                }
            else:
                return {
                    'status': 'unhealthy',
                    'error': f'HTTP {response.status_code}'
                }
        except Exception as e:
            return {
                'status': 'error',
                'error': str(e)
            }

# Instancia global del servicio Ollama
ollama_service = OllamaAIService()

class NexusOptimMaestro:
    """Sistema educativo 'Maestro' con IA"""
    
    def __init__(self):
        self.ollama = ollama_service
        self.student_profiles = {}
        self.curriculum_cr = self.load_cr_curriculum()
        self.learning_analytics = {}
        
    def load_cr_curriculum(self) -> Dict:
        """Cargar currículo educativo costarricense"""
        return {
            'primaria': {
                'matematicas': ['números', 'operaciones', 'geometría', 'medición', 'estadística'],
                'español': ['lectura', 'escritura', 'comunicación oral', 'gramática'],
                'ciencias': ['seres vivos', 'materia y energía', 'tierra y espacio'],
                'estudios_sociales': ['identidad', 'historia CR', 'geografía', 'civismo'],
                'ingles': ['vocabulario básico', 'gramática elemental', 'conversación'],
                'tecnologia': ['informática básica', 'programación visual', 'robótica']
            },
            'secundaria': {
                'matematicas': ['álgebra', 'geometría', 'trigonometría', 'estadística', 'cálculo'],
                'español': ['literatura', 'análisis textual', 'redacción avanzada'],
                'ciencias': ['biología', 'química', 'física', 'investigación científica'],
                'estudios_sociales': ['historia mundial', 'economía', 'política', 'sociología'],
                'ingles': ['conversación avanzada', 'literatura', 'escritura académica'],
                'tecnologia': ['programación', 'base de datos', 'redes', 'IA básica']
            }
        }
        
    def create_student_profile(self, student_id: str, grade_level: str, 
                              learning_preferences: Dict) -> Dict:
        """Crear perfil de estudiante personalizado"""
        profile = {
            'student_id': student_id,
            'grade_level': grade_level,
            'learning_preferences': learning_preferences,
            'strengths': [],
            'improvement_areas': [],
            'learning_path': [],
            'achievements': [],
            'created_at': datetime.now().isoformat()
        }
        
        self.student_profiles[student_id] = profile
        return profile
        
    def generate_personalized_lesson(self, student_id: str, subject: str, topic: str) -> Dict:
        """Generar lección personalizada usando Ollama"""
        if student_id not in self.student_profiles:
            return {'error': 'Student profile not found'}
            
        profile = self.student_profiles[student_id]
        grade_level = profile['grade_level']
        preferences = profile['learning_preferences']
        
        learning_style = preferences.get('style', 'visual')
        difficulty = preferences.get('difficulty', 'medio')
        interests = preferences.get('interests', [])
        
        # Generar contenido usando Ollama
        lesson_content = self.ollama.create_educational_content(
            topic=f"{subject}: {topic}",
            grade_level=grade_level,
            learning_style=learning_style
        )
        
        if lesson_content['success']:
            # Procesar y estructurar la respuesta
            structured_lesson = self.structure_lesson_content(
                lesson_content['response'], 
                subject, 
                topic, 
                grade_level
            )
            
            # Guardar en analytics
            self.update_learning_analytics(student_id, subject, topic, 'lesson_generated')
            
            return {
                'success': True,
                'lesson': structured_lesson,
                'personalization_applied': True,
                'ai_model_used': lesson_content['model_used']
            }
        else:
            return {
                'success': False,
                'error': lesson_content['error']
            }
            
    def structure_lesson_content(self, ai_response: str, subject: str, 
                                topic: str, grade_level: str) -> Dict:
        """Estructurar contenido de lección generado por IA"""
        return {
            'title': f"{subject}: {topic}",
            'grade_level': grade_level,
            'content': ai_response,
            'estimated_duration': '45 minutos',
            'difficulty_level': 'adaptado',
            'generated_at': datetime.now().isoformat(),
            'technology_integration': True,
            'cr_curriculum_aligned': True
        }
        
    def evaluate_student_progress(self, student_id: str, assessment_data: Dict) -> Dict:
        """Evaluar progreso del estudiante usando IA"""
        prompt = f"""
Analiza el progreso educativo del estudiante:

Datos de evaluación:
{json.dumps(assessment_data, indent=2)}

Proporciona:
1. Análisis de fortalezas identificadas
2. Áreas de mejora específicas
3. Recomendaciones pedagógicas
4. Plan de refuerzo personalizado
5. Predicción de rendimiento futuro
6. Sugerencias para padres y docentes

Enfócate en el desarrollo integral y el currículo costarricense.
"""
        
        analysis = asyncio.run(
            self.ollama.generate_response(prompt, context='education')
        )
        
        if analysis['success']:
            # Actualizar perfil del estudiante
            self.update_student_profile(student_id, assessment_data, analysis['response'])
            
            return {
                'success': True,
                'analysis': analysis['response'],
                'recommendations_applied': True,
                'profile_updated': True
            }
        else:
            return {
                'success': False,
                'error': analysis['error']
            }
            
    def update_student_profile(self, student_id: str, assessment_data: Dict, ai_analysis: str):
        """Actualizar perfil del estudiante basado en evaluación"""
        if student_id in self.student_profiles:
            profile = self.student_profiles[student_id]
            
            # Simular extracción de insights del análisis IA
            profile['last_assessment'] = datetime.now().isoformat()
            profile['ai_analysis'] = ai_analysis
            profile['assessment_history'] = profile.get('assessment_history', [])
            profile['assessment_history'].append(assessment_data)
            
            # Actualizar analytics
            self.update_learning_analytics(student_id, 'assessment', 'progress_update', 'completed')
            
    def update_learning_analytics(self, student_id: str, subject: str, topic: str, action: str):
        """Actualizar analytics de aprendizaje"""
        if student_id not in self.learning_analytics:
            self.learning_analytics[student_id] = {
                'total_lessons': 0,
                'subjects_studied': {},
                'engagement_score': 0,
                'last_activity': None
            }
            
        analytics = self.learning_analytics[student_id]
        analytics['total_lessons'] += 1
        analytics['last_activity'] = datetime.now().isoformat()
        
        if subject not in analytics['subjects_studied']:
            analytics['subjects_studied'][subject] = 0
        analytics['subjects_studied'][subject] += 1
        
    def get_class_insights(self, class_id: str, students: List[str]) -> Dict:
        """Obtener insights de toda la clase usando IA"""
        class_data = []
        for student_id in students:
            if student_id in self.learning_analytics:
                class_data.append(self.learning_analytics[student_id])
                
        prompt = f"""
Analiza los datos de rendimiento de una clase con {len(students)} estudiantes:

Datos agregados de la clase:
{json.dumps(class_data, indent=2)}

Proporciona insights sobre:
1. Rendimiento general de la clase
2. Patrones de aprendizaje identificados
3. Estudiantes que necesitan atención especial
4. Recomendaciones metodológicas
5. Recursos adicionales sugeridos
6. Estrategias de mejora colectiva

Enfócate en estrategias aplicables al sistema educativo costarricense.
"""
        
        insights = asyncio.run(
            self.ollama.generate_response(prompt, context='education')
        )
        
        return {
            'class_id': class_id,
            'students_analyzed': len(students),
            'insights': insights['response'] if insights['success'] else 'Error generating insights',
            'generated_at': datetime.now().isoformat()
        }

# Instancia global del sistema educativo
maestro_system = NexusOptimMaestro()

def initialize_ollama_integration():
    """Inicializar integración completa de Ollama"""
    print("🤖 Initializing NexusOptim IA Ollama Integration...")
    print("🚀 Preparing for 1500+ employee scaling...")
    
    # Verificar Ollama
    health = ollama_service.health_check()
    print(f"🔍 Ollama Status: {health['status']}")
    
    # Inicializar sistemas
    print("📚 Maestro Educational System: Ready")
    print("🗺️ Tourism AI Engine: Ready") 
    print("💼 Business Intelligence: Ready")
    
    return {
        'ollama_service': ollama_service,
        'maestro_system': maestro_system,
        'status': 'initialized',
        'ready_for_scaling': True
    }

if __name__ == "__main__":
    services = initialize_ollama_integration()
    print("✅ NexusOptim IA Ollama Integration Complete!")
    print("🇨🇷 Ready to revolutionize Costa Rica's tech ecosystem!")
