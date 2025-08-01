/*
 * NexusOptim IA - Water Sensors Firmware
 * Specialized for Water Infrastructure Monitoring
 * 
 * Features:
 * - High-precision pressure monitoring
 * - Flow rate measurement
 * - pH and water quality analysis
 * - Leak detection algorithms
 * - Waterproof design optimization
 * 
 * Target: CH32V003F4U6 + waterproof sensors
 * Copyright (c) 2025 OpenNexus
 * Licensed under MIT License
 */

#include <ch32v00x.h>
#include "FreeRTOS.h"
#include "task.h"
#include "queue.h"
#include "semphr.h"
#include "lorawan_handler.h"
#include "water_sensors.h"
#include "power_management.h"

/* Task Priorities */
#define LORAWAN_TASK_PRIORITY    (tskIDLE_PRIORITY + 2)
#define WATER_TASK_PRIORITY      (tskIDLE_PRIORITY + 2)
#define LEAK_DETECT_PRIORITY     (tskIDLE_PRIORITY + 3)  // High priority for leaks
#define MAINTENANCE_PRIORITY     (tskIDLE_PRIORITY + 1)

/* Task Stack Sizes */
#define LORAWAN_TASK_STACK_SIZE  192
#define WATER_TASK_STACK_SIZE    160
#define LEAK_DETECT_STACK_SIZE   96
#define MAINTENANCE_STACK_SIZE   80

/* Water System Configuration */
typedef struct {
    uint8_t sensor_type;          // 0=Pressure, 1=Flow, 2=pH, 3=Multi
    float pressure_range;         // Maximum pressure (bar)
    float flow_range;             // Maximum flow (L/min)
    float ph_min;                 // Minimum pH value
    float ph_max;                 // Maximum pH value
    uint32_t measurement_interval; // Normal measurement interval (ms)
    uint32_t leak_check_interval; // Leak detection interval (ms)
    float leak_threshold;         // Pressure drop threshold for leak detection
    uint8_t water_quality_mode;   // Water quality monitoring enable
} water_config_t;

water_config_t water_config = {
    .sensor_type = 3,             // Multi-sensor
    .pressure_range = 10.0,       // 10 bar maximum
    .flow_range = 100.0,          // 100 L/min maximum
    .ph_min = 6.5,                // Minimum acceptable pH
    .ph_max = 8.5,                // Maximum acceptable pH
    .measurement_interval = 60000, // 1 minute normal sampling
    .leak_check_interval = 10000, // 10 seconds leak detection
    .leak_threshold = 0.5,        // 0.5 bar pressure drop indicates leak
    .water_quality_mode = 1       // Enable water quality monitoring
};

/* Water Measurement Data */
typedef struct {
    uint32_t timestamp;
    float pressure;               // Water pressure (bar)
    float flow_rate;              // Flow rate (L/min)
    float ph_value;               // pH value
    float temperature;            // Water temperature (°C)
    float turbidity;              // Water turbidity (NTU)
    uint8_t leak_detected;        // Leak detection flag
    uint8_t water_quality_grade;  // Water quality grade (A-F)
    float total_flow;             // Cumulative flow (L)
    uint8_t sensor_status;        // Sensor health status
} water_data_t;

/* Water Quality Alerts */
#define WATER_ALERT_LOW_PRESSURE    (1 << 0)
#define WATER_ALERT_HIGH_PRESSURE   (1 << 1)
#define WATER_ALERT_NO_FLOW        (1 << 2)
#define WATER_ALERT_HIGH_FLOW      (1 << 3)
#define WATER_ALERT_LOW_PH         (1 << 4)
#define WATER_ALERT_HIGH_PH        (1 << 5)
#define WATER_ALERT_LEAK_DETECTED  (1 << 6)
#define WATER_ALERT_SENSOR_FAULT   (1 << 7)

/* Global Variables */
QueueHandle_t xWaterDataQueue;
QueueHandle_t xLeakAlertQueue;
SemaphoreHandle_t xI2CMutex;
TaskHandle_t xWaterTaskHandle;
TaskHandle_t xLeakTaskHandle;

