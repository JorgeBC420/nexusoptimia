/*
 * NexusOptim IA - Electrical Sensors Driver
 * High-Precision Voltage and Current Measurement
 * 
 * Features:
 * - RMS voltage/current calculation
 * - Power calculations (Active, Reactive, Apparent)
 * - Total Harmonic Distortion (THD) analysis
 * - Frequency measurement
 * - Power quality analysis
 * 
 * Copyright (c) 2025 OpenNexus
 * Licensed under MIT License
 */

#ifndef ELECTRICAL_SENSORS_H
#define ELECTRICAL_SENSORS_H

#include <stdint.h>
#include <stdbool.h>

/* Electrical measurement ranges and scales */
#define VOLTAGE_SCALE_FACTOR    0.244140625   // (250V / 1024) for 10-bit ADC
#define CURRENT_SCALE_FACTOR    0.09765625    // (100A / 1024) for 10-bit ADC
#define ADC_REFERENCE_VOLTAGE   3.3           // ADC reference voltage
#define NOMINAL_FREQUENCY       50.0          // 50Hz nominal frequency

/* Calibration constants */
typedef struct {
    float voltage_gain;       // Voltage gain correction
    float voltage_offset;     // Voltage offset correction
    float current_gain;       // Current gain correction
    float current_offset;     // Current offset correction
    float phase_correction;   // Phase angle correction (degrees)
    uint16_t magic_number;    // Calibration validity check
} electrical_calibration_t;

/* Power quality thresholds */
#define PQ_EXCELLENT_THD        2.0   // <2% THD
#define PQ_GOOD_THD            3.0   // <3% THD
#define PQ_ACCEPTABLE_THD      5.0   // <5% THD
#define PQ_POOR_THD            8.0   // <8% THD

#define PQ_EXCELLENT_PF        0.95  // >95% Power Factor
#define PQ_GOOD_PF            0.90  // >90% Power Factor
#define PQ_ACCEPTABLE_PF      0.85  // >85% Power Factor

/* Function declarations */

/**
 * Initialize electrical sensors and calibration
 * @return true on success, false on failure
 */
bool electrical_sensors_init(void);

/**
 * Load calibration data from EEPROM
 * @return true if valid calibration found, false otherwise
 */
bool electrical_calibration_load(void);

/**
 * Save calibration data to EEPROM
 * @param cal Pointer to calibration structure
 * @return true on success, false on failure
 */
bool electrical_calibration_save(const electrical_calibration_t *cal);

/**
 * Perform calibration procedure
 * @param reference_voltage Known reference voltage (V)
 * @param reference_current Known reference current (A)
 * @return true on successful calibration
 */
bool electrical_calibrate(float reference_voltage, float reference_current);

/**
 * Calculate RMS voltage from ADC samples
 * @param samples Pointer to ADC voltage samples
 * @param count Number of samples
 * @return RMS voltage in volts
 */
float calculate_rms_voltage(const uint16_t *samples, uint16_t count);

/**
 * Calculate RMS current from ADC samples
 * @param samples Pointer to ADC current samples
 * @param count Number of samples
 * @return RMS current in amperes
 */
float calculate_rms_current(const uint16_t *samples, uint16_t count);

/**
 * Calculate active power from voltage and current samples
 * @param voltage_samples Pointer to voltage samples
 * @param current_samples Pointer to current samples
 * @param count Number of samples
 * @return Active power in watts
 */
float calculate_active_power(const uint16_t *voltage_samples, 
                           const uint16_t *current_samples, 
                           uint16_t count);

/**
 * Calculate reactive power from voltage and current samples
 * @param voltage_samples Pointer to voltage samples
 * @param current_samples Pointer to current samples
 * @param count Number of samples
 * @return Reactive power in VAR
 */
float calculate_reactive_power(const uint16_t *voltage_samples, 
                             const uint16_t *current_samples, 
                             uint16_t count);

/**
 * Calculate Total Harmonic Distortion for voltage
 * @param samples Pointer to voltage samples
 * @param count Number of samples (must be power of 2)
 * @return THD percentage
 */
float calculate_thd_voltage(const uint16_t *samples, uint16_t count);

/**
 * Calculate Total Harmonic Distortion for current
 * @param samples Pointer to current samples
 * @param count Number of samples (must be power of 2)
 * @return THD percentage
 */
float calculate_thd_current(const uint16_t *samples, uint16_t count);

/**
 * Calculate line frequency from voltage samples
 * @param samples Pointer to voltage samples
 * @param count Number of samples
 * @param sampling_rate ADC sampling rate in Hz
 * @return Frequency in Hz
 */
float calculate_frequency(const uint16_t *samples, uint16_t count, uint16_t sampling_rate);

/**
 * Calculate power factor from active and apparent power
 * @param active_power Active power in watts
 * @param apparent_power Apparent power in VA
 * @return Power factor (0.0 to 1.0)
 */
float calculate_power_factor(float active_power, float apparent_power);

/**
 * Analyze power quality and return grade
 * @param voltage_rms RMS voltage
 * @param current_rms RMS current
 * @param thd_voltage Voltage THD percentage
 * @param thd_current Current THD percentage
 * @param power_factor Power factor
 * @param frequency Line frequency
 * @return Power quality grade (0=A, 1=B, 2=C, 3=D, 4=E, 5=F)
 */
uint8_t analyze_power_quality(float voltage_rms, float current_rms,
                            float thd_voltage, float thd_current,
                            float power_factor, float frequency);

/**
 * Convert ADC value to voltage with calibration
 * @param adc_value Raw ADC value
 * @return Calibrated voltage
 */
float adc_to_voltage(uint16_t adc_value);

/**
 * Convert ADC value to current with calibration
 * @param adc_value Raw ADC value
 * @return Calibrated current
 */
float adc_to_current(uint16_t adc_value);

/**
 * Detect zero crossings in voltage waveform
 * @param samples Pointer to voltage samples
 * @param count Number of samples
 * @param crossings Array to store crossing indices
 * @param max_crossings Maximum number of crossings to detect
 * @return Number of zero crossings found
 */
uint8_t detect_zero_crossings(const uint16_t *samples, uint16_t count, 
                            uint16_t *crossings, uint8_t max_crossings);

/**
 * Calculate instantaneous power samples
 * @param voltage_samples Pointer to voltage samples
 * @param current_samples Pointer to current samples
 * @param power_samples Output array for power samples
 * @param count Number of samples
 */
void calculate_instantaneous_power(const uint16_t *voltage_samples,
                                 const uint16_t *current_samples,
                                 float *power_samples,
                                 uint16_t count);

/**
 * Simple FFT for harmonic analysis (power of 2 samples only)
 * @param samples Input samples (will be modified)
 * @param count Number of samples (must be power of 2)
 * @param magnitude Output magnitude array
 * @param phase Output phase array (can be NULL if not needed)
 */
void simple_fft(float *samples, uint16_t count, float *magnitude, float *phase);

/**
 * Get current calibration values
 * @return Pointer to current calibration structure
 */
const electrical_calibration_t* electrical_get_calibration(void);

/**
 * Check if calibration is valid
 * @return true if calibrated, false if not
 */
bool electrical_is_calibrated(void);

/**
 * Reset calibration to factory defaults
 */
void electrical_calibration_reset(void);

/* Global calibration structure */
extern electrical_calibration_t g_electrical_calibration;

#endif // ELECTRICAL_SENSORS_H
