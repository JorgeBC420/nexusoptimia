/*
 * NexusOptim IA - RISC-V Main Firmware
 * Multi-Sector IoT Platform for Smart Cities
 * 
 * MCU: CH32V003J4M6 (RISC-V 48MHz)
 * Communication: LoRaWAN + BLE 5.3
 * OS: FreeRTOS 10.5.1
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
#include "ble_handler.h"
#include "sensor_manager.h"
#include "power_management.h"

/* Task Priorities */
#define LORAWAN_TASK_PRIORITY    (tskIDLE_PRIORITY + 3)
#define BLE_TASK_PRIORITY        (tskIDLE_PRIORITY + 2)
#define SENSOR_TASK_PRIORITY     (tskIDLE_PRIORITY + 1)
#define LED_TASK_PRIORITY        (tskIDLE_PRIORITY + 1)

/* Task Stack Sizes (optimized for RISC-V) */
#define LORAWAN_TASK_STACK_SIZE  256
#define BLE_TASK_STACK_SIZE      128
#define SENSOR_TASK_STACK_SIZE   128
#define LED_TASK_STACK_SIZE      64

/* Global Variables */
QueueHandle_t xSensorDataQueue;
SemaphoreHandle_t xI2CMutex;
TaskHandle_t xLoRaWANTaskHandle;
TaskHandle_t xBLETaskHandle;

/* Hardware Configuration */
typedef struct {
    uint8_t sector_id;        // 1=Energy, 2=Water, 3=Airport, etc.
    uint8_t node_id;          // Unique node identifier
    uint32_t sampling_rate;   // Sensor sampling rate (ms)
    uint8_t lora_sf;          // LoRa Spreading Factor
    uint8_t ble_enabled;      // BLE functionality enable
} nexus_config_t;

nexus_config_t nexus_config = {
    .sector_id = 1,           // Default: Energy sector
    .node_id = 0x01,
    .sampling_rate = 30000,   // 30 seconds
    .lora_sf = 9,             // SF9 for Costa Rica 915MHz
    .ble_enabled = 1
};

/* Sensor Data Structure */
typedef struct {
    uint32_t timestamp;
    uint8_t sensor_type;
    float value;
    uint8_t battery_level;
    int8_t rssi;
} sensor_data_t;

/*
 * LoRaWAN Task
 * Handles long-range communication to Helium Network
 */
void vLoRaWANTask(void *pvParameters) {
    sensor_data_t sensor_data;
    TickType_t xLastWakeTime = xTaskGetTickCount();
    
    // Initialize LoRaWAN stack
    if (lorawan_init() != LORAWAN_SUCCESS) {
        // Error: Red LED blink pattern
        while(1) {
            GPIO_WriteBit(GPIOA, GPIO_Pin_2, Bit_SET);   // Red LED ON
            vTaskDelay(pdMS_TO_TICKS(100));
            GPIO_WriteBit(GPIOA, GPIO_Pin_2, Bit_RESET); // Red LED OFF
            vTaskDelay(pdMS_TO_TICKS(100));
        }
    }
    
    // Join network (OTAA)
    lorawan_join();
    
    while(1) {
        // Wait for sensor data
        if (xQueueReceive(xSensorDataQueue, &sensor_data, portMAX_DELAY) == pdTRUE) {
            
            // Prepare LoRaWAN payload
            uint8_t payload[12];
            payload[0] = nexus_config.sector_id;
            payload[1] = nexus_config.node_id;
            payload[2] = sensor_data.sensor_type;
            payload[3] = sensor_data.battery_level;
            
            // Float to bytes (little endian)
            memcpy(&payload[4], &sensor_data.value, 4);
            memcpy(&payload[8], &sensor_data.timestamp, 4);
            
            // Send data
            if (lorawan_send(payload, 12, 1) == LORAWAN_SUCCESS) {
                // Success: Green LED pulse
                GPIO_WriteBit(GPIOA, GPIO_Pin_1, Bit_SET);   // Green LED ON
                vTaskDelay(pdMS_TO_TICKS(50));
                GPIO_WriteBit(GPIOA, GPIO_Pin_1, Bit_RESET); // Green LED OFF
            }
        }
        
        // Task delay for power optimization
        vTaskDelayUntil(&xLastWakeTime, pdMS_TO_TICKS(1000));
    }
}

