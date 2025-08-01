/*
 * NexusOptim IA - LoRaWAN Handler Implementation
 * SX1262 Radio Driver for Helium Network
 * 
 * Copyright (c) 2025 OpenNexus
 * Licensed under MIT License
 */

#include "lorawan_handler.h"
#include "sx1262_driver.h"
#include <ch32v00x.h>
#include <string.h>
#include <stdio.h>

/* LoRaWAN State Machine */
typedef enum {
    LORAWAN_STATE_IDLE,
    LORAWAN_STATE_JOINING,
    LORAWAN_STATE_JOINED,
    LORAWAN_STATE_SENDING,
    LORAWAN_STATE_SLEEP
} lorawan_state_t;

/* Global Variables */
static lorawan_state_t lorawan_state = LORAWAN_STATE_IDLE;
static lorawan_session_t session = {0};
static lorawan_credentials_t credentials;
static uint32_t last_tx_timestamp = 0;
static int8_t last_rssi = -100;
static int8_t last_snr = -20;

/* Costa Rica Helium Network Configuration */
const uint32_t cr_hotspot_frequencies[] = {
    915200000, 915400000, 915600000, 915800000,  // Sub-band 2
    916000000, 916200000, 916400000, 916600000   // Sub-band 2 (primary)
};
const uint8_t cr_hotspot_count = sizeof(cr_hotspot_frequencies) / sizeof(uint32_t);

/* Default OTAA Credentials (MUST be updated for production) */
const lorawan_credentials_t default_credentials = {
    .dev_eui = {0x70, 0xB3, 0xD5, 0x7E, 0xD0, 0x06, 0x12, 0x34},  // Example DevEUI
    .app_eui = {0x70, 0xB3, 0xD5, 0x7E, 0xD0, 0x06, 0x00, 0x01},  // Example AppEUI
    .app_key = {0x2B, 0x7E, 0x15, 0x16, 0x28, 0xAE, 0xD2, 0xA6,   // Example AppKey
                0xAB, 0xF7, 0x15, 0x88, 0x09, 0xCF, 0x4F, 0x3C}
};

/* Static Function Declarations */
static void lorawan_radio_init(void);
static void lorawan_timer_init(void);
static lorawan_result_t lorawan_send_join_request(void);
static lorawan_result_t lorawan_process_join_accept(void);
static void lorawan_generate_keys(uint8_t *app_nonce, uint8_t *net_id, uint16_t dev_nonce);
static uint32_t lorawan_get_timestamp(void);
static void lorawan_delay_ms(uint32_t ms);

/**
 * Initialize LoRaWAN stack
 */
lorawan_result_t lorawan_init(void) {
    // Copy default credentials
    memcpy(&credentials, &default_credentials, sizeof(lorawan_credentials_t));
    
    // Initialize radio module
    lorawan_radio_init();
    
    // Initialize timer for timestamps
    lorawan_timer_init();
    
    // Initialize SX1262 radio
    if (sx1262_init() != SX1262_OK) {
        return LORAWAN_ERROR_INIT;
    }
    
    // Configure radio for LoRaWAN AU915
    sx1262_set_frequency(LORAWAN_FREQUENCY);
    sx1262_set_spreading_factor(9);     // SF9
    sx1262_set_bandwidth(125);          // 125kHz
    sx1262_set_coding_rate(5);          // 4/5
    sx1262_set_tx_power(LORAWAN_POWER);
    sx1262_set_preamble_length(8);
    sx1262_set_sync_word(0x3444);       // LoRaWAN sync word
    
    // Reset session
    memset(&session, 0, sizeof(lorawan_session_t));
    session.joined = false;
    
    lorawan_state = LORAWAN_STATE_IDLE;
    return LORAWAN_SUCCESS;
}

/**
 * Join LoRaWAN network using OTAA
 */
lorawan_result_t lorawan_join(void) {
    if (lorawan_state != LORAWAN_STATE_IDLE) {
        return LORAWAN_ERROR_BUSY;
    }
    
    // Send join request
    lorawan_result_t result = lorawan_send_join_request();
    if (result != LORAWAN_SUCCESS) {
        return result;
    }
    
    lorawan_state = LORAWAN_STATE_JOINING;
    
    // Wait for join accept (timeout: 5 seconds)
    uint32_t timeout = lorawan_get_timestamp() + 5000;
    while (lorawan_get_timestamp() < timeout) {
        if (sx1262_is_rx_done()) {
            result = lorawan_process_join_accept();
            if (result == LORAWAN_SUCCESS) {
                session.joined = true;
                lorawan_state = LORAWAN_STATE_JOINED;
                return LORAWAN_SUCCESS;
            }
        }
        lorawan_delay_ms(10);
    }
    
    lorawan_state = LORAWAN_STATE_IDLE;
    return LORAWAN_ERROR_JOIN;
}

/**
 * Send data to LoRaWAN network
 */
