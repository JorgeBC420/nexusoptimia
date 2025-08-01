"""
Data Pipeline: Ingesta y procesamiento de datos en tiempo real
Pipeline optimizado para sensores LoRa y datos de CajaCentral POS

Funcionalidades:
- Ingesta de datos desde sensores LoRa (915MHz - Costa Rica)
- Procesamiento de señales de voltaje/corriente (ADS1115 + SCT-013)
- Limpieza y transformación de datos con pandas/dask
- Pipeline de entrenamiento continuo de modelos
"""

import asyncio
import logging
import pandas as pd
import numpy as np
from datetime import datetime, timedelta
from typing import Dict, List, Optional, AsyncGenerator
import json
from pathlib import Path

from ..core.config import settings

logger = logging.getLogger(__name__)

class SensorDataProcessor:
    """
    Procesador de datos de sensores con limpieza y validación
    """
    
    def __init__(self):
        self.voltage_range = (100, 130)  # Voltaje válido en Costa Rica
        self.current_range = (0, 200)    # Corriente máxima esperada
        self.temperature_range = (-10, 60)  # Temperatura ambiente CR
        
    def validate_sensor_data(self, data: Dict) -> Dict:
        """Validar y limpiar datos de sensores"""
        try:
            cleaned_data = data.copy()
            validation_errors = []
            
            # Validar voltaje
            if 'voltage' in data:
                voltage = float(data['voltage'])
                if not (self.voltage_range[0] <= voltage <= self.voltage_range[1]):
                    validation_errors.append(f"Voltaje fuera de rango: {voltage}V")
                    cleaned_data['voltage'] = np.clip(voltage, *self.voltage_range)
                    
            # Validar corriente
            if 'current' in data:
                current = float(data['current'])
                if not (self.current_range[0] <= current <= self.current_range[1]):
                    validation_errors.append(f"Corriente fuera de rango: {current}A")
                    cleaned_data['current'] = np.clip(current, *self.current_range)
                    
            # Validar temperatura
            if 'temperature' in data:
                temp = float(data['temperature'])
                if not (self.temperature_range[0] <= temp <= self.temperature_range[1]):
                    validation_errors.append(f"Temperatura fuera de rango: {temp}°C")
                    cleaned_data['temperature'] = np.clip(temp, *self.temperature_range)
            
            # Calcular métricas derivadas
            if 'voltage' in cleaned_data and 'current' in cleaned_data:
                cleaned_data['power'] = cleaned_data['voltage'] * cleaned_data['current']
                
            # Agregar timestamp si no existe
            if 'timestamp' not in cleaned_data:
                cleaned_data['timestamp'] = datetime.now().isoformat()
                
            # Agregar información de validación
            cleaned_data['validation_errors'] = validation_errors
            cleaned_data['is_valid'] = len(validation_errors) == 0
            
            return cleaned_data
            
        except Exception as e:
            logger.error(f"❌ Error validando datos: {e}")
            return {"error": str(e), "original_data": data}
    
    def calculate_power_quality_metrics(self, data: Dict) -> Dict:
        """Calcular métricas de calidad de energía"""
        try:
            metrics = {}
            
            # Total Harmonic Distortion (simulado)
            if 'voltage' in data and 'current' in data:
                voltage = data['voltage']
                current = data['current']
                
                # THD simplificado (en producción usar FFT)
                metrics['thd_voltage'] = abs(voltage - 120) / 120 * 100  # % THD
                metrics['thd_current'] = abs(current - np.mean([current])) / current * 100 if current > 0 else 0
                
                # Factor de potencia estimado
                metrics['power_factor'] = min(1.0, voltage * current / (voltage * current + 10))
                
                # Efficiency estimation
                metrics['efficiency'] = max(0.7, min(0.98, 1 - (metrics['thd_voltage'] + metrics['thd_current']) / 1000))
                
            return metrics
            
        except Exception as e:
            logger.error(f"❌ Error calculando métricas: {e}")
            return {}