/* Leak detection variables */
static float pressure_history[10];  // Pressure history for leak detection
static uint8_t pressure_index = 0;
static float cumulative_flow = 0.0;
static uint32_t last_flow_timestamp = 0;

/*
 * Leak Detection Task - High priority monitoring
 */
void vLeakDetectionTask(void *pvParameters) {
    water_data_t water_data;
    uint8_t leak_alert = 0;
    TickType_t xLastWakeTime = xTaskGetTickCount();
    
    while(1) {
        // Take I2C mutex for sensor access
        if (xSemaphoreTake(xI2CMutex, pdMS_TO_TICKS(100)) == pdTRUE) {
            
            // Read pressure sensor for leak detection
            float current_pressure = water_read_pressure();
            
            // Store pressure in circular buffer
            pressure_history[pressure_index] = current_pressure;
            pressure_index = (pressure_index + 1) % 10;
            
            // Calculate pressure trend (last 3 readings)
            float pressure_trend = 0.0;
            if (pressure_index >= 3) {
                uint8_t idx1 = (pressure_index - 1 + 10) % 10;
                uint8_t idx2 = (pressure_index - 2 + 10) % 10;
                uint8_t idx3 = (pressure_index - 3 + 10) % 10;
                
                pressure_trend = (pressure_history[idx1] - pressure_history[idx3]) / 2.0;
            }
            
            xSemaphoreGive(xI2CMutex);
            
            // Leak detection algorithm
            if (pressure_trend < -water_config.leak_threshold) {
                // Significant pressure drop detected
                leak_alert |= WATER_ALERT_LEAK_DETECTED;
                
                // Immediate emergency transmission
                uint8_t emergency_payload[10];
                emergency_payload[0] = 0xFF;  // Emergency flag
                emergency_payload[1] = 0x02;  // Water sector
                emergency_payload[2] = WATER_ALERT_LEAK_DETECTED;
                emergency_payload[3] = (uint8_t)(current_pressure * 10);  // Current pressure
                
                // Pressure trend (signed 8-bit)
                int8_t trend_encoded = (int8_t)(pressure_trend * 10);
                emergency_payload[4] = (uint8_t)trend_encoded;
                
                // Location identifier
                emergency_payload[5] = 0x01;  // Node ID
                
                // Timestamp
                uint32_t timestamp = xTaskGetTickCount();
                emergency_payload[6] = (timestamp >> 24) & 0xFF;
                emergency_payload[7] = (timestamp >> 16) & 0xFF;
                emergency_payload[8] = (timestamp >> 8) & 0xFF;
                emergency_payload[9] = timestamp & 0xFF;
                
                // Send emergency alert
                lorawan_send(emergency_payload, 10, 98);  // Emergency port for water
                
                // Visual alert - rapid red LED flashing
                for (int i = 0; i < 20; i++) {
                    GPIO_WriteBit(GPIOA, GPIO_Pin_2, Bit_SET);
                    vTaskDelay(pdMS_TO_TICKS(50));
                    GPIO_WriteBit(GPIOA, GPIO_Pin_2, Bit_RESET);
                    vTaskDelay(pdMS_TO_TICKS(50));
                }
                
                // Increase monitoring frequency
                water_config.leak_check_interval = 5000;  // 5 seconds
                water_config.measurement_interval = 30000; // 30 seconds
            }
            
            // Send leak alert to main task
            if (leak_alert != 0) {
                xQueueSend(xLeakAlertQueue, &leak_alert, 0);
                leak_alert = 0;  // Reset for next cycle
            }
        }
        
        vTaskDelayUntil(&xLastWakeTime, pdMS_TO_TICKS(water_config.leak_check_interval));
    }
}

/*
 * Water Monitoring Task
 */
