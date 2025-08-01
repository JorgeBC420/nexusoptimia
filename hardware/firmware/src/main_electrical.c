/*
 * NexusOptim IA - Electrical Sensors Firmware
 * Specialized for Energy Sector Applications
 * 
 * Features:
 * - High-precision voltage/current measurement
 * - Power quality monitoring
 * - Electrical safety protection
 * - Real-time electrical parameter calculation
 * 
 * Target: CH32V003 + specialized analog front-end
 * Copyright (c) 2025 OpenNexus
 * Licensed under MIT License
 */

#include <ch32v00x.h>
#include "FreeRTOS.h"
#include "task.h"
#include "queue.h"
#include "semphr.h"
#include "lorawan_handler.h"
#include "electrical_sensors.h"
#include "power_management.h"
#include <math.h>

/* Task Priorities */
#define LORAWAN_TASK_PRIORITY      (tskIDLE_PRIORITY + 3)
#define ELECTRICAL_TASK_PRIORITY   (tskIDLE_PRIORITY + 2)
#define MONITORING_TASK_PRIORITY   (tskIDLE_PRIORITY + 1)
#define SAFETY_TASK_PRIORITY       (tskIDLE_PRIORITY + 3)  // Highest priority

/* Task Stack Sizes */
#define LORAWAN_TASK_STACK_SIZE    256
#define ELECTRICAL_TASK_STACK_SIZE 200  // Larger for math operations
#define MONITORING_TASK_STACK_SIZE 128
#define SAFETY_TASK_STACK_SIZE     96

/* Electrical Configuration */
typedef struct {
    uint8_t measurement_type;     // 0=Voltage, 1=Current, 2=Both, 3=Power Quality
    float voltage_range;          // Maximum voltage (V)
    float current_range;          // Maximum current (A)
    uint16_t sampling_frequency;  // ADC sampling rate (Hz)
    uint8_t calibration_mode;     // Calibration status
    float power_factor_limit;     // Power factor alarm threshold
    float thd_limit;              // Total Harmonic Distortion limit (%)
    uint32_t measurement_window;  // Measurement window (ms)
} electrical_config_t;

electrical_config_t electrical_config = {
    .measurement_type = 2,        // Both voltage and current
    .voltage_range = 250.0,       // 250V AC
    .current_range = 100.0,       // 100A
    .sampling_frequency = 2000,   // 2kHz sampling for 50Hz analysis
    .calibration_mode = 0,        // Not calibrated
    .power_factor_limit = 0.85,   // 85% power factor minimum
    .thd_limit = 5.0,             // 5% THD maximum
    .measurement_window = 1000    // 1 second measurement window
};

/* Electrical Measurement Data */
typedef struct {
    uint32_t timestamp;
    float voltage_rms;            // RMS Voltage (V)
    float current_rms;            // RMS Current (A)
    float power_active;           // Active Power (W)
    float power_reactive;         // Reactive Power (VAR)
    float power_apparent;         // Apparent Power (VA)
    float power_factor;           // Power Factor
    float frequency;              // Line Frequency (Hz)
    float thd_voltage;            // Voltage THD (%)
    float thd_current;            // Current THD (%)
    uint8_t safety_status;        // Safety flags
    uint8_t quality_grade;        // Power quality grade (A-F)
} electrical_data_t;

/* Safety Flags */
#define SAFETY_OVERVOLTAGE    (1 << 0)
#define SAFETY_UNDERVOLTAGE   (1 << 1)
#define SAFETY_OVERCURRENT    (1 << 2)
#define SAFETY_OVERPOWER      (1 << 3)
#define SAFETY_LOW_PF         (1 << 4)
#define SAFETY_HIGH_THD       (1 << 5)
#define SAFETY_FREQ_DEVIATION (1 << 6)
#define SAFETY_PHASE_IMBALANCE (1 << 7)

/* Global Variables */
QueueHandle_t xElectricalDataQueue;
QueueHandle_t xSafetyAlertQueue;
SemaphoreHandle_t xADCMutex;
TaskHandle_t xElectricalTaskHandle;
TaskHandle_t xSafetyTaskHandle;

/* ADC Buffer for high-speed sampling */
#define ADC_BUFFER_SIZE 4096
uint16_t adc_buffer_voltage[ADC_BUFFER_SIZE];
uint16_t adc_buffer_current[ADC_BUFFER_SIZE];
volatile uint16_t adc_buffer_index = 0;
volatile bool adc_buffer_ready = false;

/*
 * High-Priority Safety Monitoring Task
 */
