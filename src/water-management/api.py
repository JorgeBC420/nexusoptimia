"""
API endpoints para gestión de infraestructura hídrica
Servicios REST para monitoreo y control de agua
"""

from fastapi import APIRouter, HTTPException, Depends, BackgroundTasks
from fastapi.responses import JSONResponse
from typing import Dict, List, Optional
import asyncio
from datetime import datetime, timedelta
import logging

from .config import WATER_SENSOR_CONFIG, EMERGENCY_RESPONSE_CONFIG
from . import WaterManagementCore, LeakAlert, WaterSensor

logger = logging.getLogger(__name__)

# Router para API de gestión de agua
water_router = APIRouter(prefix="/api/v1/water", tags=["water-management"])

# Instancia global del sistema de gestión
water_system: Optional[WaterManagementCore] = None

def get_water_system() -> WaterManagementCore:
    """Obtener instancia del sistema de gestión de agua"""
    global water_system
    if water_system is None:
        water_system = WaterManagementCore()
    return water_system

@water_router.post("/start-monitoring")
async def start_water_monitoring(
    background_tasks: BackgroundTasks,
    system: WaterManagementCore = Depends(get_water_system)
):
    """Iniciar monitoreo automático de la red hídrica"""
    
    try:
        if system.is_monitoring:
            return JSONResponse(
                status_code=200,
                content={
                    "message": "Sistema ya está monitoreando",
                    "status": "monitoring",
                    "started_at": datetime.now().isoformat()
                }
            )
        
        # Iniciar monitoreo en segundo plano
        background_tasks.add_task(system.start_monitoring)
        
        logger.info("💧 Monitoreo hídrico iniciado desde API")
        
        return JSONResponse(
            status_code=200,
            content={
                "message": "Monitoreo hídrico iniciado exitosamente",
                "status": "starting",
                "sensors_count": len(system.simulator.sensors),
                "started_at": datetime.now().isoformat()
            }
        )
        
    except Exception as e:
        logger.error(f"❌ Error iniciando monitoreo hídrico: {e}")
        raise HTTPException(status_code=500, detail=f"Error iniciando monitoreo: {str(e)}")

@water_router.post("/stop-monitoring")
async def stop_water_monitoring(
    system: WaterManagementCore = Depends(get_water_system)
):
    """Detener monitoreo de la red hídrica"""
    
    try:
        system.is_monitoring = False
        
        logger.info("💧 Monitoreo hídrico detenido desde API")
        
        return JSONResponse(
            status_code=200,
            content={
                "message": "Monitoreo hídrico detenido",
                "status": "stopped",
                "stopped_at": datetime.now().isoformat()
            }
        )
        
    except Exception as e:
        logger.error(f"❌ Error deteniendo monitoreo: {e}")
        raise HTTPException(status_code=500, detail=f"Error deteniendo monitoreo: {str(e)}")

@water_router.get("/status")
async def get_water_system_status(
    system: WaterManagementCore = Depends(get_water_system)
):
    """Obtener estado completo del sistema hídrico"""
    
    try:
        status = await system.get_system_status()
        return JSONResponse(status_code=200, content=status)
        
    except Exception as e:
        logger.error(f"❌ Error obteniendo estado del sistema: {e}")
        raise HTTPException(status_code=500, detail=f"Error obteniendo estado: {str(e)}")

@water_router.get("/sensors")
async def list_water_sensors(
    water_source: Optional[str] = None,
    municipality: Optional[str] = None,
    sensor_type: Optional[str] = None,
    system: WaterManagementCore = Depends(get_water_system)
):
    """Listar sensores de agua con filtros opcionales"""
    
    try:
        sensors = []
        
        for sensor_id, sensor in system.simulator.sensors.items():
            # Aplicar filtros
            if water_source and sensor.water_source != water_source:
                continue
            if municipality and sensor.municipality != municipality:
                continue
            if sensor_type and sensor.sensor_type != sensor_type:
                continue
            
            sensor_data = {
                "sensor_id": sensor.sensor_id,
                "sensor_type": sensor.sensor_type,
                "location": {"lat": sensor.location[0], "lon": sensor.location[1]},
                "municipality": sensor.municipality,
                "water_source": sensor.water_source,
                "pipe_diameter": sensor.pipe_diameter,
                "normal_pressure": sensor.normal_pressure,
                "normal_flow": sensor.normal_flow,
                "installation_date": sensor.installation_date
            }
            sensors.append(sensor_data)
        
        return JSONResponse(
            status_code=200,
            content={
                "sensors": sensors,
                "total_count": len(sensors),
                "filters_applied": {
                    "water_source": water_source,
                    "municipality": municipality,
                    "sensor_type": sensor_type
                }
            }
        )
        
    except Exception as e:
        logger.error(f"❌ Error listando sensores: {e}")
        raise HTTPException(status_code=500, detail=f"Error listando sensores: {str(e)}")