void vWaterTask(void *pvParameters) {
    water_data_t water_data;
    TickType_t xLastWakeTime = xTaskGetTickCount();
    
    // Initialize water sensors
    water_sensors_init();
    water_calibration_load();
    
    // Initialize flow accumulator
    cumulative_flow = 0.0;
    last_flow_timestamp = xTaskGetTickCount();
    
    while(1) {
        uint8_t sensor_alerts = 0;
        
        // Take I2C mutex for sensor readings
        if (xSemaphoreTake(xI2CMutex, pdMS_TO_TICKS(200)) == pdTRUE) {
            
            // Read all water sensors
            water_data.pressure = water_read_pressure();
            water_data.flow_rate = water_read_flow();
            water_data.ph_value = water_read_ph();
            water_data.temperature = water_read_temperature();
            
            if (water_config.water_quality_mode) {
                water_data.turbidity = water_read_turbidity();
            } else {
                water_data.turbidity = 0.0;
            }
            
            water_data.timestamp = xTaskGetTickCount() / 1000;
            
            xSemaphoreGive(xI2CMutex);
            
            // Calculate flow accumulation
            uint32_t current_time = xTaskGetTickCount();
            float time_diff = (current_time - last_flow_timestamp) / 1000.0;  // seconds
            cumulative_flow += water_data.flow_rate * (time_diff / 60.0);     // L/min to L
            water_data.total_flow = cumulative_flow;
            last_flow_timestamp = current_time;
            
            // Water quality analysis
            sensor_alerts = 0;
            
            // Pressure checks
            if (water_data.pressure < 1.0) {
                sensor_alerts |= WATER_ALERT_LOW_PRESSURE;
            }
            if (water_data.pressure > water_config.pressure_range * 0.9) {
                sensor_alerts |= WATER_ALERT_HIGH_PRESSURE;
            }
            
            // Flow checks
            if (water_data.flow_rate < 0.1 && water_data.pressure > 2.0) {
                sensor_alerts |= WATER_ALERT_NO_FLOW;  // Pressure but no flow = blockage
            }
            if (water_data.flow_rate > water_config.flow_range * 0.8) {
                sensor_alerts |= WATER_ALERT_HIGH_FLOW;
            }
            
            // pH checks
            if (water_data.ph_value < water_config.ph_min) {
                sensor_alerts |= WATER_ALERT_LOW_PH;
            }
            if (water_data.ph_value > water_config.ph_max) {
                sensor_alerts |= WATER_ALERT_HIGH_PH;
            }
            
            // Water quality grading
            water_data.water_quality_grade = calculate_water_quality_grade(&water_data);
            
            // Sensor health check
            water_data.sensor_status = water_check_sensor_health();
            if (water_data.sensor_status != 0) {
                sensor_alerts |= WATER_ALERT_SENSOR_FAULT;
            }
            
            // Check for leak alerts from leak detection task
            uint8_t leak_alert;
            if (xQueueReceive(xLeakAlertQueue, &leak_alert, 0) == pdTRUE) {
                sensor_alerts |= leak_alert;
                water_data.leak_detected = 1;
            } else {
                water_data.leak_detected = 0;
            }
            
            // Send data to LoRaWAN task
            xQueueSend(xWaterDataQueue, &water_data, pdMS_TO_TICKS(100));
            
            // Adaptive sampling based on conditions
            if (sensor_alerts != 0) {
                // Increase sampling frequency for alerts
                water_config.measurement_interval = 30000;  // 30 seconds
            } else if (water_data.flow_rate < 0.1) {
                // Reduce sampling for no-flow conditions
                water_config.measurement_interval = 300000; // 5 minutes
            } else {
                // Normal sampling
                water_config.measurement_interval = 60000;  // 1 minute
            }
        }
        
        vTaskDelayUntil(&xLastWakeTime, pdMS_TO_TICKS(water_config.measurement_interval));
    }
}

/*
 * LoRaWAN Task - Water data transmission
 */