lorawan_result_t lorawan_send(uint8_t *data, uint8_t length, uint8_t port) {
    if (!session.joined || lorawan_state != LORAWAN_STATE_JOINED) {
        return LORAWAN_ERROR_NO_NETWORK;
    }
    
    if (length > 242) {  // Max payload for DR3
        return LORAWAN_ERROR_SEND;
    }
    
    // Check duty cycle (1% for AU915)
    uint32_t current_time = lorawan_get_timestamp();
    if (current_time - last_tx_timestamp < 99000) {  // 99 seconds minimum
        return LORAWAN_ERROR_BUSY;
    }
    
    // Build LoRaWAN frame
    uint8_t frame[256];
    uint8_t frame_length = 0;
    
    // MAC Header (MHDR)
    frame[frame_length++] = 0x40;  // Unconfirmed Data Up
    
    // Frame Header (FHDR)
    frame[frame_length++] = (session.dev_addr >> 0) & 0xFF;   // DevAddr
    frame[frame_length++] = (session.dev_addr >> 8) & 0xFF;
    frame[frame_length++] = (session.dev_addr >> 16) & 0xFF;
    frame[frame_length++] = (session.dev_addr >> 24) & 0xFF;
    
    frame[frame_length++] = 0x00;  // FCtrl (no options)
    
    frame[frame_length++] = (session.fcnt_up >> 0) & 0xFF;    // FCnt
    frame[frame_length++] = (session.fcnt_up >> 8) & 0xFF;
    
    // Port
    frame[frame_length++] = port;
    
    // Payload (encrypted with AppSKey)
    for (uint8_t i = 0; i < length; i++) {
        frame[frame_length++] = data[i] ^ session.app_skey[i % 16];  // Simple XOR (real implementation uses AES)
    }
    
    // MIC (Message Integrity Code) - simplified
    uint32_t mic = 0x12345678;  // Real implementation uses AES-CMAC
    frame[frame_length++] = (mic >> 0) & 0xFF;
    frame[frame_length++] = (mic >> 8) & 0xFF;
    frame[frame_length++] = (mic >> 16) & 0xFF;
    frame[frame_length++] = (mic >> 24) & 0xFF;
    
    // Send frame
    lorawan_state = LORAWAN_STATE_SENDING;
    sx1262_send(frame, frame_length);
    
    // Wait for transmission complete
    while (!sx1262_is_tx_done()) {
        lorawan_delay_ms(1);
    }
    
    // Update counters
    session.fcnt_up++;
    last_tx_timestamp = current_time;
    last_rssi = sx1262_get_rssi();
    last_snr = sx1262_get_snr();
    
    lorawan_state = LORAWAN_STATE_JOINED;
    return LORAWAN_SUCCESS;
}

/**
 * Check if ready to send
 */
bool lorawan_is_ready(void) {
    return (session.joined && lorawan_state == LORAWAN_STATE_JOINED);
}

/**
 * Get RSSI
 */
int8_t lorawan_get_rssi(void) {
    return last_rssi;
}

/**
 * Get SNR
 */
int8_t lorawan_get_snr(void) {
    return last_snr;
}

/**
 * Check join status
 */
bool lorawan_is_joined(void) {
    return session.joined;
}

/**
 * Process LoRaWAN events
 */
void lorawan_process(void) {
    // Handle downlink messages
    if (sx1262_is_rx_done()) {
        uint8_t rx_buffer[256];
        uint8_t rx_length = sx1262_receive(rx_buffer, sizeof(rx_buffer));
        
        if (rx_length > 0) {
            // Process downlink (simplified)
            last_rssi = sx1262_get_rssi();
            last_snr = sx1262_get_snr();
        }
    }
}

/**
 * Enter sleep mode
 */
void lorawan_sleep(void) {
    sx1262_sleep();
    lorawan_state = LORAWAN_STATE_SLEEP;
}

/**
 * Wake up from sleep
 */
void lorawan_wakeup(void) {
    sx1262_wakeup();
    if (session.joined) {
        lorawan_state = LORAWAN_STATE_JOINED;
    } else {
        lorawan_state = LORAWAN_STATE_IDLE;
    }
}

/**
 * Reset LoRaWAN stack
 */
void lorawan_reset(void) {
    sx1262_reset();
    memset(&session, 0, sizeof(lorawan_session_t));
    session.joined = false;
    lorawan_state = LORAWAN_STATE_IDLE;
}

/* Static Function Implementations */

