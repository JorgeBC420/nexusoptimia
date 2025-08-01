/*
 * NexusOptim IA - LoRaWAN Only Firmware
 * Specialized for cost-optimized sensors without BLE
 * 
 * Target: CH32V003F4U6 (minimal package)
 * Communication: LoRaWAN only (SX1262)
 * Power: Ultra-low consumption design
 * 
 * Copyright (c) 2025 OpenNexus
 * Licensed under MIT License
 */

#include <ch32v00x.h>
#include "FreeRTOS.h"
#include "task.h"
#include "queue.h"
#include "semphr.h"
#include "lorawan_handler.h"
#include "sensor_manager.h"
#include "power_management.h"

/* Task Priorities - Simplified for LoRaWAN-only */
#define LORAWAN_TASK_PRIORITY    (tskIDLE_PRIORITY + 2)
#define SENSOR_TASK_PRIORITY     (tskIDLE_PRIORITY + 1)
#define POWER_TASK_PRIORITY      (tskIDLE_PRIORITY + 1)

/* Task Stack Sizes - Optimized for minimal RAM */
#define LORAWAN_TASK_STACK_SIZE  192   // Reduced from 256
#define SENSOR_TASK_STACK_SIZE   96    // Reduced from 128
#define POWER_TASK_STACK_SIZE    64    // New power management task

/* Configuration for LoRaWAN-only operation */
typedef struct {
    uint8_t sector_id;        // Sector type
    uint8_t node_id;          // Node identifier
    uint32_t sampling_rate;   // Sampling interval (ms)
    uint8_t lora_sf;          // LoRa Spreading Factor
    uint8_t tx_power;         // Transmission power
    uint8_t low_power_mode;   // Deep sleep enable
} lorawan_only_config_t;

/* Default configuration for water/environment sensors */
lorawan_only_config_t device_config = {
    .sector_id = 2,           // Water sector
    .node_id = 0x01,
    .sampling_rate = 300000,  // 5 minutes (extended for battery life)
    .lora_sf = 10,            // SF10 for better range
    .tx_power = 14,           // 14dBm
    .low_power_mode = 1       // Enable deep sleep
};

/* Global Variables */
QueueHandle_t xSensorDataQueue;
SemaphoreHandle_t xI2CMutex;
TaskHandle_t xLoRaWANTaskHandle;

/* Sensor data structure - simplified */
typedef struct {
    uint32_t timestamp;
    uint8_t sensor_type;
    float value;
    uint8_t battery_level;
    int8_t rssi;
    uint16_t sequence;        // Packet sequence number
} sensor_packet_t;

/*
 * LoRaWAN Task - Optimized for long battery life
 */
void vLoRaWANTask(void *pvParameters) {
    sensor_packet_t sensor_data;
    TickType_t xLastWakeTime = xTaskGetTickCount();
    uint16_t packet_sequence = 0;
    
    // Initialize LoRaWAN with retry mechanism
    uint8_t init_retries = 0;
    while (lorawan_init() != LORAWAN_SUCCESS && init_retries < 5) {
        vTaskDelay(pdMS_TO_TICKS(1000));
        init_retries++;
    }
    
    if (init_retries >= 5) {
        // Critical error - enter safe mode with LED indication
        while(1) {
            GPIO_WriteBit(GPIOA, GPIO_Pin_2, Bit_SET);   // Red LED
            vTaskDelay(pdMS_TO_TICKS(200));
            GPIO_WriteBit(GPIOA, GPIO_Pin_2, Bit_RESET);
            vTaskDelay(pdMS_TO_TICKS(5000));             // 5 second error cycle
        }
    }
    
    // Join network with extended timeout for challenging environments
    if (lorawan_join() != LORAWAN_SUCCESS) {
        // Join failed - reduce transmission frequency and continue trying
        device_config.sampling_rate = 900000;  // 15 minutes
        device_config.lora_sf = 12;            // Maximum range
    }
    
    while(1) {
        // Wait for sensor data
        if (xQueueReceive(xSensorDataQueue, &sensor_data, portMAX_DELAY) == pdTRUE) {
            
            // Build optimized payload (minimize airtime)
            uint8_t payload[11];  // Compact 11-byte payload
            payload[0] = device_config.sector_id;
            payload[1] = device_config.node_id;
            payload[2] = sensor_data.sensor_type;
            payload[3] = sensor_data.battery_level;
            
            // Float to fixed-point (16-bit) for smaller payload
            int16_t value_fixed = (int16_t)(sensor_data.value * 100);
            payload[4] = (value_fixed >> 8) & 0xFF;
            payload[5] = value_fixed & 0xFF;
            
            // Timestamp (32-bit Unix timestamp)
            payload[6] = (sensor_data.timestamp >> 24) & 0xFF;
            payload[7] = (sensor_data.timestamp >> 16) & 0xFF;
            payload[8] = (sensor_data.timestamp >> 8) & 0xFF;
            payload[9] = sensor_data.timestamp & 0xFF;
            
            // Sequence number
            payload[10] = packet_sequence & 0xFF;
            
            // Send data with adaptive retry
            uint8_t retry_count = 0;
            while (retry_count < 3) {
                if (lorawan_send(payload, 11, 1) == LORAWAN_SUCCESS) {
                    // Success - quick green LED pulse
                    GPIO_WriteBit(GPIOA, GPIO_Pin_1, Bit_SET);
                    vTaskDelay(pdMS_TO_TICKS(50));
                    GPIO_WriteBit(GPIOA, GPIO_Pin_1, Bit_RESET);
                    packet_sequence++;
                    break;
                } else {
                    retry_count++;
                    vTaskDelay(pdMS_TO_TICKS(5000));  // Wait 5s before retry
                }
            }
            
            if (retry_count >= 3) {
                // Transmission failed - enter extended sleep mode
                device_config.sampling_rate = 1800000;  // 30 minutes
            }
        }
        
        // Enter deep sleep mode between transmissions
        if (device_config.low_power_mode) {
            lorawan_sleep();
            power_enter_deep_sleep(device_config.sampling_rate - 1000);
            lorawan_wakeup();
        } else {
            vTaskDelayUntil(&xLastWakeTime, pdMS_TO_TICKS(device_config.sampling_rate));
        }
    }
}