/*
 * BLE Task
 * Handles local communication for maintenance and configuration
 */
void vBLETask(void *pvParameters) {
    TickType_t xLastWakeTime = xTaskGetTickCount();
    
    if (nexus_config.ble_enabled) {
        // Initialize BLE stack
        ble_init();
        ble_advertising_start();
    }
    
    while(1) {
        if (nexus_config.ble_enabled) {
            // Handle BLE events
            ble_process();
            
            // Check for configuration updates via BLE
            if (ble_config_updated()) {
                // Update local configuration
                ble_get_config(&nexus_config);
            }
        }
        
        vTaskDelayUntil(&xLastWakeTime, pdMS_TO_TICKS(100));
    }
}

/*
 * Sensor Task
 * Manages all sensor readings and data processing
 */
void vSensorTask(void *pvParameters) {
    sensor_data_t sensor_data;
    TickType_t xLastWakeTime = xTaskGetTickCount();
    
    // Initialize sensors
    sensor_init();
    
    while(1) {
        // Take I2C mutex
        if (xSemaphoreTake(xI2CMutex, pdMS_TO_TICKS(100)) == pdTRUE) {
            
            // Read sensors based on sector configuration
            switch(nexus_config.sector_id) {
                case 1: // Energy Sector
                    sensor_data.value = sensor_read_voltage();
                    sensor_data.sensor_type = 0x01;
                    break;
                    
                case 2: // Water Sector
                    sensor_data.value = sensor_read_pressure();
                    sensor_data.sensor_type = 0x02;
                    break;
                    
                case 3: // Airport Sector
                    sensor_data.value = sensor_read_temperature();
                    sensor_data.sensor_type = 0x03;
                    break;
                    
                default:
                    sensor_data.value = sensor_read_generic();
                    sensor_data.sensor_type = 0xFF;
                    break;
            }
            
            // Common sensor data
            sensor_data.timestamp = xTaskGetTickCount();
            sensor_data.battery_level = power_get_battery_level();
            sensor_data.rssi = lorawan_get_rssi();
            
            // Release I2C mutex
            xSemaphoreGive(xI2CMutex);
            
            // Send to LoRaWAN queue
            xQueueSend(xSensorDataQueue, &sensor_data, 0);
        }
        
        // Sleep based on configured sampling rate
        vTaskDelayUntil(&xLastWakeTime, pdMS_TO_TICKS(nexus_config.sampling_rate));
    }
}

/*
 * LED Status Task
 * Provides visual feedback for system status
 */
void vLEDTask(void *pvParameters) {
    TickType_t xLastWakeTime = xTaskGetTickCount();
    uint8_t heartbeat_counter = 0;
    
    while(1) {
        // Heartbeat pattern every 5 seconds
        if (++heartbeat_counter >= 50) {
            heartbeat_counter = 0;
            
            // Quick double blink on green LED
            GPIO_WriteBit(GPIOA, GPIO_Pin_1, Bit_SET);
            vTaskDelay(pdMS_TO_TICKS(50));
            GPIO_WriteBit(GPIOA, GPIO_Pin_1, Bit_RESET);
            vTaskDelay(pdMS_TO_TICKS(50));
            GPIO_WriteBit(GPIOA, GPIO_Pin_1, Bit_SET);
            vTaskDelay(pdMS_TO_TICKS(50));
            GPIO_WriteBit(GPIOA, GPIO_Pin_1, Bit_RESET);
        }
        
        vTaskDelayUntil(&xLastWakeTime, pdMS_TO_TICKS(100));
    }
}

/*
 * System Initialization
 */