void vLoRaWANTask(void *pvParameters) {
    water_data_t water_data;
    TickType_t xLastWakeTime = xTaskGetTickCount();
    
    // Initialize LoRaWAN
    if (lorawan_init() != LORAWAN_SUCCESS) {
        while(1) {
            GPIO_WriteBit(GPIOA, GPIO_Pin_2, Bit_SET);
            vTaskDelay(pdMS_TO_TICKS(1000));
            GPIO_WriteBit(GPIOA, GPIO_Pin_2, Bit_RESET);
            vTaskDelay(pdMS_TO_TICKS(1000));
        }
    }
    
    lorawan_join();
    
    while(1) {
        if (xQueueReceive(xWaterDataQueue, &water_data, portMAX_DELAY) == pdTRUE) {
            
            // Build water monitoring payload (18 bytes)
            uint8_t payload[18];
            uint8_t idx = 0;
            
            payload[idx++] = 0x02;  // Water sector
            payload[idx++] = 0x01;  // Node ID
            payload[idx++] = 0x20;  // Water measurements type
            payload[idx++] = water_data.leak_detected;
            
            // Pressure (16-bit, 0.01 bar resolution)
            uint16_t pressure_encoded = (uint16_t)(water_data.pressure * 100);
            payload[idx++] = (pressure_encoded >> 8) & 0xFF;
            payload[idx++] = pressure_encoded & 0xFF;
            
            // Flow rate (16-bit, 0.1 L/min resolution)
            uint16_t flow_encoded = (uint16_t)(water_data.flow_rate * 10);
            payload[idx++] = (flow_encoded >> 8) & 0xFF;
            payload[idx++] = flow_encoded & 0xFF;
            
            // pH value (8-bit, 0.1 pH resolution, offset from pH 5.0)
            uint8_t ph_encoded = (uint8_t)((water_data.ph_value - 5.0) * 10);
            payload[idx++] = ph_encoded;
            
            // Temperature (8-bit, 1°C resolution, offset from -20°C)
            uint8_t temp_encoded = (uint8_t)(water_data.temperature + 20);
            payload[idx++] = temp_encoded;
            
            // Turbidity (8-bit, 0.5 NTU resolution)
            uint8_t turbidity_encoded = (uint8_t)(water_data.turbidity * 2);
            payload[idx++] = turbidity_encoded;
            
            // Water quality grade
            payload[idx++] = water_data.water_quality_grade;
            
            // Cumulative flow (32-bit, 1L resolution)
            uint32_t total_flow_encoded = (uint32_t)water_data.total_flow;
            payload[idx++] = (total_flow_encoded >> 24) & 0xFF;
            payload[idx++] = (total_flow_encoded >> 16) & 0xFF;
            payload[idx++] = (total_flow_encoded >> 8) & 0xFF;
            payload[idx++] = total_flow_encoded & 0xFF;
            
            // Battery level
            payload[idx++] = power_get_battery_level();
            
            // Sensor status
            payload[idx++] = water_data.sensor_status;
            
            // Send data
            if (lorawan_send(payload, idx, 20) == LORAWAN_SUCCESS) {  // Port 20 for water data
                // Success indication
                GPIO_WriteBit(GPIOA, GPIO_Pin_1, Bit_SET);   // Green LED
                vTaskDelay(pdMS_TO_TICKS(100));
                GPIO_WriteBit(GPIOA, GPIO_Pin_1, Bit_RESET);
            }
        }
        
        vTaskDelayUntil(&xLastWakeTime, pdMS_TO_TICKS(2000));
    }
}

/*
 * Maintenance Task - Sensor calibration and health monitoring
 */
void vMaintenanceTask(void *pvParameters) {
    TickType_t xLastWakeTime = xTaskGetTickCount();
    uint32_t maintenance_counter = 0;
    
    while(1) {
        maintenance_counter++;
        
        // Weekly maintenance cycle (assuming 1 hour task cycle)
        if (maintenance_counter % 168 == 0) {  // 168 hours = 1 week
            
            // Perform sensor calibration check
            if (xSemaphoreTake(xI2CMutex, pdMS_TO_TICKS(1000)) == pdTRUE) {
                
                // pH sensor maintenance (cleaning cycle)
                water_ph_maintenance();
                
                // Pressure sensor zero-point check
                water_pressure_zero_check();
                
                // Flow sensor cleaning pulse
                water_flow_cleaning_pulse();
                
                xSemaphoreGive(xI2CMutex);
            }
            
            // Reset flow accumulator weekly
            cumulative_flow = 0.0;
        }
        
        // Daily sensor health check
        if (maintenance_counter % 24 == 0) {  // 24 hours = 1 day
            water_sensor_health_check();
        }
        
        // Sleep for 1 hour
        vTaskDelayUntil(&xLastWakeTime, pdMS_TO_TICKS(3600000));
    }
}