static void lorawan_radio_init(void) {
    // Configure SPI for SX1262
    RCC_APB2PeriphClockCmd(RCC_APB2Periph_SPI1, ENABLE);
    
    GPIO_InitTypeDef GPIO_InitStructure = {0};
    
    // SPI pins: SCK(PA5), MISO(PA6), MOSI(PA7)
    GPIO_InitStructure.GPIO_Pin = GPIO_Pin_5 | GPIO_Pin_6 | GPIO_Pin_7;
    GPIO_InitStructure.GPIO_Mode = GPIO_Mode_AF_PP;
    GPIO_InitStructure.GPIO_Speed = GPIO_Speed_50MHz;
    GPIO_Init(GPIOA, &GPIO_InitStructure);
    
    // NSS pin (PA4)
    GPIO_InitStructure.GPIO_Pin = GPIO_Pin_4;
    GPIO_InitStructure.GPIO_Mode = GPIO_Mode_Out_PP;
    GPIO_Init(GPIOA, &GPIO_InitStructure);
    
    // Configure SPI
    SPI_InitTypeDef SPI_InitStructure = {0};
    SPI_InitStructure.SPI_Direction = SPI_Direction_2Lines_FullDuplex;
    SPI_InitStructure.SPI_Mode = SPI_Mode_Master;
    SPI_InitStructure.SPI_DataSize = SPI_DataSize_8b;
    SPI_InitStructure.SPI_CPOL = SPI_CPOL_Low;
    SPI_InitStructure.SPI_CPHA = SPI_CPHA_1Edge;
    SPI_InitStructure.SPI_NSS = SPI_NSS_Soft;
    SPI_InitStructure.SPI_BaudRatePrescaler = SPI_BaudRatePrescaler_8;
    SPI_InitStructure.SPI_FirstBit = SPI_FirstBit_MSB;
    SPI_Init(SPI1, &SPI_InitStructure);
    SPI_Cmd(SPI1, ENABLE);
}

static void lorawan_timer_init(void) {
    // Configure TIM2 for timestamps
    RCC_APB1PeriphClockCmd(RCC_APB1Periph_TIM2, ENABLE);
    
    TIM_TimeBaseInitTypeDef TIM_TimeBaseStructure = {0};
    TIM_TimeBaseStructure.TIM_Period = 0xFFFFFFFF;
    TIM_TimeBaseStructure.TIM_Prescaler = 48 - 1;  // 1MHz counter (48MHz / 48)
    TIM_TimeBaseStructure.TIM_ClockDivision = TIM_CKD_DIV1;
    TIM_TimeBaseStructure.TIM_CounterMode = TIM_CounterMode_Up;
    TIM_TimeBaseInit(TIM2, &TIM_TimeBaseStructure);
    TIM_Cmd(TIM2, ENABLE);
}

static lorawan_result_t lorawan_send_join_request(void) {
    // Build join request frame
    uint8_t join_request[23];
    uint8_t length = 0;
    
    // MHDR
    join_request[length++] = 0x00;  // Join Request
    
    // AppEUI (reversed)
    for (int i = 7; i >= 0; i--) {
        join_request[length++] = credentials.app_eui[i];
    }
    
    // DevEUI (reversed)
    for (int i = 7; i >= 0; i--) {
        join_request[length++] = credentials.dev_eui[i];
    }
    
    // DevNonce (random)
    uint16_t dev_nonce = 0x1234;  // Should be random
    join_request[length++] = (dev_nonce >> 0) & 0xFF;
    join_request[length++] = (dev_nonce >> 8) & 0xFF;
    
    // MIC (simplified)
    uint32_t mic = 0x87654321;
    join_request[length++] = (mic >> 0) & 0xFF;
    join_request[length++] = (mic >> 8) & 0xFF;
    join_request[length++] = (mic >> 16) & 0xFF;
    join_request[length++] = (mic >> 24) & 0xFF;
    
    // Send join request
    sx1262_send(join_request, length);
    
    // Wait for transmission complete
    while (!sx1262_is_tx_done()) {
        lorawan_delay_ms(1);
    }
    
    // Switch to RX mode for join accept
    sx1262_receive_continuous();
    
    return LORAWAN_SUCCESS;
}

static lorawan_result_t lorawan_process_join_accept(void) {
    uint8_t rx_buffer[256];
    uint8_t rx_length = sx1262_receive(rx_buffer, sizeof(rx_buffer));
    
    if (rx_length < 17) {  // Minimum join accept length
        return LORAWAN_ERROR_JOIN;
    }
    
    // Simplified join accept processing
    // In real implementation, decrypt and verify MIC
    
    // Extract DevAddr
    session.dev_addr = (rx_buffer[4] << 0) | (rx_buffer[5] << 8) | 
                      (rx_buffer[6] << 16) | (rx_buffer[7] << 24);
    
    // Generate session keys (simplified)
    uint8_t app_nonce[3] = {rx_buffer[1], rx_buffer[2], rx_buffer[3]};
    uint8_t net_id[3] = {rx_buffer[8], rx_buffer[9], rx_buffer[10]};
    uint16_t dev_nonce = 0x1234;
    
    lorawan_generate_keys(app_nonce, net_id, dev_nonce);
    
    // Reset frame counters
    session.fcnt_up = 0;
    session.fcnt_down = 0;
    
    return LORAWAN_SUCCESS;
}

static void lorawan_generate_keys(uint8_t *app_nonce, uint8_t *net_id, uint16_t dev_nonce) {
    // Simplified key generation (real implementation uses AES)
    for (int i = 0; i < 16; i++) {
        session.nwk_skey[i] = credentials.app_key[i] ^ (i + 0x01);
        session.app_skey[i] = credentials.app_key[i] ^ (i + 0x02);
    }
}

static uint32_t lorawan_get_timestamp(void) {
    return TIM_GetCounter(TIM2) / 1000;  // Convert to milliseconds
}

static void lorawan_delay_ms(uint32_t ms) {
    uint32_t start = lorawan_get_timestamp();
    while ((lorawan_get_timestamp() - start) < ms);
}
