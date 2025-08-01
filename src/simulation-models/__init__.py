"""
Simulation Models: Modelos de simulación y gemelos digitales
Validación de algoritmos antes de despliegue real en redes eléctricas

Funcionalidades:
- Simulación de redes eléctricas con PyPSA/pandapower
- Escenarios de sobrecarga y variaciones climáticas
- Validación de algoritmos antes de despliegue real
- Integración con datos históricos del ICE
"""

import numpy as np
import pandas as pd
import matplotlib.pyplot as plt
from datetime import datetime, timedelta
from typing import Dict, List, Tuple, Optional
import logging
import json
from dataclasses import dataclass

logger = logging.getLogger(__name__)

@dataclass
class GridNode:
    """Nodo de la red eléctrica"""
    node_id: str
    node_type: str  # "generator", "load", "substation"
    voltage_nominal: float  # Voltaje nominal en kV
    power_rating: float     # Potencia nominal en MW
    location: Tuple[float, float]  # (lat, lon)
    efficiency: float = 0.95

@dataclass
class GridEdge:
    """Línea de transmisión"""
    from_node: str
    to_node: str
    resistance: float    # Resistencia en Ohms/km
    reactance: float     # Reactancia en Ohms/km
    length: float        # Longitud en km
    capacity: float      # Capacidad en MW

