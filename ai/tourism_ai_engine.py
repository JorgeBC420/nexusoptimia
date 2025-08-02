"""
Tourism IA Engine - Backend para recomendaciones inteligentes
Motor de inteligencia artificial para turismo tecnológico

Sistema de recomendaciones basado en:
- Machine Learning para preferencias
- Geolocalización inteligente
- Análisis de patrones de comportamiento
- Optimización de ranking por pagos premium

Copyright (c) 2025 OpenNexus - NexusOptim IA
"""

import json
import math
import random
from datetime import datetime, timedelta
from typing import Dict, List, Tuple, Optional
import threading
import time

class TourismAIEngine:
    """Motor de IA para recomendaciones turísticas inteligentes"""
    
    def __init__(self):
        self.user_profiles = {}
        self.interaction_history = []
        self.location_data = {}
        self.weather_data = {}
        self.business_premiums = {}
        self.ml_weights = self.initialize_ml_weights()
        
    def initialize_ml_weights(self) -> Dict:
        """Inicializar pesos del modelo de machine learning"""
        return {
            'preference_weight': 0.35,
            'distance_weight': 0.25,
            'rating_weight': 0.15,
            'premium_weight': 0.10,
            'weather_weight': 0.05,
            'time_weight': 0.05,
            'social_weight': 0.05
        }
        
    def create_user_profile(self, user_id: str, preferences: Dict, location: Tuple[float, float]) -> Dict:
        """Crear perfil de usuario con análisis inicial"""
        profile = {
            'user_id': user_id,
            'preferences': preferences,
            'location': location,
            'created_at': datetime.now().isoformat(),
            'interaction_count': 0,
            'booking_history': [],
            'search_patterns': {},
            'ml_score_adjustments': {},
            'predicted_interests': self.predict_interests(preferences)
        }
        
        self.user_profiles[user_id] = profile
        return profile
        
    def predict_interests(self, preferences: Dict) -> Dict:
        """Predicción de intereses usando ML básico"""
        predictions = {}
        
        # Análisis de correlaciones entre preferencias
        if preferences.get('tech', 0) > 0.7 and preferences.get('nature', 0) > 0.6:
            predictions['eco_tech'] = 0.85
            predictions['smart_conservation'] = 0.9
            
        if preferences.get('adventure', 0) > 0.8:
            predictions['extreme_sports'] = 0.8
            predictions['volcano_tours'] = 0.9
            
        if preferences.get('culture', 0) > 0.7 and preferences.get('tech', 0) > 0.5:
            predictions['digital_heritage'] = 0.8
            predictions['ar_museums'] = 0.7
            
        if preferences.get('luxury', 0) > 0.6:
            predictions['premium_experiences'] = 0.9
            predictions['exclusive_access'] = 0.8
            
        return predictions
        
    def calculate_recommendation_score(self, user_id: str, item: Dict, item_type: str) -> float:
        """Calcular puntuación de recomendación usando ML"""
        if user_id not in self.user_profiles:
            return 0.0
            
        user_profile = self.user_profiles[user_id]
        user_prefs = user_profile['preferences']
        user_location = user_profile['location']
        
        total_score = 0.0
        
        # 1. Preference matching score
        pref_score = 0.0
        for category in item.get('category', []):
            if category in user_prefs:
                pref_score += user_prefs[category] * 100
                
        # Aplicar predicciones de ML
        for predicted_interest, confidence in user_profile['predicted_interests'].items():
            if self.item_matches_prediction(item, predicted_interest):
                pref_score += confidence * 50
                
        total_score += pref_score * self.ml_weights['preference_weight']
        
        # 2. Distance score (más cerca = mejor)
        if 'location' in item:
            distance = self.calculate_distance(
                user_location[0], user_location[1],
                item['location']['lat'], item['location']['lng']
            )
            distance_score = max(0, 100 - distance * 3)  # 3 km penalty per km
            total_score += distance_score * self.ml_weights['distance_weight']
            
        # 3. Rating score
        rating_score = item.get('rating', 0) * 20  # Convert 5-star to 100 scale
        total_score += rating_score * self.ml_weights['rating_weight']
        
        # 4. Premium boost (business paid for visibility)
        if item.get('premium', False):
            premium_boost = self.get_premium_boost(item['id'], item_type)
            total_score += premium_boost * self.ml_weights['premium_weight']
            
        # 5. Weather compatibility
        weather_score = self.calculate_weather_compatibility(item, user_location)
        total_score += weather_score * self.ml_weights['weather_weight']
        
        # 6. Time compatibility
        time_score = self.calculate_time_compatibility(item)
        total_score += time_score * self.ml_weights['time_weight']
        
        # 7. Social proof (other similar users liked this)
        social_score = self.calculate_social_proof(user_id, item)
        total_score += social_score * self.ml_weights['social_weight']
        
        # Aplicar ajustes personalizados de ML
        if item['id'] in user_profile.get('ml_score_adjustments', {}):
            total_score *= user_profile['ml_score_adjustments'][item['id']]
            
        return max(0, total_score)
        
    def item_matches_prediction(self, item: Dict, predicted_interest: str) -> bool:
        """Verificar si un item coincide con una predicción de interés"""
        matches = {
            'eco_tech': lambda i: 'tech' in i.get('category', []) and 'nature' in i.get('category', []),
            'smart_conservation': lambda i: any('sensor' in f.lower() or 'monitor' in f.lower() for f in i.get('tech_features', [])),
            'extreme_sports': lambda i: 'adventure' in i.get('category', []) and any('extreme' in f.lower() for f in i.get('tech_features', [])),
            'volcano_tours': lambda i: 'volc' in i.get('name', '').lower() or 'volc' in i.get('description', '').lower(),
            'digital_heritage': lambda i: 'culture' in i.get('category', []) and 'tech' in i.get('category', []),
            'ar_museums': lambda i: any('ar' in f.lower() or 'realidad' in f.lower() for f in i.get('tech_features', [])),
            'premium_experiences': lambda i: i.get('premium', False),
            'exclusive_access': lambda i: 'exclusive' in i.get('description', '').lower()
        }
        
        return matches.get(predicted_interest, lambda x: False)(item)
        
    def calculate_distance(self, lat1: float, lng1: float, lat2: float, lng2: float) -> float:
        """Calcular distancia haversine entre dos puntos"""
        R = 6371  # Radio de la Tierra en km
        
        lat1_rad = math.radians(lat1)
        lat2_rad = math.radians(lat2)
        delta_lat = math.radians(lat2 - lat1)
        delta_lng = math.radians(lng2 - lng1)
        
        a = (math.sin(delta_lat/2) * math.sin(delta_lat/2) +
             math.cos(lat1_rad) * math.cos(lat2_rad) *
             math.sin(delta_lng/2) * math.sin(delta_lng/2))
        
        c = 2 * math.atan2(math.sqrt(a), math.sqrt(1-a))
        return R * c
        
    def get_premium_boost(self, item_id: int, item_type: str) -> float:
        """Obtener boost de visibilidad premium"""
        premium_key = f"{item_type}_{item_id}"
        
        if premium_key not in self.business_premiums:
            return 0.0
            
        premium_data = self.business_premiums[premium_key]
        
        # Diferentes tiers de premium
        tier_boosts = {
            'bronze': 20,
            'silver': 50,
            'gold': 100,
            'platinum': 150
        }
        
        base_boost = tier_boosts.get(premium_data.get('tier', 'bronze'), 20)
        
        # Factor de tiempo (premium reciente es más efectivo)
        days_since_payment = (datetime.now() - datetime.fromisoformat(premium_data['paid_at'])).days
        time_factor = max(0.5, 1.0 - (days_since_payment / 30))  # Decae en 30 días
        
        return base_boost * time_factor
        
    def calculate_weather_compatibility(self, item: Dict, user_location: Tuple[float, float]) -> float:
        """Calcular compatibilidad con el clima"""
        # Simular datos meteorológicos
        weather_score = 50  # Base score
        
        current_weather = self.get_simulated_weather(user_location)
        
        # Actividades que dependen del clima
        if 'nature' in item.get('category', []):
            if current_weather['condition'] == 'sunny':
                weather_score += 30
            elif current_weather['condition'] == 'rainy':
                weather_score -= 20
                
        if 'adventure' in item.get('category', []):
            if current_weather['condition'] == 'sunny' and current_weather['temperature'] > 20:
                weather_score += 25
                
        # Actividades cubiertas no se ven afectadas tanto
        if any('indoor' in f.lower() or 'museo' in f.lower() for f in item.get('tech_features', [])):
            weather_score = max(weather_score, 70)  # Mínimo para actividades cubiertas
            
        return max(0, min(100, weather_score))
        
    def get_simulated_weather(self, location: Tuple[float, float]) -> Dict:
        """Simular datos meteorológicos para Costa Rica"""
        conditions = ['sunny', 'partly_cloudy', 'rainy', 'cloudy']
        return {
            'condition': random.choice(conditions),
            'temperature': random.randint(18, 32),  # Rango típico Costa Rica
            'humidity': random.randint(60, 90),
            'wind_speed': random.randint(5, 25)
        }
        
    def calculate_time_compatibility(self, item: Dict) -> float:
        """Calcular compatibilidad temporal"""
        current_hour = datetime.now().hour
        current_day = datetime.now().weekday()
        
        score = 50  # Base score
        
        # Horarios óptimos para diferentes actividades
        if 'adventure' in item.get('category', []):
            if 6 <= current_hour <= 10 or 15 <= current_hour <= 18:  # Mejores horas para aventura
                score += 25
                
        if 'culture' in item.get('category', []):
            if 9 <= current_hour <= 17:  # Horario típico de museos
                score += 20
                
        # Fin de semana vs días laborales
        if current_day >= 5:  # Weekend
            if 'adventure' in item.get('category', []) or 'nature' in item.get('category', []):
                score += 15
        else:
            if 'tech' in item.get('category', []):  # Tech tours mejor en días laborales
                score += 10
                
        return max(0, min(100, score))
        
    def calculate_social_proof(self, user_id: str, item: Dict) -> float:
        """Calcular prueba social basada en usuarios similares"""
        user_profile = self.user_profiles.get(user_id, {})
        user_prefs = user_profile.get('preferences', {})
        
        # Simular usuarios similares que han interactuado con este item
        similar_users_count = 0
        total_similar_users = 0
        
        for other_user_id, other_profile in self.user_profiles.items():
            if other_user_id == user_id:
                continue
                
            # Calcular similitud de preferencias
            similarity = self.calculate_preference_similarity(user_prefs, other_profile.get('preferences', {}))
            
            if similarity > 0.6:  # Usuarios similares
                total_similar_users += 1
                
                # Verificar si han interactuado positivamente con este item
                for interaction in other_profile.get('booking_history', []):
                    if interaction.get('item_id') == item['id'] and interaction.get('rating', 0) >= 4:
                        similar_users_count += 1
                        break
                        
        if total_similar_users == 0:
            return 50  # Score neutral si no hay datos
            
        social_ratio = similar_users_count / total_similar_users
        return social_ratio * 100
        
    def calculate_preference_similarity(self, prefs1: Dict, prefs2: Dict) -> float:
        """Calcular similitud entre dos conjuntos de preferencias"""
        if not prefs1 or not prefs2:
            return 0.0
            
        common_prefs = set(prefs1.keys()) & set(prefs2.keys())
        if not common_prefs:
            return 0.0
            
        total_diff = 0.0
        for pref in common_prefs:
            total_diff += abs(prefs1[pref] - prefs2[pref])
            
        # Convertir diferencia a similitud (0-1)
        avg_diff = total_diff / len(common_prefs)
        similarity = max(0, 1 - avg_diff)
        
        return similarity
        
    def update_user_interaction(self, user_id: str, item_id: int, interaction_type: str, rating: Optional[int] = None):
        """Actualizar interacción del usuario para ML"""
        if user_id not in self.user_profiles:
            return
            
        interaction = {
            'item_id': item_id,
            'interaction_type': interaction_type,  # 'view', 'book', 'rate', 'search'
            'rating': rating,
            'timestamp': datetime.now().isoformat()
        }
        
        self.interaction_history.append(interaction)
        self.user_profiles[user_id]['interaction_count'] += 1
        
        # Actualizar patrones de búsqueda
        if interaction_type == 'search':
            search_patterns = self.user_profiles[user_id].get('search_patterns', {})
            hour = datetime.now().hour
            day = datetime.now().weekday()
            
            search_patterns[f'hour_{hour}'] = search_patterns.get(f'hour_{hour}', 0) + 1
            search_patterns[f'day_{day}'] = search_patterns.get(f'day_{day}', 0) + 1
            
            self.user_profiles[user_id]['search_patterns'] = search_patterns
            
        # Actualizar historial de reservas
        if interaction_type == 'book':
            self.user_profiles[user_id]['booking_history'].append(interaction)
            
        # Ajustar pesos de ML basado en interacciones
        self.adjust_ml_weights(user_id, item_id, interaction_type, rating)
        
    def adjust_ml_weights(self, user_id: str, item_id: int, interaction_type: str, rating: Optional[int]):
        """Ajustar pesos de ML basado en feedback del usuario"""
        if user_id not in self.user_profiles:
            return
            
        adjustments = self.user_profiles[user_id].get('ml_score_adjustments', {})
        
        # Factores de ajuste basados en interacciones
        adjustment_factors = {
            'view': 1.01,      # Ligero aumento por ver
            'book': 1.15,      # Aumento moderado por reservar
            'rate_5': 1.25,    # Gran aumento por rating alto
            'rate_4': 1.15,
            'rate_3': 1.0,     # Neutral
            'rate_2': 0.85,    # Penalización por rating bajo
            'rate_1': 0.7
        }
        
        # Determinar factor de ajuste
        if interaction_type == 'rate' and rating:
            factor_key = f'rate_{rating}'
        else:
            factor_key = interaction_type
            
        factor = adjustment_factors.get(factor_key, 1.0)
        
        # Aplicar ajuste
        current_adjustment = adjustments.get(item_id, 1.0)
        new_adjustment = min(2.0, max(0.5, current_adjustment * factor))  # Limitar entre 0.5 y 2.0
        
        adjustments[item_id] = new_adjustment
        self.user_profiles[user_id]['ml_score_adjustments'] = adjustments
        
    def activate_premium_service(self, business_id: int, service_type: str, tier: str, duration_days: int = 30) -> Dict:
        """Activar servicio premium para un negocio"""
        premium_key = f"{service_type}_{business_id}"
        
        activation_data = {
            'business_id': business_id,
            'service_type': service_type,
            'tier': tier,
            'paid_at': datetime.now().isoformat(),
            'expires_at': (datetime.now() + timedelta(days=duration_days)).isoformat(),
            'status': 'active'
        }
        
        self.business_premiums[premium_key] = activation_data
        
        return {
            'success': True,
            'message': f'Premium {tier} activado para {service_type} ID {business_id}',
            'boost_percentage': self.get_premium_boost(business_id, service_type),
            'expires_at': activation_data['expires_at']
        }
        
    def generate_business_analytics(self, business_id: int, service_type: str) -> Dict:
        """Generar analytics detallados para un negocio"""
        premium_key = f"{service_type}_{business_id}"
        
        # Datos simulados de analytics
        base_views = random.randint(50, 200)
        base_bookings = random.randint(5, 25)
        
        # Boost si es premium
        if premium_key in self.business_premiums:
            premium_data = self.business_premiums[premium_key]
            boost_factor = 1.5 if premium_data.get('tier') == 'gold' else 1.2
            views = int(base_views * boost_factor)
            bookings = int(base_bookings * boost_factor)
        else:
            views = base_views
            bookings = base_bookings
            
        analytics = {
            'business_id': business_id,
            'service_type': service_type,
            'period': '30_days',
            'metrics': {
                'total_views': views,
                'total_bookings': bookings,
                'conversion_rate': round((bookings / views) * 100, 2),
                'revenue_estimated': bookings * random.randint(50, 200),
                'ai_recommendations': random.randint(10, 50),
                'search_ranking_avg': random.randint(1, 10),
                'user_rating_avg': round(random.uniform(4.0, 5.0), 1)
            },
            'premium_status': premium_key in self.business_premiums,
            'generated_at': datetime.now().isoformat()
        }
        
        return analytics
        
    def get_trending_destinations(self, user_location: Tuple[float, float], radius_km: int = 100) -> List[Dict]:
        """Obtener destinos trending basados en ML"""
        # Simular trending basado en interacciones recientes
        trending_data = []
        
        # Análisis de patrones de búsqueda recientes
        recent_interactions = [i for i in self.interaction_history 
                             if datetime.fromisoformat(i['timestamp']) > datetime.now() - timedelta(days=7)]
        
        # Contar interacciones por item
        item_counts = {}
        for interaction in recent_interactions:
            item_id = interaction['item_id']
            item_counts[item_id] = item_counts.get(item_id, 0) + 1
            
        # Crear trending list
        for item_id, count in sorted(item_counts.items(), key=lambda x: x[1], reverse=True)[:5]:
            trending_data.append({
                'item_id': item_id,
                'trend_score': count,
                'interaction_count': count,
                'trend_direction': 'up',  # Simplificado
                'category': 'hot'
            })
            
        return trending_data
        
    def export_user_insights(self, user_id: str) -> Dict:
        """Exportar insights detallados del usuario"""
        if user_id not in self.user_profiles:
            return {'error': 'Usuario no encontrado'}
            
        profile = self.user_profiles[user_id]
        
        insights = {
            'user_id': user_id,
            'profile_summary': {
                'created_at': profile['created_at'],
                'total_interactions': profile['interaction_count'],
                'booking_count': len(profile.get('booking_history', [])),
                'preferences': profile['preferences'],
                'predicted_interests': profile['predicted_interests']
            },
            'behavior_patterns': {
                'search_patterns': profile.get('search_patterns', {}),
                'preferred_times': self.analyze_preferred_times(user_id),
                'booking_seasonality': self.analyze_booking_seasonality(user_id)
            },
            'ml_adjustments': profile.get('ml_score_adjustments', {}),
            'recommendations_performance': self.analyze_recommendation_performance(user_id),
            'generated_at': datetime.now().isoformat()
        }
        
        return insights
        
    def analyze_preferred_times(self, user_id: str) -> Dict:
        """Analizar horarios preferidos del usuario"""
        user_interactions = [i for i in self.interaction_history 
                           if i.get('user_id') == user_id]
        
        hour_counts = {}
        day_counts = {}
        
        for interaction in user_interactions:
            timestamp = datetime.fromisoformat(interaction['timestamp'])
            hour = timestamp.hour
            day = timestamp.weekday()
            
            hour_counts[hour] = hour_counts.get(hour, 0) + 1
            day_counts[day] = day_counts.get(day, 0) + 1
            
        preferred_hour = max(hour_counts.items(), key=lambda x: x[1])[0] if hour_counts else 12
        preferred_day = max(day_counts.items(), key=lambda x: x[1])[0] if day_counts else 0
        
        day_names = ['Monday', 'Tuesday', 'Wednesday', 'Thursday', 'Friday', 'Saturday', 'Sunday']
        
        return {
            'preferred_hour': preferred_hour,
            'preferred_day': day_names[preferred_day],
            'hour_distribution': hour_counts,
            'day_distribution': day_counts
        }
        
    def analyze_booking_seasonality(self, user_id: str) -> Dict:
        """Analizar estacionalidad de reservas"""
        profile = self.user_profiles.get(user_id, {})
        bookings = profile.get('booking_history', [])
        
        if not bookings:
            return {'no_data': True}
            
        month_counts = {}
        for booking in bookings:
            timestamp = datetime.fromisoformat(booking['timestamp'])
            month = timestamp.month
            month_counts[month] = month_counts.get(month, 0) + 1
            
        return {
            'monthly_distribution': month_counts,
            'peak_month': max(month_counts.items(), key=lambda x: x[1])[0] if month_counts else 1,
            'total_bookings': len(bookings)
        }
        
    def analyze_recommendation_performance(self, user_id: str) -> Dict:
        """Analizar performance de recomendaciones para un usuario"""
        user_interactions = [i for i in self.interaction_history 
                           if i.get('user_id') == user_id]
        
        # Simular métricas de performance
        recommendations_shown = len(user_interactions) * 3  # Asumiendo 3 recomendaciones por interacción
        recommendations_clicked = len([i for i in user_interactions if i['interaction_type'] in ['view', 'book']])
        recommendations_booked = len([i for i in user_interactions if i['interaction_type'] == 'book'])
        
        ctr = (recommendations_clicked / recommendations_shown * 100) if recommendations_shown > 0 else 0
        conversion = (recommendations_booked / recommendations_clicked * 100) if recommendations_clicked > 0 else 0
        
        return {
            'recommendations_shown': recommendations_shown,
            'click_through_rate': round(ctr, 2),
            'conversion_rate': round(conversion, 2),
            'total_bookings_from_recommendations': recommendations_booked,
            'user_satisfaction_estimated': round(random.uniform(3.5, 5.0), 1)
        }