void vSafetyTask(void *pvParameters) {
    electrical_data_t electrical_data;
    uint8_t safety_alert = 0;
    
    while(1) {
        // Check for safety alerts
        if (xQueueReceive(xSafetyAlertQueue, &safety_alert, pdMS_TO_TICKS(10)) == pdTRUE) {
            
            // Critical safety response
            if (safety_alert & (SAFETY_OVERVOLTAGE | SAFETY_OVERCURRENT | SAFETY_OVERPOWER)) {
                // EMERGENCY: Immediate alert transmission
                uint8_t emergency_payload[8];
                emergency_payload[0] = 0xFF;  // Emergency flag
                emergency_payload[1] = 0x01;  // Energy sector
                emergency_payload[2] = safety_alert;
                emergency_payload[3] = 0xAA;  // Emergency signature
                
                uint32_t timestamp = xTaskGetTickCount();
                emergency_payload[4] = (timestamp >> 24) & 0xFF;
                emergency_payload[5] = (timestamp >> 16) & 0xFF;
                emergency_payload[6] = (timestamp >> 8) & 0xFF;
                emergency_payload[7] = timestamp & 0xFF;
                
                // Send emergency packet immediately
                lorawan_send(emergency_payload, 8, 99);  // Emergency port
                
                // Visual/audible alarm
                for (int i = 0; i < 10; i++) {
                    GPIO_WriteBit(GPIOA, GPIO_Pin_2, Bit_SET);   // Red LED
                    vTaskDelay(pdMS_TO_TICKS(100));
                    GPIO_WriteBit(GPIOA, GPIO_Pin_2, Bit_RESET);
                    vTaskDelay(pdMS_TO_TICKS(100));
                }
            }
            
            // Log safety event
            // In production, would save to non-volatile memory
        }
        
        // Safety task runs every 100ms for fast response
        vTaskDelay(pdMS_TO_TICKS(100));
    }
}

/*
 * Electrical Measurement Task
 */
void vElectricalTask(void *pvParameters) {
    electrical_data_t electrical_data;
    TickType_t xLastWakeTime = xTaskGetTickCount();
    
    // Initialize electrical measurement system
    electrical_sensors_init();
    electrical_calibration_load();  // Load calibration from EEPROM
    
    while(1) {
        // Wait for ADC buffer to be ready
        while (!adc_buffer_ready) {
            vTaskDelay(pdMS_TO_TICKS(1));
        }
        
        // Take ADC mutex for exclusive access
        if (xSemaphoreTake(xADCMutex, pdMS_TO_TICKS(100)) == pdTRUE) {
            
            // Disable ADC interrupt during processing
            adc_buffer_ready = false;
            
            // Process voltage measurements
            electrical_data.voltage_rms = calculate_rms_voltage(adc_buffer_voltage, ADC_BUFFER_SIZE);
            electrical_data.thd_voltage = calculate_thd_voltage(adc_buffer_voltage, ADC_BUFFER_SIZE);
            
            // Process current measurements
            electrical_data.current_rms = calculate_rms_current(adc_buffer_current, ADC_BUFFER_SIZE);
            electrical_data.thd_current = calculate_thd_current(adc_buffer_current, ADC_BUFFER_SIZE);
            
            // Calculate power parameters
            electrical_data.power_active = calculate_active_power(adc_buffer_voltage, adc_buffer_current, ADC_BUFFER_SIZE);
            electrical_data.power_reactive = calculate_reactive_power(adc_buffer_voltage, adc_buffer_current, ADC_BUFFER_SIZE);
            electrical_data.power_apparent = sqrt(electrical_data.power_active * electrical_data.power_active + 
                                                 electrical_data.power_reactive * electrical_data.power_reactive);
            
            // Calculate power factor
            if (electrical_data.power_apparent > 0.1) {  // Avoid division by zero
                electrical_data.power_factor = electrical_data.power_active / electrical_data.power_apparent;
            } else {
                electrical_data.power_factor = 1.0;
            }
            
            // Calculate frequency
            electrical_data.frequency = calculate_frequency(adc_buffer_voltage, ADC_BUFFER_SIZE, electrical_config.sampling_frequency);
            
            // Timestamp
            electrical_data.timestamp = xTaskGetTickCount() / 1000;
            
            // Release ADC mutex
            xSemaphoreGive(xADCMutex);
            
            // Safety checks
            uint8_t safety_flags = 0;
            
            // Voltage safety checks
            if (electrical_data.voltage_rms > electrical_config.voltage_range * 1.1) {
                safety_flags |= SAFETY_OVERVOLTAGE;
            }
            if (electrical_data.voltage_rms < electrical_config.voltage_range * 0.85) {
                safety_flags |= SAFETY_UNDERVOLTAGE;
            }
            
            // Current safety checks
            if (electrical_data.current_rms > electrical_config.current_range * 0.9) {
                safety_flags |= SAFETY_OVERCURRENT;
            }
            
            // Power factor check
            if (electrical_data.power_factor < electrical_config.power_factor_limit) {
                safety_flags |= SAFETY_LOW_PF;
            }
            
            // THD checks
            if (electrical_data.thd_voltage > electrical_config.thd_limit || 
                electrical_data.thd_current > electrical_config.thd_limit) {
                safety_flags |= SAFETY_HIGH_THD;
            }
            
            // Frequency deviation check (50Hz ±2Hz)
            if (electrical_data.frequency < 48.0 || electrical_data.frequency > 52.0) {
                safety_flags |= SAFETY_FREQ_DEVIATION;
            }
            
            electrical_data.safety_status = safety_flags;
            
            // Calculate power quality grade
            electrical_data.quality_grade = calculate_power_quality_grade(&electrical_data);
            
            // Send safety alert if needed
            if (safety_flags != 0) {
                xQueueSend(xSafetyAlertQueue, &safety_flags, 0);
            }
            
            // Send data to LoRaWAN task
            xQueueSend(xElectricalDataQueue, &electrical_data, pdMS_TO_TICKS(10));
            
            // Re-enable ADC for next measurement cycle
            adc_buffer_index = 0;
            ADC_SoftwareStartConvCmd(ADC1, ENABLE);
        }
        
        // Wait for next measurement window
        vTaskDelayUntil(&xLastWakeTime, pdMS_TO_TICKS(electrical_config.measurement_window));
    }
}