@water_router.get("/sensors/{sensor_id}")
async def get_sensor_details(
    sensor_id: str,
    system: WaterManagementCore = Depends(get_water_system)
):
    """Obtener detalles específicos de un sensor"""
    
    try:
        if sensor_id not in system.simulator.sensors:
            raise HTTPException(status_code=404, detail=f"Sensor {sensor_id} no encontrado")
        
        sensor = system.simulator.sensors[sensor_id]
        
        # Simular lectura actual
        current_reading = system._simulate_sensor_reading(sensor)
        
        # Analizar con IA
        analysis = system.leak_detector.analyze_sensor_data(current_reading)
        
        sensor_details = {
            "sensor_info": {
                "sensor_id": sensor.sensor_id,
                "sensor_type": sensor.sensor_type,
                "location": {"lat": sensor.location[0], "lon": sensor.location[1]},
                "municipality": sensor.municipality,
                "water_source": sensor.water_source,
                "pipe_diameter": sensor.pipe_diameter,
                "installation_date": sensor.installation_date
            },
            "current_reading": current_reading,
            "ai_analysis": analysis,
            "normal_parameters": {
                "pressure": sensor.normal_pressure,
                "flow": sensor.normal_flow
            }
        }
        
        return JSONResponse(status_code=200, content=sensor_details)
        
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"❌ Error obteniendo detalles del sensor {sensor_id}: {e}")
        raise HTTPException(status_code=500, detail=f"Error obteniendo sensor: {str(e)}")

@water_router.get("/alerts")
async def list_active_alerts(
    severity: Optional[str] = None,
    municipality: Optional[str] = None,
    limit: int = 50,
    system: WaterManagementCore = Depends(get_water_system)
):
    """Listar alertas activas de fugas"""
    
    try:
        alerts = []
        
        for alert_id, alert in system.active_alerts.items():
            # Aplicar filtros
            if severity and alert.severity != severity:
                continue
            
            # Obtener información del sensor para filtro de municipalidad
            sensor = system.simulator.sensors.get(alert.sensor_id)
            if municipality and sensor and sensor.municipality != municipality:
                continue
            
            alert_data = {
                "alert_id": alert.alert_id,
                "sensor_id": alert.sensor_id,
                "location": {"lat": alert.location[0], "lon": alert.location[1]},
                "severity": alert.severity,
                "estimated_loss": alert.estimated_loss,
                "confidence": alert.confidence,
                "detection_time": alert.detection_time.isoformat(),
                "description": alert.description,
                "recommended_actions": alert.recommended_actions,
                "municipality": sensor.municipality if sensor else "Unknown"
            }
            alerts.append(alert_data)
        
        # Ordenar por tiempo de detección (más recientes primero)
        alerts.sort(key=lambda x: x["detection_time"], reverse=True)
        
        # Aplicar límite
        alerts = alerts[:limit]
        
        return JSONResponse(
            status_code=200,
            content={
                "alerts": alerts,
                "total_count": len(alerts),
                "filters_applied": {
                    "severity": severity,
                    "municipality": municipality,
                    "limit": limit
                }
            }
        )
        
    except Exception as e:
        logger.error(f"❌ Error listando alertas: {e}")
        raise HTTPException(status_code=500, detail=f"Error listando alertas: {str(e)}")

@water_router.post("/simulate-leak")
async def simulate_leak_scenario(
    sensor_id: str,
    severity: str = "moderate",
    system: WaterManagementCore = Depends(get_water_system)
):
    """Simular escenario de fuga para pruebas"""
    
    try:
        if sensor_id not in system.simulator.sensors:
            raise HTTPException(status_code=404, detail=f"Sensor {sensor_id} no encontrado")
        
        if severity not in ["minor", "moderate", "major", "critical"]:
            raise HTTPException(status_code=400, detail="Severidad debe ser: minor, moderate, major, critical")
        
        # Simular fuga
        leak_data = system.simulator.simulate_leak_scenario(sensor_id, severity)
        
        # Analizar con IA
        analysis = system.leak_detector.analyze_sensor_data(leak_data)
        
        # Si requiere acción, procesar como fuga real
        if analysis.get("requires_action", False):
            sensor = system.simulator.sensors[sensor_id]
            await system._process_leak_detection(sensor, analysis)
        
        return JSONResponse(
            status_code=200,
            content={
                "message": f"Simulación de fuga {severity} ejecutada",
                "sensor_id": sensor_id,
                "simulation_data": leak_data,
                "ai_analysis": analysis,
                "alert_created": analysis.get("requires_action", False)
            }
        )
        
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"❌ Error simulando fuga: {e}")
        raise HTTPException(status_code=500, detail=f"Error en simulación: {str(e)}")

