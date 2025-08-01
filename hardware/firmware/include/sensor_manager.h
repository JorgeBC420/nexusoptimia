/*
 * NexusOptim IA - Sensor Manager
 * Multi-Sector Sensor Interface
 * 
 * Supports:
 * - Energy: Voltage/Current monitoring
 * - Water: Pressure/Flow sensors
 * - Airport: Temperature/Humidity
 * - Environment: Air quality sensors
 * - Agriculture: Soil moisture/pH
 * 
 * Copyright (c) 2025 OpenNexus
 * Licensed under MIT License
 */

#ifndef SENSOR_MANAGER_H
#define SENSOR_MANAGER_H

#include <stdint.h>
#include <stdbool.h>

/* Sensor Types */
typedef enum {
    SENSOR_TYPE_VOLTAGE = 0x01,      // Energy sector
    SENSOR_TYPE_CURRENT = 0x02,      // Energy sector
    SENSOR_TYPE_PRESSURE = 0x03,     // Water sector
    SENSOR_TYPE_FLOW = 0x04,         // Water sector
    SENSOR_TYPE_TEMPERATURE = 0x05,  // Airport/General
    SENSOR_TYPE_HUMIDITY = 0x06,     // Airport/Environment
    SENSOR_TYPE_CO2 = 0x07,          // Environment sector
    SENSOR_TYPE_PM25 = 0x08,         // Environment sector
    SENSOR_TYPE_SOIL_MOISTURE = 0x09, // Agriculture sector
    SENSOR_TYPE_PH = 0x0A,           // Agriculture/Water
    SENSOR_TYPE_LIGHT = 0x0B,        // Agriculture/Airport
    SENSOR_TYPE_VIBRATION = 0x0C,    // Transportation
    SENSOR_TYPE_GPS = 0x0D,          // Transportation/General
    SENSOR_TYPE_GENERIC = 0xFF       // Generic analog sensor
} sensor_type_t;

/* Sensor Status */
typedef enum {
    SENSOR_STATUS_OK = 0,
    SENSOR_STATUS_ERROR,
    SENSOR_STATUS_CALIBRATING,
    SENSOR_STATUS_OFFLINE
} sensor_status_t;

/* Sensor Data Structure */
typedef struct {
    sensor_type_t type;
    float value;
    uint32_t timestamp;
    sensor_status_t status;
    uint8_t quality;          // Data quality (0-100%)
} sensor_data_t;

/* Sensor Configuration */
typedef struct {
    sensor_type_t type;
    uint8_t i2c_address;      // I2C address (if applicable)
    uint8_t adc_channel;      // ADC channel (for analog sensors)
    float scale_factor;       // Scaling factor
    float offset;             // Offset correction
    uint16_t sample_count;    // Samples for averaging
    bool enabled;             // Sensor enable flag
} sensor_config_t;

/* Public Function Declarations */

/**
 * Initialize sensor manager
 * @return true on success, false on error
 */
bool sensor_init(void);

/**
 * Configure sensor
 * @param config Sensor configuration
 * @return true on success, false on error
 */
bool sensor_configure(const sensor_config_t *config);

/**
 * Read voltage sensor (Energy sector)
 * @return Voltage in volts
 */
float sensor_read_voltage(void);

/**
 * Read current sensor (Energy sector)
 * @return Current in amperes
 */
float sensor_read_current(void);

/**
 * Read pressure sensor (Water sector)
 * @return Pressure in bar
 */
float sensor_read_pressure(void);

/**
 * Read flow sensor (Water sector)
 * @return Flow rate in L/min
 */
float sensor_read_flow(void);

/**
 * Read temperature sensor
 * @return Temperature in Celsius
 */
float sensor_read_temperature(void);

/**
 * Read humidity sensor
 * @return Relative humidity in %
 */
float sensor_read_humidity(void);

/**
 * Read CO2 sensor (Environment sector)
 * @return CO2 concentration in ppm
 */
float sensor_read_co2(void);

/**
 * Read PM2.5 sensor (Environment sector)
 * @return PM2.5 concentration in µg/m³
 */
float sensor_read_pm25(void);

/**
 * Read soil moisture sensor (Agriculture sector)
 * @return Soil moisture in %
 */
float sensor_read_soil_moisture(void);

/**
 * Read pH sensor
 * @return pH value (0-14)
 */
float sensor_read_ph(void);

/**
 * Read light sensor
 * @return Light intensity in lux
 */
float sensor_read_light(void);

/**
 * Read vibration sensor
 * @return Vibration level (0-100)
 */
float sensor_read_vibration(void);

/**
 * Read generic analog sensor
 * @return Raw ADC value (0-4095)
 */
float sensor_read_generic(void);

/**
 * Get sensor status
 * @param type Sensor type
 * @return Sensor status
 */
sensor_status_t sensor_get_status(sensor_type_t type);

/**
 * Calibrate sensor
 * @param type Sensor type
 * @param reference_value Known reference value
 * @return true on success, false on error
 */
bool sensor_calibrate(sensor_type_t type, float reference_value);

/**
 * Enable/disable sensor
 * @param type Sensor type
 * @param enable true to enable, false to disable
 */
void sensor_enable(sensor_type_t type, bool enable);

/**
 * Get sensor reading with full data structure
 * @param type Sensor type
 * @param data Pointer to sensor data structure
 * @return true on success, false on error
 */
bool sensor_read_data(sensor_type_t type, sensor_data_t *data);

/**
 * Perform sensor self-test
 * @return true if all sensors pass, false if any fail
 */
bool sensor_self_test(void);

/**
 * Enter low power mode
 */
void sensor_sleep(void);

/**
 * Wake up from low power mode
 */
void sensor_wakeup(void);

/* Sector-specific sensor arrays */
extern const sensor_type_t energy_sensors[];
extern const sensor_type_t water_sensors[];
extern const sensor_type_t airport_sensors[];
extern const sensor_type_t environment_sensors[];
extern const sensor_type_t agriculture_sensors[];
extern const sensor_type_t transportation_sensors[];

extern const uint8_t energy_sensor_count;
extern const uint8_t water_sensor_count;
extern const uint8_t airport_sensor_count;
extern const uint8_t environment_sensor_count;
extern const uint8_t agriculture_sensor_count;
extern const uint8_t transportation_sensor_count;

#endif // SENSOR_MANAGER_H
