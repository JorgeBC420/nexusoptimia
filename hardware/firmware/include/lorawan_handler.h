/*
 * NexusOptim IA - LoRaWAN Handler
 * Helium Network Integration for Costa Rica
 * 
 * Frequency Plan: AU915 (915MHz for Costa Rica)
 * Network: Helium Console
 * Protocol: LoRaWAN 1.0.3
 * 
 * Copyright (c) 2025 OpenNexus
 * Licensed under MIT License
 */

#ifndef LORAWAN_HANDLER_H
#define LORAWAN_HANDLER_H

#include <stdint.h>
#include <stdbool.h>

/* LoRaWAN Return Codes */
typedef enum {
    LORAWAN_SUCCESS = 0,
    LORAWAN_ERROR_INIT,
    LORAWAN_ERROR_JOIN,
    LORAWAN_ERROR_SEND,
    LORAWAN_ERROR_BUSY,
    LORAWAN_ERROR_NO_NETWORK
} lorawan_result_t;

/* LoRaWAN Configuration for Costa Rica */
#define LORAWAN_REGION          "AU915"    // 915MHz band
#define LORAWAN_FREQUENCY       915000000  // Base frequency
#define LORAWAN_DATARATE        DR_3       // SF9BW125 (default)
#define LORAWAN_POWER           14         // 14dBm (25mW)
#define LORAWAN_ADR_ENABLED     true       // Adaptive Data Rate
#define LORAWAN_CONFIRMED       false      // Unconfirmed uplinks

/* Device Credentials (OTAA) */
typedef struct {
    uint8_t dev_eui[8];    // Device EUI (from Helium Console)
    uint8_t app_eui[8];    // Application EUI
    uint8_t app_key[16];   // Application Key
} lorawan_credentials_t;

/* Network Session Info */
typedef struct {
    uint32_t dev_addr;     // Device Address (after join)
    uint8_t nwk_skey[16];  // Network Session Key
    uint8_t app_skey[16];  // Application Session Key
    uint16_t fcnt_up;      // Uplink frame counter
    uint16_t fcnt_down;    // Downlink frame counter
    bool joined;           // Network join status
} lorawan_session_t;

/* Public Function Declarations */

/**
 * Initialize LoRaWAN stack and radio module
 * @return LORAWAN_SUCCESS on success, error code otherwise
 */
lorawan_result_t lorawan_init(void);

/**
 * Join LoRaWAN network using OTAA
 * @return LORAWAN_SUCCESS on success, error code otherwise
 */
lorawan_result_t lorawan_join(void);

/**
 * Send data packet to LoRaWAN network
 * @param data Pointer to data buffer
 * @param length Data length (max 242 bytes)
 * @param port Application port (1-223)
 * @return LORAWAN_SUCCESS on success, error code otherwise
 */
lorawan_result_t lorawan_send(uint8_t *data, uint8_t length, uint8_t port);

/**
 * Check if LoRaWAN is ready to send
 * @return true if ready, false if busy
 */
bool lorawan_is_ready(void);

/**
 * Get current RSSI value
 * @return RSSI in dBm
 */
int8_t lorawan_get_rssi(void);

/**
 * Get current SNR value
 * @return SNR in dB
 */
int8_t lorawan_get_snr(void);

/**
 * Enable/disable ADR (Adaptive Data Rate)
 * @param enable true to enable, false to disable
 */
void lorawan_set_adr(bool enable);

/**
 * Set transmission power
 * @param power Power level in dBm (2-20)
 */
void lorawan_set_power(uint8_t power);

/**
 * Set data rate
 * @param datarate Data rate (0-6 for AU915)
 */
void lorawan_set_datarate(uint8_t datarate);

/**
 * Process LoRaWAN events (call from main loop)
 */
void lorawan_process(void);

/**
 * Enter low power mode
 */
void lorawan_sleep(void);

/**
 * Wake up from low power mode
 */
void lorawan_wakeup(void);

/**
 * Get join status
 * @return true if joined to network
 */
bool lorawan_is_joined(void);

/**
 * Reset LoRaWAN stack
 */
void lorawan_reset(void);

/* Costa Rica Helium Hotspot Coverage */
extern const uint32_t cr_hotspot_frequencies[];
extern const uint8_t cr_hotspot_count;

/* Default device credentials (must be updated for production) */
extern const lorawan_credentials_t default_credentials;

#endif // LORAWAN_HANDLER_H