/*
 * Sensor Task - Simplified for single sensor type
 */
void vSensorTask(void *pvParameters) {
    sensor_packet_t sensor_data;
    TickType_t xLastWakeTime = xTaskGetTickCount();
    
    // Initialize sensors based on sector
    sensor_init();
    
    // Sensor warm-up period
    vTaskDelay(pdMS_TO_TICKS(2000));
    
    while(1) {
        // Power up sensor subsystem
        power_enable_sensors(true);
        vTaskDelay(pdMS_TO_TICKS(100));  // Sensor stabilization time
        
        // Take I2C mutex
        if (xSemaphoreTake(xI2CMutex, pdMS_TO_TICKS(1000)) == pdTRUE) {
            
            // Read sensor based on sector configuration
            switch(device_config.sector_id) {
                case 1: // Energy Sector - Electrical measurements
                    sensor_data.value = sensor_read_voltage();
                    sensor_data.sensor_type = 0x01;
                    break;
                    
                case 2: // Water Sector - Pressure monitoring
                    sensor_data.value = sensor_read_pressure();
                    sensor_data.sensor_type = 0x03;
                    
                    // Additional water quality check
                    if (sensor_data.value > 10.0) {  // High pressure alert
                        device_config.sampling_rate = 60000;  // 1 minute sampling
                    }
                    break;
                    
                case 3: // Environment Sector - Air quality
                    sensor_data.value = sensor_read_co2();
                    sensor_data.sensor_type = 0x07;
                    break;
                    
                case 4: // Agriculture Sector - Soil monitoring
                    sensor_data.value = sensor_read_soil_moisture();
                    sensor_data.sensor_type = 0x09;
                    break;
                    
                default:
                    sensor_data.value = sensor_read_generic();
                    sensor_data.sensor_type = 0xFF;
                    break;
            }
            
            // Common sensor data
            sensor_data.timestamp = xTaskGetTickCount() / 1000;  // Simple timestamp
            sensor_data.battery_level = power_get_battery_level();
            sensor_data.rssi = lorawan_get_rssi();
            
            // Release I2C mutex
            xSemaphoreGive(xI2CMutex);
            
            // Send to LoRaWAN queue
            if (xQueueSend(xSensorDataQueue, &sensor_data, pdMS_TO_TICKS(100)) != pdTRUE) {
                // Queue full - possible system issue
                // Reset queue to prevent deadlock
                xQueueReset(xSensorDataQueue);
            }
        }
        
        // Power down sensors to save energy
        power_enable_sensors(false);
        
        // Extended sleep between readings
        vTaskDelayUntil(&xLastWakeTime, pdMS_TO_TICKS(device_config.sampling_rate));
    }
}

/*
 * Power Management Task - Battery optimization
 */