/*
 * System Initialization - Water sensors optimized
 */
void system_init(void) {
    // Enable peripheral clocks
    RCC_APB2PeriphClockCmd(RCC_APB2Periph_GPIOA | RCC_APB2Periph_GPIOC, ENABLE);
    RCC_APB1PeriphClockCmd(RCC_APB1Periph_I2C1, ENABLE);
    
    // Configure GPIO for LEDs
    GPIO_InitTypeDef GPIO_InitStructure = {0};
    GPIO_InitStructure.GPIO_Pin = GPIO_Pin_1 | GPIO_Pin_2;
    GPIO_InitStructure.GPIO_Mode = GPIO_Mode_Out_PP;
    GPIO_InitStructure.GPIO_Speed = GPIO_Speed_2MHz;
    GPIO_Init(GPIOA, &GPIO_InitStructure);
    
    // Configure I2C for water sensors (standard speed for reliability)
    I2C_InitTypeDef I2C_InitStructure = {0};
    I2C_InitStructure.I2C_ClockSpeed = 100000;  // 100kHz
    I2C_InitStructure.I2C_Mode = I2C_Mode_I2C;
    I2C_InitStructure.I2C_DutyCycle = I2C_DutyCycle_2;
    I2C_InitStructure.I2C_OwnAddress1 = 0x00;
    I2C_InitStructure.I2C_Ack = I2C_Ack_Enable;
    I2C_InitStructure.I2C_AcknowledgedAddress = I2C_AcknowledgedAddress_7bit;
    I2C_Init(I2C1, &I2C_InitStructure);
    I2C_Cmd(I2C1, ENABLE);
    
    // Power management - waterproof mode
    power_init();
    power_set_mode(POWER_MODE_WATERPROOF);
}

/*
 * Main Function - Water sensors
 */
int main(void) {
    SystemInit();
    system_init();
    
    // Create FreeRTOS objects
    xWaterDataQueue = xQueueCreate(8, sizeof(water_data_t));
    xLeakAlertQueue = xQueueCreate(3, sizeof(uint8_t));
    xI2CMutex = xSemaphoreCreateMutex();
    
    if (xWaterDataQueue == NULL || xLeakAlertQueue == NULL || xI2CMutex == NULL) {
        while(1);
    }
    
    // Create tasks
    xTaskCreate(vWaterTask, "Water", WATER_TASK_STACK_SIZE, NULL, WATER_TASK_PRIORITY, &xWaterTaskHandle);
    xTaskCreate(vLoRaWANTask, "LoRa", LORAWAN_TASK_STACK_SIZE, NULL, LORAWAN_TASK_PRIORITY, NULL);
    xTaskCreate(vLeakDetectionTask, "Leak", LEAK_DETECT_STACK_SIZE, NULL, LEAK_DETECT_PRIORITY, &xLeakTaskHandle);
    xTaskCreate(vMaintenanceTask, "Maint", MAINTENANCE_STACK_SIZE, NULL, MAINTENANCE_PRIORITY, NULL);
    
    // Start FreeRTOS scheduler
    vTaskStartScheduler();
    
    while(1);
}

/*
 * Helper Functions
 */
uint8_t calculate_water_quality_grade(water_data_t *data) {
    uint8_t grade = 0;  // Start with A grade
    
    // pH grading
    if (data->ph_value < 6.8 || data->ph_value > 8.2) grade += 1;  // B
    if (data->ph_value < 6.5 || data->ph_value > 8.5) grade += 1;  // C
    
    // Turbidity grading
    if (data->turbidity > 1.0) grade += 1;   // B
    if (data->turbidity > 4.0) grade += 1;   // C
    if (data->turbidity > 10.0) grade += 1;  // D
    
    // Temperature grading (optimal 10-25°C)
    if (data->temperature < 5.0 || data->temperature > 30.0) grade += 1;
    
    // Pressure consistency (should be stable)
    // This would require pressure history analysis
    
    return (grade > 5) ? 5 : grade;  // F is worst grade
}