/*
 * LoRaWAN Task - Electrical data transmission
 */
void vLoRaWANTask(void *pvParameters) {
    electrical_data_t electrical_data;
    TickType_t xLastWakeTime = xTaskGetTickCount();
    
    // Initialize LoRaWAN
    if (lorawan_init() != LORAWAN_SUCCESS) {
        // Error indication
        while(1) {
            GPIO_WriteBit(GPIOA, GPIO_Pin_2, Bit_SET);
            vTaskDelay(pdMS_TO_TICKS(500));
            GPIO_WriteBit(GPIOA, GPIO_Pin_2, Bit_RESET);
            vTaskDelay(pdMS_TO_TICKS(500));
        }
    }
    
    // Join network
    lorawan_join();
    
    while(1) {
        // Wait for electrical data
        if (xQueueReceive(xElectricalDataQueue, &electrical_data, portMAX_DELAY) == pdTRUE) {
            
            // Build electrical data payload (24 bytes - detailed electrical info)
            uint8_t payload[24];
            uint8_t idx = 0;
            
            payload[idx++] = 0x01;  // Energy sector
            payload[idx++] = 0x01;  // Node ID
            payload[idx++] = 0x10;  // Electrical measurements type
            payload[idx++] = electrical_data.safety_status;
            
            // Voltage RMS (16-bit, 0.1V resolution)
            uint16_t voltage_encoded = (uint16_t)(electrical_data.voltage_rms * 10);
            payload[idx++] = (voltage_encoded >> 8) & 0xFF;
            payload[idx++] = voltage_encoded & 0xFF;
            
            // Current RMS (16-bit, 0.01A resolution)
            uint16_t current_encoded = (uint16_t)(electrical_data.current_rms * 100);
            payload[idx++] = (current_encoded >> 8) & 0xFF;
            payload[idx++] = current_encoded & 0xFF;
            
            // Active Power (16-bit, 1W resolution)
            uint16_t power_encoded = (uint16_t)electrical_data.power_active;
            payload[idx++] = (power_encoded >> 8) & 0xFF;
            payload[idx++] = power_encoded & 0xFF;
            
            // Power Factor (8-bit, 0.01 resolution)
            payload[idx++] = (uint8_t)(electrical_data.power_factor * 100);
            
            // Frequency (8-bit, 0.1Hz resolution, offset from 45Hz)
            payload[idx++] = (uint8_t)((electrical_data.frequency - 45.0) * 10);
            
            // THD Voltage (8-bit, 0.1% resolution)
            payload[idx++] = (uint8_t)(electrical_data.thd_voltage * 10);
            
            // THD Current (8-bit, 0.1% resolution)
            payload[idx++] = (uint8_t)(electrical_data.thd_current * 10);
            
            // Power Quality Grade
            payload[idx++] = electrical_data.quality_grade;
            
            // Timestamp (32-bit)
            payload[idx++] = (electrical_data.timestamp >> 24) & 0xFF;
            payload[idx++] = (electrical_data.timestamp >> 16) & 0xFF;
            payload[idx++] = (electrical_data.timestamp >> 8) & 0xFF;
            payload[idx++] = electrical_data.timestamp & 0xFF;
            
            // Reactive Power (16-bit, 1VAR resolution)
            uint16_t reactive_encoded = (uint16_t)electrical_data.power_reactive;
            payload[idx++] = (reactive_encoded >> 8) & 0xFF;
            payload[idx++] = reactive_encoded & 0xFF;
            
            // Battery level
            payload[idx++] = power_get_battery_level();
            
            // CRC8 checksum
            payload[idx++] = calculate_crc8(payload, idx);
            
            // Send data
            if (lorawan_send(payload, idx, 10) == LORAWAN_SUCCESS) {  // Port 10 for electrical data
                // Success indication
                GPIO_WriteBit(GPIOA, GPIO_Pin_1, Bit_SET);   // Green LED
                vTaskDelay(pdMS_TO_TICKS(100));
                GPIO_WriteBit(GPIOA, GPIO_Pin_1, Bit_RESET);
            }
        }
        
        vTaskDelayUntil(&xLastWakeTime, pdMS_TO_TICKS(1000));
    }
}