void vPowerTask(void *pvParameters) {
    TickType_t xLastWakeTime = xTaskGetTickCount();
    
    while(1) {
        uint8_t battery_level = power_get_battery_level();
        
        // Adaptive power management based on battery level
        if (battery_level < 20) {
            // Critical battery - emergency mode
            device_config.sampling_rate = 3600000;    // 1 hour
            device_config.lora_sf = 12;               // Maximum range
            device_config.tx_power = 10;              // Reduced power
            
        } else if (battery_level < 50) {
            // Low battery - conservation mode
            device_config.sampling_rate = 1800000;    // 30 minutes
            device_config.lora_sf = 11;               // Extended range
            device_config.tx_power = 12;              // Reduced power
            
        } else {
            // Normal operation
            device_config.sampling_rate = 300000;     // 5 minutes
            device_config.lora_sf = 10;               // Balanced range/power
            device_config.tx_power = 14;              // Full power
        }
        
        // Check every 10 minutes
        vTaskDelayUntil(&xLastWakeTime, pdMS_TO_TICKS(600000));
    }
}

/*
 * System Initialization - Minimal configuration
 */
void system_init(void) {
    // Enable essential peripheral clocks only
    RCC_APB2PeriphClockCmd(RCC_APB2Periph_GPIOA | RCC_APB2Periph_GPIOC, ENABLE);
    RCC_APB1PeriphClockCmd(RCC_APB1Periph_I2C1, ENABLE);
    
    // Configure GPIO for LEDs (minimal - only status LEDs)
    GPIO_InitTypeDef GPIO_InitStructure = {0};
    GPIO_InitStructure.GPIO_Pin = GPIO_Pin_1 | GPIO_Pin_2;  // Green and Red LEDs
    GPIO_InitStructure.GPIO_Mode = GPIO_Mode_Out_PP;
    GPIO_InitStructure.GPIO_Speed = GPIO_Speed_2MHz;        // Low speed for power saving
    GPIO_Init(GPIOA, &GPIO_InitStructure);
    
    // Configure I2C for sensors (reduced speed for power saving)
    I2C_InitTypeDef I2C_InitStructure = {0};
    I2C_InitStructure.I2C_ClockSpeed = 50000;               // 50kHz (reduced from 100kHz)
    I2C_InitStructure.I2C_Mode = I2C_Mode_I2C;
    I2C_InitStructure.I2C_DutyCycle = I2C_DutyCycle_2;
    I2C_InitStructure.I2C_OwnAddress1 = 0x00;
    I2C_InitStructure.I2C_Ack = I2C_Ack_Enable;
    I2C_InitStructure.I2C_AcknowledgedAddress = I2C_AcknowledgedAddress_7bit;
    I2C_Init(I2C1, &I2C_InitStructure);
    I2C_Cmd(I2C1, ENABLE);
    
    // Power management initialization
    power_init();
    power_set_mode(POWER_MODE_ULTRA_LOW);
}

/*
 * Main Function - LoRaWAN-only variant
 */
int main(void) {
    // System initialization
    SystemInit();
    system_init();
    
    // Create FreeRTOS objects (minimal set)
    xSensorDataQueue = xQueueCreate(5, sizeof(sensor_packet_t));  // Smaller queue
    xI2CMutex = xSemaphoreCreateMutex();
    
    if (xSensorDataQueue == NULL || xI2CMutex == NULL) {
        // Error indication and halt
        GPIO_WriteBit(GPIOA, GPIO_Pin_2, Bit_SET);  // Red LED ON
        while(1);
    }
    
    // Create tasks (no BLE task)
    xTaskCreate(vLoRaWANTask, "LoRa", LORAWAN_TASK_STACK_SIZE, NULL, LORAWAN_TASK_PRIORITY, &xLoRaWANTaskHandle);
    xTaskCreate(vSensorTask, "Sensor", SENSOR_TASK_STACK_SIZE, NULL, SENSOR_TASK_PRIORITY, NULL);
    xTaskCreate(vPowerTask, "Power", POWER_TASK_STACK_SIZE, NULL, POWER_TASK_PRIORITY, NULL);
    
    // Start FreeRTOS scheduler
    vTaskStartScheduler();
    
    // Should never reach here
    while(1);
}

/*
 * FreeRTOS Hook Functions - Power optimized
 */
void vApplicationStackOverflowHook(TaskHandle_t xTask, char *pcTaskName) {
    // Stack overflow - minimal error indication
    GPIO_WriteBit(GPIOA, GPIO_Pin_2, Bit_SET);
    power_enter_deep_sleep(60000);  // Sleep 1 minute, then reset
    NVIC_SystemReset();
}

void vApplicationMallocFailedHook(void) {
    // Memory allocation failed - reset system
    NVIC_SystemReset();
}

/*
 * Idle Hook - Enter low power mode
 */
void vApplicationIdleHook(void) {
    // Enter lowest power mode during idle
    __WFI();  // Wait for interrupt
}