void system_init(void) {
    // Enable peripheral clocks
    RCC_APB2PeriphClockCmd(RCC_APB2Periph_GPIOA | RCC_APB2Periph_GPIOC, ENABLE);
    RCC_APB1PeriphClockCmd(RCC_APB1Periph_I2C1, ENABLE);
    
    // Configure GPIO for LEDs
    GPIO_InitTypeDef GPIO_InitStructure = {0};
    GPIO_InitStructure.GPIO_Pin = GPIO_Pin_1 | GPIO_Pin_2;  // Green and Red LEDs
    GPIO_InitStructure.GPIO_Mode = GPIO_Mode_Out_PP;
    GPIO_InitStructure.GPIO_Speed = GPIO_Speed_2MHz;
    GPIO_Init(GPIOA, &GPIO_InitStructure);
    
    // Configure I2C for sensors
    I2C_InitTypeDef I2C_InitStructure = {0};
    I2C_InitStructure.I2C_ClockSpeed = 100000;              // 100kHz
    I2C_InitStructure.I2C_Mode = I2C_Mode_I2C;
    I2C_InitStructure.I2C_DutyCycle = I2C_DutyCycle_16_9;
    I2C_InitStructure.I2C_OwnAddress1 = 0x00;
    I2C_InitStructure.I2C_Ack = I2C_Ack_Enable;
    I2C_InitStructure.I2C_AcknowledgedAddress = I2C_AcknowledgedAddress_7bit;
    I2C_Init(I2C1, &I2C_InitStructure);
    I2C_Cmd(I2C1, ENABLE);
    
    // Power management initialization
    power_init();
}

/*
 * Main Function
 */
int main(void) {
    // System initialization
    SystemInit();
    system_init();
    
    // Create FreeRTOS objects
    xSensorDataQueue = xQueueCreate(10, sizeof(sensor_data_t));
    xI2CMutex = xSemaphoreCreateMutex();
    
    if (xSensorDataQueue == NULL || xI2CMutex == NULL) {
        // Error: Unable to create FreeRTOS objects
        while(1);
    }
    
    // Create tasks
    xTaskCreate(vLoRaWANTask, "LoRaWAN", LORAWAN_TASK_STACK_SIZE, NULL, LORAWAN_TASK_PRIORITY, &xLoRaWANTaskHandle);
    xTaskCreate(vBLETask, "BLE", BLE_TASK_STACK_SIZE, NULL, BLE_TASK_PRIORITY, &xBLETaskHandle);
    xTaskCreate(vSensorTask, "Sensor", SENSOR_TASK_STACK_SIZE, NULL, SENSOR_TASK_PRIORITY, NULL);
    xTaskCreate(vLEDTask, "LED", LED_TASK_STACK_SIZE, NULL, LED_TASK_PRIORITY, NULL);
    
    // Start FreeRTOS scheduler
    vTaskStartScheduler();
    
    // Should never reach here
    while(1);
}

/*
 * FreeRTOS Hook Functions
 */
void vApplicationStackOverflowHook(TaskHandle_t xTask, char *pcTaskName) {
    // Stack overflow detected - flash red LED rapidly
    while(1) {
        GPIO_WriteBit(GPIOA, GPIO_Pin_2, Bit_SET);
        for(volatile int i = 0; i < 10000; i++);
        GPIO_WriteBit(GPIOA, GPIO_Pin_2, Bit_RESET);
        for(volatile int i = 0; i < 10000; i++);
    }
}

void vApplicationMallocFailedHook(void) {
    // Memory allocation failed - solid red LED
    GPIO_WriteBit(GPIOA, GPIO_Pin_2, Bit_SET);
    while(1);
}

/*
 * Hard Fault Handler (RISC-V specific)
 */
void HardFault_Handler(void) __attribute__((interrupt("WCH-Interrupt-fast")));
void HardFault_Handler(void) {
    // Hard fault - alternating red/green LEDs
    while(1) {
        GPIO_WriteBit(GPIOA, GPIO_Pin_2, Bit_SET);   // Red ON
        GPIO_WriteBit(GPIOA, GPIO_Pin_1, Bit_RESET); // Green OFF
        for(volatile int i = 0; i < 50000; i++);
        
        GPIO_WriteBit(GPIOA, GPIO_Pin_2, Bit_RESET); // Red OFF
        GPIO_WriteBit(GPIOA, GPIO_Pin_1, Bit_SET);   // Green ON
        for(volatile int i = 0; i < 50000; i++);
    }
}