/*
 * ADC Interrupt Handler - High-speed data acquisition
 */
void ADC1_IRQHandler(void) __attribute__((interrupt("WCH-Interrupt-fast")));
void ADC1_IRQHandler(void) {
    if (ADC_GetITStatus(ADC1, ADC_IT_EOC) != RESET) {
        // Read voltage channel
        adc_buffer_voltage[adc_buffer_index] = ADC_GetConversionValue(ADC1);
        
        // Switch to current channel
        ADC_RegularChannelConfig(ADC1, ADC_Channel_1, 1, ADC_SampleTime_7Cycles5);
        ADC_SoftwareStartConvCmd(ADC1, ENABLE);
        
        // Small delay for channel switching
        for (volatile int i = 0; i < 10; i++);
        
        // Read current channel
        adc_buffer_current[adc_buffer_index] = ADC_GetConversionValue(ADC1);
        
        // Switch back to voltage channel for next cycle
        ADC_RegularChannelConfig(ADC1, ADC_Channel_0, 1, ADC_SampleTime_7Cycles5);
        
        adc_buffer_index++;
        
        if (adc_buffer_index >= ADC_BUFFER_SIZE) {
            adc_buffer_index = 0;
            adc_buffer_ready = true;
            // Stop ADC until buffer is processed
            ADC_Cmd(ADC1, DISABLE);
        }
        
        ADC_ClearITPendingBit(ADC1, ADC_IT_EOC);
    }
}

/*
 * System Initialization - Electrical measurement optimized
 */