class LoRaDataIngestion:
    """
    Sistema de ingesta de datos desde sensores LoRa
    """
    
    def __init__(self):
        self.processor = SensorDataProcessor()
        self.active_sensors = {}
        self.data_buffer = []
        self.buffer_size = 1000
        
    async def start_ingestion(self) -> None:
        """Iniciar proceso de ingesta de datos"""
        logger.info(f"📡 Iniciando ingesta LoRa en {settings.LORA_FREQUENCY} Hz")
        
        # TODO: Implementar conexión real con gateway LoRa
        # Por ahora simulamos datos
        await self._simulate_sensor_data()
    
    async def _simulate_sensor_data(self) -> None:
        """Simular datos de sensores para desarrollo"""
        sensor_ids = ["NXS_001", "NXS_002", "NXS_003", "NXS_004", "NXS_005"]
        
        while True:
            try:
                for sensor_id in sensor_ids:
                    # Simular datos realistas
                    base_voltage = 120 + np.random.normal(0, 2)  # 120V ± 2V
                    base_current = 50 + np.random.normal(0, 5)   # 50A ± 5A
                    temperature = 25 + np.random.normal(0, 3)    # 25°C ± 3°C
                    humidity = 70 + np.random.normal(0, 10)      # 70% ± 10%
                    
                    # Simular variaciones por hora del día
                    hour = datetime.now().hour
                    demand_factor = 0.7 + 0.3 * np.sin(2 * np.pi * (hour - 6) / 24)
                    
                    raw_data = {
                        "sensor_id": sensor_id,
                        "voltage": base_voltage * demand_factor,
                        "current": base_current * demand_factor,
                        "temperature": temperature,
                        "humidity": humidity,
                        "timestamp": datetime.now().isoformat()
                    }
                    
                    # Procesar datos
                    processed_data = await self.process_sensor_reading(raw_data)
                    
                    # Agregar a buffer
                    self.data_buffer.append(processed_data)
                    
                    # Limpiar buffer si está lleno
                    if len(self.data_buffer) > self.buffer_size:
                        self.data_buffer = self.data_buffer[-self.buffer_size//2:]
                
                # Esperar intervalo de muestreo
                await asyncio.sleep(60)  # 1 minuto entre muestras
                
            except Exception as e:
                logger.error(f"❌ Error en simulación de datos: {e}")
                await asyncio.sleep(5)
    
    async def process_sensor_reading(self, raw_data: Dict) -> Dict:
        """Procesar lectura individual de sensor"""
        try:
            # Validar y limpiar datos
            validated_data = self.processor.validate_sensor_data(raw_data)
            
            # Calcular métricas de calidad
            quality_metrics = self.processor.calculate_power_quality_metrics(validated_data)
            validated_data.update(quality_metrics)
            
            # Detectar patrones anómalos simples
            validated_data['anomaly_flags'] = self._detect_simple_anomalies(validated_data)
            
            logger.debug(f"📊 Datos procesados para {validated_data.get('sensor_id')}")
            
            return validated_data
            
        except Exception as e:
            logger.error(f"❌ Error procesando lectura: {e}")
            return {"error": str(e), "raw_data": raw_data}
    
    def _detect_simple_anomalies(self, data: Dict) -> List[str]:
        """Detectar anomalías simples en tiempo real"""
        flags = []
        
        # Voltaje crítico
        if 'voltage' in data:
            if data['voltage'] < 105 or data['voltage'] > 135:
                flags.append("voltage_critical")
                
        # Sobrecorriente
        if 'current' in data:
            if data['current'] > 100:
                flags.append("overcurrent")
                
        # Temperatura alta
        if 'temperature' in data:
            if data['temperature'] > 45:
                flags.append("high_temperature")
                
        # Eficiencia baja
        if 'efficiency' in data:
            if data['efficiency'] < 0.8:
                flags.append("low_efficiency")
                
        return flags
    
    def get_recent_data(self, sensor_id: Optional[str] = None, 
                       minutes: int = 60) -> List[Dict]:
        """Obtener datos recientes del buffer"""
        cutoff_time = datetime.now() - timedelta(minutes=minutes)
        
        filtered_data = []
        for data in self.data_buffer:
            try:
                data_time = datetime.fromisoformat(data['timestamp'])
                if data_time >= cutoff_time:
                    if sensor_id is None or data.get('sensor_id') == sensor_id:
                        filtered_data.append(data)
            except:
                continue
                
        return filtered_data

class CajaCentralIntegration:
    """
    Integración con datos anónimos de CajaCentral POS
    Correlaciona patrones de demanda energética con actividad comercial
    """
    
    def __init__(self):
        self.correlation_models = {}
        
    async def correlate_energy_commerce(self, energy_data: List[Dict], 
                                       commerce_data: List[Dict]) -> Dict:
        """Correlacionar datos energéticos con actividad comercial"""
        try:
            # Convertir a DataFrames para análisis
            energy_df = pd.DataFrame(energy_data)
            commerce_df = pd.DataFrame(commerce_data)
            
            # Agrupar por hora
            energy_hourly = energy_df.groupby(
                pd.to_datetime(energy_df['timestamp']).dt.hour
            )['power'].mean()
            
            commerce_hourly = commerce_df.groupby(
                pd.to_datetime(commerce_df['timestamp']).dt.hour
            )['transaction_count'].sum()
            
            # Calcular correlación
            correlation = energy_hourly.corr(commerce_hourly)
            
            return {
                "correlation_coefficient": float(correlation),
                "energy_peaks": energy_hourly.nlargest(3).to_dict(),
                "commerce_peaks": commerce_hourly.nlargest(3).to_dict(),
                "insights": self._generate_insights(correlation)
            }
            
        except Exception as e:
            logger.error(f"❌ Error en correlación: {e}")
            return {"error": str(e)}
    
    def _generate_insights(self, correlation: float) -> List[str]:
        """Generar insights basados en correlación"""
        insights = []
        
        if correlation > 0.7:
            insights.append("Alta correlación: Demanda energética sigue patrones comerciales")
        elif correlation > 0.4:
            insights.append("Correlación moderada: Algunos patrones comerciales afectan demanda")
        else:
            insights.append("Baja correlación: Demanda energética independiente de actividad comercial")
            
        return insights

class DataPipeline:
    """
    Pipeline principal de datos para NexusOptim IA
    """
    
    def __init__(self):
        self.lora_ingestion = LoRaDataIngestion()
        self.cajacentral_integration = CajaCentralIntegration()
        self.is_running = False
        
    async def start_pipeline(self) -> None:
        """Iniciar pipeline completo de datos"""
        logger.info("🔄 Iniciando Data Pipeline de NexusOptim")
        
        self.is_running = True
        
        # Iniciar tareas asíncronas
        tasks = [
            asyncio.create_task(self.lora_ingestion.start_ingestion()),
            asyncio.create_task(self._periodic_analysis()),
        ]
        
        await asyncio.gather(*tasks)
    
    async def _periodic_analysis(self) -> None:
        """Análisis periódico de datos acumulados"""
        while self.is_running:
            try:
                # Obtener datos recientes
                recent_data = self.lora_ingestion.get_recent_data(minutes=60)
                
                if len(recent_data) > 10:
                    # Generar reporte de análisis
                    analysis = self._analyze_data_batch(recent_data)
                    logger.info(f"📈 Análisis completado: {len(recent_data)} muestras")
                    
                    # TODO: Enviar análisis a sistema de monitoreo
                
                await asyncio.sleep(300)  # Análisis cada 5 minutos
                
            except Exception as e:
                logger.error(f"❌ Error en análisis periódico: {e}")
                await asyncio.sleep(60)
    
    def _analyze_data_batch(self, data_batch: List[Dict]) -> Dict:
        """Analizar lote de datos para tendencias"""
        try:
            df = pd.DataFrame(data_batch)
            
            analysis = {
                "sample_count": len(data_batch),
                "voltage_stats": {
                    "mean": float(df['voltage'].mean()),
                    "std": float(df['voltage'].std()),
                    "min": float(df['voltage'].min()),
                    "max": float(df['voltage'].max())
                },
                "current_stats": {
                    "mean": float(df['current'].mean()),
                    "std": float(df['current'].std()),
                    "min": float(df['current'].min()),
                    "max": float(df['current'].max())
                },
                "anomaly_count": sum(1 for d in data_batch if d.get('anomaly_flags')),
                "timestamp": datetime.now().isoformat()
            }
            
            return analysis
            
        except Exception as e:
            logger.error(f"❌ Error analizando batch: {e}")
            return {"error": str(e)}