@water_router.post("/emergency-response/{alert_id}")
async def trigger_emergency_response(
    alert_id: str,
    system: WaterManagementCore = Depends(get_water_system)
):
    """Activar respuesta de emergencia manual para una alerta"""
    
    try:
        if alert_id not in system.active_alerts:
            raise HTTPException(status_code=404, detail=f"Alerta {alert_id} no encontrada")
        
        alert = system.active_alerts[alert_id]
        
        # Activar respuesta de emergencia
        response = await system.emergency_system.handle_leak_emergency(alert)
        
        return JSONResponse(
            status_code=200,
            content={
                "message": "Respuesta de emergencia activada",
                "alert_id": alert_id,
                "response_details": response
            }
        )
        
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"❌ Error activando respuesta de emergencia: {e}")
        raise HTTPException(status_code=500, detail=f"Error en respuesta: {str(e)}")

@water_router.get("/response-teams")
async def list_response_teams(
    system: WaterManagementCore = Depends(get_water_system)
):
    """Listar equipos de respuesta disponibles"""
    
    try:
        teams = system.emergency_system.response_teams
        
        return JSONResponse(
            status_code=200,
            content={
                "response_teams": teams,
                "total_teams": len(teams)
            }
        )
        
    except Exception as e:
        logger.error(f"❌ Error listando equipos de respuesta: {e}")
        raise HTTPException(status_code=500, detail=f"Error listando equipos: {str(e)}")

@water_router.get("/municipalities")
async def list_municipalities(
    system: WaterManagementCore = Depends(get_water_system)
):
    """Listar municipalidades con sensores instalados"""
    
    try:
        municipalities = set()
        for sensor in system.simulator.sensors.values():
            municipalities.add(sensor.municipality)
        
        municipality_stats = {}
        for municipality in municipalities:
            sensors_in_municipality = [
                s for s in system.simulator.sensors.values() 
                if s.municipality == municipality
            ]
            
            municipality_stats[municipality] = {
                "total_sensors": len(sensors_in_municipality),
                "by_type": {},
                "by_source": {}
            }
            
            for sensor in sensors_in_municipality:
                # Contar por tipo
                sensor_type = sensor.sensor_type
                municipality_stats[municipality]["by_type"][sensor_type] = \
                    municipality_stats[municipality]["by_type"].get(sensor_type, 0) + 1
                
                # Contar por fuente
                water_source = sensor.water_source
                municipality_stats[municipality]["by_source"][water_source] = \
                    municipality_stats[municipality]["by_source"].get(water_source, 0) + 1
        
        return JSONResponse(
            status_code=200,
            content={
                "municipalities": list(municipalities),
                "detailed_stats": municipality_stats,
                "total_municipalities": len(municipalities)
            }
        )
        
    except Exception as e:
        logger.error(f"❌ Error listando municipalidades: {e}")
        raise HTTPException(status_code=500, detail=f"Error listando municipalidades: {str(e)}")

@water_router.get("/metrics/dashboard")
async def get_dashboard_metrics(
    system: WaterManagementCore = Depends(get_water_system)
):
    """Obtener métricas para dashboard ejecutivo"""
    
    try:
        status = await system.get_system_status()
        
        # Calcular métricas adicionales
        total_sensors = status["total_sensors"]
        active_alerts = status["active_alerts"] 
        daily_loss_liters = status["daily_estimated_loss_liters"]
        
        # Métricas de eficiencia
        detection_rate = (active_alerts / max(total_sensors, 1)) * 100
        system_health = max(0, 100 - (active_alerts * 10))  # Simplificado
        
        # Impacto económico (estimado)
        cost_per_liter = 0.35  # colones por litro
        daily_loss_cost = daily_loss_liters * cost_per_liter
        monthly_loss_cost = daily_loss_cost * 30
        
        dashboard_metrics = {
            "system_overview": {
                "status": status["system_status"],
                "total_sensors": total_sensors,
                "active_alerts": active_alerts,
                "system_health_percentage": round(system_health, 1)
            },
            
            "water_losses": {
                "daily_loss_liters": daily_loss_liters,
                "monthly_loss_liters": daily_loss_liters * 30,
                "daily_cost_colones": round(daily_loss_cost),
                "monthly_cost_colones": round(monthly_loss_cost)
            },
            
            "coverage_stats": status["coverage_area"],
            
            "alert_breakdown": status["severity_breakdown"],
            
            "performance_indicators": {
                "detection_rate_percentage": round(detection_rate, 2),
                "average_response_time_minutes": 65,  # Promedio estimado
                "false_positive_rate": 12,  # % estimado
                "uptime_percentage": 98.5
            },
            
            "last_updated": status["last_update"]
        }
        
        return JSONResponse(status_code=200, content=dashboard_metrics)
        
    except Exception as e:
        logger.error(f"❌ Error generando métricas de dashboard: {e}")
        raise HTTPException(status_code=500, detail=f"Error generando métricas: {str(e)}")

# Middleware de autenticación simple (en producción usar JWT real)
@water_router.middleware("http")
async def water_api_middleware(request, call_next):
    """Middleware básico para API de agua"""
    
    # Log de request
    logger.info(f"🌊 API Water Request: {request.method} {request.url.path}")
    
    response = await call_next(request)
    
    # Log de response
    logger.info(f"🌊 API Water Response: {response.status_code}")
    
    return response