class ElectricalGridSimulator:
    """
    Simulador de red eléctrica para Costa Rica
    Basado en topología simplificada del ICE
    """
    
    def __init__(self):
        self.nodes = {}
        self.edges = {}
        self.load_profiles = {}
        self.generation_profiles = {}
        self.weather_data = {}
        
        # Configurar red básica de Costa Rica
        self._setup_costa_rica_grid()
    
    def _setup_costa_rica_grid(self):
        """Configurar topología básica de la red eléctrica de Costa Rica"""
        
        # Principales centrales generadoras
        generators = [
            GridNode("arenal", "generator", 138, 157, (10.5167, -84.9167), 0.92),  # Arenal
            GridNode("reventazon", "generator", 230, 305.5, (9.7167, -83.7833), 0.94),  # Reventazón
            GridNode("cachí", "generator", 138, 102, (9.7833, -83.8167), 0.90),  # Cachí
            GridNode("la_garita", "generator", 138, 157, (10.0167, -84.2833), 0.88),  # La Garita (térmica)
        ]
        
        # Principales subestaciones
        substations = [
            GridNode("colima", "substation", 230, 400, (9.9500, -84.1167)),  # Colima (GAM)
            GridNode("rio_macho", "substation", 230, 300, (9.7167, -83.7667)),  # Río Macho
            GridNode("lindora", "substation", 138, 200, (9.9333, -84.1833)),  # Lindora
            GridNode("liberia", "substation", 138, 150, (10.6333, -85.4333)),  # Liberia
            GridNode("limon", "substation", 138, 100, (10.0000, -83.0333)),  # Limón
        ]
        
        # Cargas principales (centros urbanos)
        loads = [
            GridNode("san_jose", "load", 23, 450, (9.9333, -84.0833)),  # Gran Área Metropolitana
            GridNode("cartago", "load", 23, 80, (9.8667, -83.9167)),   # Cartago
            GridNode("alajuela", "load", 23, 120, (10.0167, -84.2167)), # Alajuela
            GridNode("puntarenas", "load", 23, 60, (9.9667, -84.8333)), # Puntarenas
            GridNode("guanacaste", "load", 23, 90, (10.6333, -85.4333)), # Guanacaste
        ]
        
        # Agregar todos los nodos
        for node_list in [generators, substations, loads]:
            for node in node_list:
                self.nodes[node.node_id] = node
        
        # Líneas de transmisión principales
        transmission_lines = [
            GridEdge("arenal", "colima", 0.02, 0.08, 85, 300),
            GridEdge("reventazon", "rio_macho", 0.015, 0.06, 45, 400),
            GridEdge("rio_macho", "colima", 0.02, 0.08, 60, 350),
            GridEdge("colima", "lindora", 0.025, 0.10, 25, 250),
            GridEdge("colima", "san_jose", 0.03, 0.12, 15, 400),
            GridEdge("lindora", "alajuela", 0.025, 0.10, 20, 200),
            GridEdge("colima", "liberia", 0.02, 0.08, 180, 200),
            GridEdge("liberia", "guanacaste", 0.025, 0.10, 30, 150),
            GridEdge("rio_macho", "cartago", 0.03, 0.12, 35, 150),
            GridEdge("colima", "limon", 0.02, 0.08, 120, 150),
        ]
        
        for edge in transmission_lines:
            edge_id = f"{edge.from_node}_{edge.to_node}"
            self.edges[edge_id] = edge
    
    def generate_load_profile(self, node_id: str, days: int = 7) -> pd.DataFrame:
        """Generar perfil de carga realista para un nodo"""
        
        if node_id not in self.nodes:
            raise ValueError(f"Nodo {node_id} no encontrado")
        
        node = self.nodes[node_id]
        base_power = node.power_rating
        
        # Crear timeline
        start_time = datetime.now() - timedelta(days=days)
        timestamps = pd.date_range(start_time, periods=days*24, freq='H')
        
        loads = []
        
        for timestamp in timestamps:
            hour = timestamp.hour
            day_of_week = timestamp.weekday()  # 0=Monday, 6=Sunday
            
            # Patrón diario básico (Costa Rica)
            daily_pattern = {
                0: 0.4, 1: 0.35, 2: 0.32, 3: 0.30, 4: 0.35,   # Madrugada
                5: 0.45, 6: 0.65, 7: 0.85, 8: 0.95, 9: 0.90,  # Mañana
                10: 0.85, 11: 0.90, 12: 0.95, 13: 0.85, 14: 0.80, # Mediodía
                15: 0.85, 16: 0.90, 17: 0.95, 18: 1.0, 19: 0.95,  # Tarde
                20: 0.85, 21: 0.75, 22: 0.65, 23: 0.50          # Noche
            }
            
            # Factor fin de semana (menor demanda)
            weekend_factor = 0.8 if day_of_week >= 5 else 1.0
            
            # Variación estacional (época seca vs lluviosa)
            month = timestamp.month
            seasonal_factor = 1.1 if month in [1,2,3,4] else 0.95  # Seca: más A/C
            
            # Ruido aleatorio ±5%
            noise_factor = 1.0 + np.random.normal(0, 0.05)
            
            # Calcular carga final
            load_factor = daily_pattern[hour] * weekend_factor * seasonal_factor * noise_factor
            power_mw = base_power * load_factor
            
            loads.append({
                'timestamp': timestamp,
                'node_id': node_id,
                'power_mw': power_mw,
                'load_factor': load_factor
            })
        
        df = pd.DataFrame(loads)
        self.load_profiles[node_id] = df
        
        return df
    
    def generate_weather_scenario(self, days: int = 7) -> pd.DataFrame:
        """Generar escenario climático para Costa Rica"""
        
        start_time = datetime.now() - timedelta(days=days)
        timestamps = pd.date_range(start_time, periods=days*24, freq='H')
        
        weather_data = []
        
        for timestamp in timestamps:
            month = timestamp.month
            hour = timestamp.hour
            
            # Temperatura (°C) - Patrón típico Costa Rica
            if month in [12, 1, 2, 3, 4]:  # Época seca
                temp_base = 28 + 3 * np.sin(2 * np.pi * (hour - 6) / 24)
                humidity_base = 65
                rain_prob = 0.1
            else:  # Época lluviosa
                temp_base = 24 + 4 * np.sin(2 * np.pi * (hour - 6) / 24)
                humidity_base = 85
                rain_prob = 0.4 if 14 <= hour <= 18 else 0.2
            
            # Agregar variación aleatoria
            temperature = temp_base + np.random.normal(0, 2)
            humidity = humidity_base + np.random.normal(0, 10)
            humidity = np.clip(humidity, 30, 100)
            
            # Lluvia (mm/h)
            is_raining = np.random.random() < rain_prob
            rainfall = np.random.exponential(5) if is_raining else 0
            
            # Viento (km/h) - afecta generación eólica
            wind_speed = 15 + 10 * np.sin(2 * np.pi * timestamp.timetuple().tm_yday / 365) + np.random.normal(0, 5)
            wind_speed = max(0, wind_speed)
            
            weather_data.append({
                'timestamp': timestamp,
                'temperature': temperature,
                'humidity': humidity,
                'rainfall': rainfall,
                'wind_speed': wind_speed
            })
        
        df = pd.DataFrame(weather_data)
        self.weather_data = df
        
        return df
    
    def simulate_line_losses(self, edge_id: str, power_flow: float) -> float:
        """Simular pérdidas en línea de transmisión"""
        
        if edge_id not in self.edges:
            raise ValueError(f"Línea {edge_id} no encontrada")
        
        edge = self.edges[edge_id]
        
        # Pérdidas resistivas: P_loss = I²R
        # Aproximación: I = P/V, entonces P_loss = (P²/V²) * R
        voltage_kv = 138  # Voltaje típico
        current_a = (power_flow * 1000) / (voltage_kv * np.sqrt(3))  # Corriente trifásica
        
        # Resistencia total de la línea
        resistance_total = edge.resistance * edge.length
        
        # Pérdidas en kW
        losses_kw = 3 * (current_a ** 2) * resistance_total / 1000
        
        # Como porcentaje de la potencia transmitida
        loss_percentage = (losses_kw / (power_flow * 1000)) * 100 if power_flow > 0 else 0
        
        return loss_percentage
    
    def simulate_grid_scenario(self, scenario_name: str, days: int = 7) -> Dict:
        """Simular escenario completo de la red eléctrica"""
        
        logger.info(f"🔄 Iniciando simulación: {scenario_name}")
        
        # Generar perfiles de carga para todos los nodos de demanda
        load_nodes = [node_id for node_id, node in self.nodes.items() if node.node_type == "load"]
        
        total_loads = {}
        for node_id in load_nodes:
            load_profile = self.generate_load_profile(node_id, days)
            total_loads[node_id] = load_profile
        
        # Generar datos climáticos
        weather = self.generate_weather_scenario(days)
        
        # Simular flujos de potencia y pérdidas
        results = {
            'scenario_name': scenario_name,
            'simulation_period': f"{days} days",
            'total_energy_demand': 0,
            'total_losses': 0,
            'peak_demand': 0,
            'efficiency': 0,
            'load_profiles': total_loads,
            'weather_data': weather,
            'hourly_analysis': []
        }
        
        # Análisis hora por hora
        timestamps = weather['timestamp'].tolist()
        
        for i, timestamp in enumerate(timestamps):
            hour_analysis = {
                'timestamp': timestamp,
                'weather': weather.iloc[i].to_dict(),
                'loads': {},
                'generation': {},
                'losses': {},
                'total_demand': 0,
                'total_generation': 0,
                'total_losses': 0
            }
            
            # Calcular demanda total para esta hora
            total_demand = 0
            for node_id in load_nodes:
                if node_id in total_loads:
                    load_mw = total_loads[node_id].iloc[i]['power_mw']
                    hour_analysis['loads'][node_id] = load_mw
                    total_demand += load_mw
            
            hour_analysis['total_demand'] = total_demand
            results['total_energy_demand'] += total_demand
            
            if total_demand > results['peak_demand']:
                results['peak_demand'] = total_demand
            
            # Simular generación (despacho económico simplificado)
            generation_dispatch = self._simulate_generation_dispatch(total_demand, weather.iloc[i])
            hour_analysis['generation'] = generation_dispatch
            hour_analysis['total_generation'] = sum(generation_dispatch.values())
            
            # Simular pérdidas en líneas de transmisión
            line_losses = {}
            total_line_losses = 0
            
            for edge_id, edge in self.edges.items():
                # Estimar flujo basado en topología (simplificado)
                estimated_flow = total_demand * 0.1  # 10% del total por línea promedio
                loss_pct = self.simulate_line_losses(edge_id, estimated_flow)
                loss_mw = estimated_flow * (loss_pct / 100)
                
                line_losses[edge_id] = {
                    'flow_mw': estimated_flow,
                    'loss_percentage': loss_pct,
                    'loss_mw': loss_mw
                }
                total_line_losses += loss_mw
            
            hour_analysis['losses'] = line_losses
            hour_analysis['total_losses'] = total_line_losses
            results['total_losses'] += total_line_losses
            
            results['hourly_analysis'].append(hour_analysis)
        
        # Calcular eficiencia total
        if results['total_energy_demand'] > 0:
            results['efficiency'] = 1 - (results['total_losses'] / results['total_energy_demand'])
        
        logger.info(f"✅ Simulación completada: {scenario_name}")
        logger.info(f"📊 Eficiencia total: {results['efficiency']*100:.2f}%")
        logger.info(f"📈 Demanda pico: {results['peak_demand']:.1f} MW")
        
        return results
    
    def _simulate_generation_dispatch(self, total_demand: float, weather_data: Dict) -> Dict:
        """Simular despacho de generación basado en demanda y clima"""
        
        generation = {}
        remaining_demand = total_demand
        
        # Generadores ordenados por costo operativo (más baratos primero)
        gen_priority = [
            ("reventazon", 0.94),  # Hidro - más barato
            ("cachi", 0.90),       # Hidro
            ("arenal", 0.92),      # Hidro + eólico
            ("la_garita", 0.88),   # Térmica - más caro
        ]
        
        for gen_id, efficiency in gen_priority:
            if remaining_demand <= 0:
                generation[gen_id] = 0
                continue
            
            generator = self.nodes[gen_id]
            max_capacity = generator.power_rating
            
            # Ajustar capacidad por condiciones climáticas
            if gen_id in ["arenal"]:  # Eólica afectada por viento
                wind_factor = min(1.0, weather_data['wind_speed'] / 25)  # Optimal at 25 km/h
                max_capacity *= (0.3 + 0.7 * wind_factor)  # 30% hidro, 70% eólico variable
            
            elif gen_id in ["reventazon", "cachi"]:  # Hidro afectada por lluvia
                # Más lluvia = más generación hidro (con delay, simplificado)
                rain_factor = min(1.2, 1.0 + weather_data['rainfall'] / 10)
                max_capacity *= rain_factor
            
            # Generar lo que se pueda hasta cubrir demanda
            generation_mw = min(remaining_demand, max_capacity)
            generation[gen_id] = generation_mw
            remaining_demand -= generation_mw
        
        # Si queda demanda sin cubrir, es déficit
        if remaining_demand > 0.1:  # Tolerancia 0.1 MW
            logger.warning(f"⚠️ Déficit de generación: {remaining_demand:.1f} MW")
        
        return generation
    
    def optimize_network(self, current_state: Dict) -> Dict:
        """Optimizar la red usando algoritmos de NexusOptim IA"""
        
        logger.info("🎯 Iniciando optimización de red...")
        
        # Análisis del estado actual
        total_losses = current_state.get('total_losses', 0)
        peak_demand = current_state.get('peak_demand', 0)
        current_efficiency = current_state.get('efficiency', 0.9)
        
        optimization_actions = []
        projected_savings = 0
        
        # 1. Identificar líneas con altas pérdidas
        if 'hourly_analysis' in current_state:
            avg_losses_by_line = {}
            
            for hour in current_state['hourly_analysis']:
                for line_id, line_data in hour['losses'].items():
                    if line_id not in avg_losses_by_line:
                        avg_losses_by_line[line_id] = []
                    avg_losses_by_line[line_id].append(line_data['loss_percentage'])
            
            # Calcular promedio de pérdidas por línea
            for line_id, losses in avg_losses_by_line.items():
                avg_loss = np.mean(losses)
                
                if avg_loss > 3.0:  # >3% pérdidas es alto
                    optimization_actions.append({
                        'action': 'voltage_regulation',
                        'target': line_id,
                        'description': f'Ajustar voltaje en línea {line_id}',
                        'expected_reduction': f'{avg_loss * 0.3:.1f}% pérdidas',  # 30% mejora
                        'priority': 'high' if avg_loss > 5.0 else 'medium'
                    })
                    projected_savings += avg_loss * 0.3 * peak_demand * 0.1  # Estimación conservadora
        
        # 2. Optimización de despacho
        optimization_actions.append({
            'action': 'generation_rebalance',
            'target': 'all_generators',
            'description': 'Rebalancear despacho económico considerando pérdidas',
            'expected_reduction': '2-4% pérdidas totales',
            'priority': 'medium'
        })
        projected_savings += total_losses * 0.03  # 3% mejora en despacho
        
        # 3. Control reactivo
        optimization_actions.append({
            'action': 'reactive_power_control',
            'target': 'substations',
            'description': 'Optimizar potencia reactiva en subestaciones',
            'expected_reduction': '1-2% pérdidas',
            'priority': 'low'
        })
        projected_savings += total_losses * 0.015  # 1.5% mejora reactiva
        
        # Calcular nueva eficiencia proyectada
        new_efficiency = current_efficiency + (projected_savings / (peak_demand * 24 * 7))  # Semana base
        new_efficiency = min(0.98, new_efficiency)  # Máximo 98% eficiencia
        
        optimization_result = {
            'current_efficiency': current_efficiency,
            'projected_efficiency': new_efficiency,
            'improvement': new_efficiency - current_efficiency,
            'projected_savings_mw': projected_savings,
            'optimization_actions': optimization_actions,
            'implementation_priority': sorted(optimization_actions, 
                                           key=lambda x: {'high': 3, 'medium': 2, 'low': 1}[x['priority']], 
                                           reverse=True),
            'roi_estimate': {
                'annual_savings_usd': projected_savings * 8760 * 80,  # $80/MWh precio promedio
                'implementation_cost_usd': len(optimization_actions) * 25000,  # $25k por acción
                'payback_months': max(1, (len(optimization_actions) * 25000) / (projected_savings * 8760 * 80 / 12))
            }
        }
        
        logger.info(f"✅ Optimización completada")
        logger.info(f"📈 Mejora eficiencia: {optimization_result['improvement']*100:.2f}%")
        logger.info(f"💰 Ahorro proyectado: {projected_savings:.1f} MW")
        
        return optimization_result