# Instancia global del motor de IA
tourism_ai_engine = TourismAIEngine()

def initialize_demo_data():
    """Inicializar datos de demostración"""
    # Crear algunos perfiles de usuario de prueba
    demo_users = [
        {
            'user_id': 'user_001',
            'preferences': {'tech': 0.8, 'nature': 0.9, 'adventure': 0.7, 'culture': 0.4, 'luxury': 0.3},
            'location': (9.748917, -83.753428)  # San José
        },
        {
            'user_id': 'user_002', 
            'preferences': {'tech': 0.5, 'nature': 0.6, 'adventure': 0.3, 'culture': 0.9, 'luxury': 0.8},
            'location': (10.463056, -84.703333)  # Arenal
        }
    ]
    
    for user_data in demo_users:
        tourism_ai_engine.create_user_profile(
            user_data['user_id'],
            user_data['preferences'], 
            user_data['location']
        )
        
    # Activar algunos servicios premium de demo
    tourism_ai_engine.activate_premium_service(1, 'tour', 'gold', 30)
    tourism_ai_engine.activate_premium_service(101, 'hotel', 'silver', 15)
    
    print("✅ Tourism AI Engine initialized with demo data")

if __name__ == "__main__":
    initialize_demo_data()
    print("🤖 Tourism AI Engine ready for integration")