void system_init(void) {
    // Enable peripheral clocks
    RCC_APB2PeriphClockCmd(RCC_APB2Periph_GPIOA | RCC_APB2Periph_GPIOC | RCC_APB2Periph_ADC1, ENABLE);
    RCC_APB1PeriphClockCmd(RCC_APB1Periph_TIM2, ENABLE);
    
    // Configure GPIO for LEDs
    GPIO_InitTypeDef GPIO_InitStructure = {0};
    GPIO_InitStructure.GPIO_Pin = GPIO_Pin_1 | GPIO_Pin_2;
    GPIO_InitStructure.GPIO_Mode = GPIO_Mode_Out_PP;
    GPIO_InitStructure.GPIO_Speed = GPIO_Speed_2MHz;
    GPIO_Init(GPIOA, &GPIO_InitStructure);
    
    // Configure ADC pins (PA0 = Voltage, PA1 = Current)
    GPIO_InitStructure.GPIO_Pin = GPIO_Pin_0 | GPIO_Pin_1;
    GPIO_InitStructure.GPIO_Mode = GPIO_Mode_AIN;
    GPIO_Init(GPIOA, &GPIO_InitStructure);
    
    // Configure ADC for high-speed sampling
    ADC_InitTypeDef ADC_InitStructure = {0};
    ADC_InitStructure.ADC_Mode = ADC_Mode_Independent;
    ADC_InitStructure.ADC_ScanConvMode = DISABLE;
    ADC_InitStructure.ADC_ContinuousConvMode = DISABLE;
    ADC_InitStructure.ADC_ExternalTrigConv = ADC_ExternalTrigConv_T2_CC2;
    ADC_InitStructure.ADC_DataAlign = ADC_DataAlign_Right;
    ADC_InitStructure.ADC_NbrOfChannel = 1;
    ADC_Init(ADC1, &ADC_InitStructure);
    
    // Configure ADC regular channel
    ADC_RegularChannelConfig(ADC1, ADC_Channel_0, 1, ADC_SampleTime_7Cycles5);
    
    // Enable ADC interrupt
    ADC_ITConfig(ADC1, ADC_IT_EOC, ENABLE);
    NVIC_EnableIRQ(ADC_IRQn);
    
    // Enable ADC
    ADC_Cmd(ADC1, ENABLE);
    
    // ADC calibration
    ADC_ResetCalibration(ADC1);
    while(ADC_GetResetCalibrationStatus(ADC1));
    ADC_StartCalibration(ADC1);
    while(ADC_GetCalibrationStatus(ADC1));
    
    // Configure Timer 2 for ADC trigger (2kHz sampling rate)
    TIM_TimeBaseInitTypeDef TIM_TimeBaseStructure = {0};
    TIM_TimeBaseStructure.TIM_Period = 24000 - 1;  // 48MHz/2kHz = 24000
    TIM_TimeBaseStructure.TIM_Prescaler = 0;
    TIM_TimeBaseStructure.TIM_ClockDivision = TIM_CKD_DIV1;
    TIM_TimeBaseStructure.TIM_CounterMode = TIM_CounterMode_Up;
    TIM_TimeBaseInit(TIM2, &TIM_TimeBaseStructure);
    
    // Configure TIM2 CC2 for ADC trigger
    TIM_OCInitTypeDef TIM_OCInitStructure = {0};
    TIM_OCInitStructure.TIM_OCMode = TIM_OCMode_PWM1;
    TIM_OCInitStructure.TIM_OutputState = TIM_OutputState_Enable;
    TIM_OCInitStructure.TIM_Pulse = 12000;  // 50% duty cycle
    TIM_OCInitStructure.TIM_OCPolarity = TIM_OCPolarity_High;
    TIM_OC2Init(TIM2, &TIM_OCInitStructure);
    
    TIM_Cmd(TIM2, ENABLE);
    
    // Power management initialization
    power_init();
}

/*
 * Main Function - Electrical sensors
 */
int main(void) {
    // System initialization
    SystemInit();
    system_init();
    
    // Create FreeRTOS objects
    xElectricalDataQueue = xQueueCreate(10, sizeof(electrical_data_t));
    xSafetyAlertQueue = xQueueCreate(5, sizeof(uint8_t));
    xADCMutex = xSemaphoreCreateMutex();
    
    if (xElectricalDataQueue == NULL || xSafetyAlertQueue == NULL || xADCMutex == NULL) {
        while(1);
    }
    
    // Create tasks
    xTaskCreate(vElectricalTask, "Elect", ELECTRICAL_TASK_STACK_SIZE, NULL, ELECTRICAL_TASK_PRIORITY, &xElectricalTaskHandle);
    xTaskCreate(vLoRaWANTask, "LoRa", LORAWAN_TASK_STACK_SIZE, NULL, LORAWAN_TASK_PRIORITY, NULL);
    xTaskCreate(vSafetyTask, "Safety", SAFETY_TASK_STACK_SIZE, NULL, SAFETY_TASK_PRIORITY, &xSafetyTaskHandle);
    
    // Start FreeRTOS scheduler
    vTaskStartScheduler();
    
    // Should never reach here
    while(1);
}

/*
 * Helper Functions
 */
uint8_t calculate_power_quality_grade(electrical_data_t *data) {
    uint8_t grade = 0;  // A grade
    
    // THD penalties
    if (data->thd_voltage > 3.0 || data->thd_current > 3.0) grade += 1;  // B
    if (data->thd_voltage > 5.0 || data->thd_current > 5.0) grade += 1;  // C
    
    // Power factor penalties
    if (data->power_factor < 0.95) grade += 1;
    if (data->power_factor < 0.85) grade += 1;
    
    // Frequency deviation penalties
    if (data->frequency < 49.5 || data->frequency > 50.5) grade += 1;
    if (data->frequency < 49.0 || data->frequency > 51.0) grade += 1;
    
    return (grade > 5) ? 5 : grade;  // F is worst grade
}

uint8_t calculate_crc8(uint8_t *data, uint8_t length) {
    uint8_t crc = 0xFF;
    for (uint8_t i = 0; i < length; i++) {
        crc ^= data[i];
        for (uint8_t j = 0; j < 8; j++) {
            if (crc & 0x80) {
                crc = (crc << 1) ^ 0x31;
            } else {
                crc <<= 1;
            }
        }
    }
    return crc;
}