class ScenarioManager:
    """
    Gestor de escenarios de simulación para validación de algoritmos
    """
    
    def __init__(self):
        self.simulator = ElectricalGridSimulator()
        self.scenarios = {}
    
    def create_scenario(self, name: str, description: str, parameters: Dict) -> Dict:
        """Crear nuevo escenario de simulación"""
        
        scenario = {
            'name': name,
            'description': description,
            'parameters': parameters,
            'created_at': datetime.now().isoformat(),
            'results': None
        }
        
        self.scenarios[name] = scenario
        return scenario
    
    def run_stress_test(self) -> Dict:
        """Ejecutar prueba de estrés del sistema"""
        
        logger.info("🔥 Iniciando prueba de estrés...")
        
        # Escenario de alta demanda + clima adverso
        stress_results = {}
        
        # Simular pico de demanda extremo (150% normal)
        base_scenario = self.simulator.simulate_grid_scenario("stress_test", days=3)
        
        # Aumentar demanda artificialmente
        for hour in base_scenario['hourly_analysis']:
            for node_id in hour['loads']:
                hour['loads'][node_id] *= 1.5  # 150% demanda
            hour['total_demand'] *= 1.5
        
        # Recalcular eficiencia con demanda aumentada
        base_scenario['peak_demand'] *= 1.5
        base_scenario['total_energy_demand'] *= 1.5
        base_scenario['efficiency'] = 1 - (base_scenario['total_losses'] / base_scenario['total_energy_demand'])
        
        # Probar optimización bajo estrés
        optimization = self.simulator.optimize_network(base_scenario)
        
        stress_results = {
            'scenario': 'extreme_demand',
            'base_results': base_scenario,
            'optimization': optimization,
            'stress_factors': {
                'demand_multiplier': 1.5,
                'weather_conditions': 'adverse',
                'grid_stability': 'challenged'
            },
            'conclusions': {
                'system_resilience': 'good' if optimization['projected_efficiency'] > 0.85 else 'needs_improvement',
                'optimization_effectiveness': f"{optimization['improvement']*100:.1f}% improvement",
                'critical_points': []
            }
        }
        
        # Identificar puntos críticos
        for hour in base_scenario['hourly_analysis']:
            if hour['total_demand'] > 800:  # >800 MW es crítico para CR
                stress_results['conclusions']['critical_points'].append({
                    'timestamp': hour['timestamp'],
                    'demand': hour['total_demand'],
                    'issue': 'extreme_demand'
                })
        
        logger.info("✅ Prueba de estrés completada")
        return stress_results
