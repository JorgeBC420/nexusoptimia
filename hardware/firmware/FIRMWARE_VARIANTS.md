# NexusOptim IA - Firmware Variants
## Specialized RISC-V Firmware for Different Sensor Applications

### Firmware Architecture Overview

The NexusOptim IA platform provides **4 specialized firmware variants** optimized for different sensor applications and cost requirements:

| Firmware Variant | Target Application | Communication | Features | Flash Usage | RAM Usage |
|------------------|-------------------|---------------|----------|-------------|-----------|
| **main.c** | Universal IoT Platform | LoRaWAN + BLE 5.3 | Full feature set | ~14KB | ~1.8KB |
| **main_lorawan_only.c** | Cost-optimized sensors | LoRaWAN only | Power optimized | ~10KB | ~1.2KB |
| **main_electrical.c** | Energy sector | LoRaWAN only | High-precision electrical | ~12KB | ~1.6KB |
| **main_water.c** | Water infrastructure | LoRaWAN only | Water quality + leak detection | ~11KB | ~1.4KB |

---

### 1. Universal Platform (main.c)

**Target Hardware:** CH32V003 + GD32VF103 dual-core
**Communication:** SX1262 (LoRaWAN) + nRF5340 (BLE 5.3)

**Key Features:**
- Dual-core RISC-V architecture
- Multi-protocol communication (LoRaWAN, BLE, WiFi)
- Configurable for all 9 infrastructure sectors
- BLE configuration and maintenance interface
- Advanced power management
- Hardware security module support

**Use Cases:**
- Airport beacon systems
- Gateway and aggregation nodes
- Research and development platforms
- High-value installations requiring local connectivity

**Memory Footprint:**
- Flash: ~14KB (87% of CH32V003 16KB)
- RAM: ~1.8KB (90% of CH32V003 2KB)
- Optimized for dual-MCU configuration

---

### 2. LoRaWAN-Only Platform (main_lorawan_only.c)

**Target Hardware:** CH32V003F4U6 (minimal package)
**Communication:** SX1262 (LoRaWAN 915MHz)

**Key Features:**
- **Ultra-low power consumption** (<10µA sleep mode)
- **Extended battery life** (10+ years with lithium battery)
- **Simplified task structure** (3 tasks vs 4)
- **Adaptive power management** based on battery level
- **Emergency mode** for critical battery situations
- **Compact payload** (11 bytes vs 24 bytes)

**Power Optimization:**
```c
// Battery-based adaptive behavior
if (battery_level < 20%) {
    sampling_rate = 3600000;    // 1 hour intervals
    lora_sf = 12;               // Maximum range
    tx_power = 10;              // Reduced power
} else if (battery_level < 50%) {
    sampling_rate = 1800000;    // 30 minute intervals
    lora_sf = 11;               // Extended range
    tx_power = 12;              // Reduced power
} else {
    sampling_rate = 300000;     // 5 minute intervals (normal)
    lora_sf = 10;               // Balanced range/power
    tx_power = 14;              // Full power
}
```

**Use Cases:**
- Remote environmental monitoring
- Agriculture soil sensors
- Basic infrastructure monitoring
- Large-scale deployments (100+ nodes)
- Battery-powered installations

**Memory Footprint:**
- Flash: ~10KB (62% of CH32V003 16KB)
- RAM: ~1.2KB (60% of CH32V003 2KB)
- **50% memory savings** vs universal platform

---

### 3. Electrical Sensors Platform (main_electrical.c)

**Target Hardware:** CH32V003 + specialized analog front-end
**Communication:** LoRaWAN only
**ADC:** High-speed 2kHz sampling for 50Hz analysis

**Key Features:**
- **High-precision electrical measurements**
  - RMS voltage/current calculation
  - Active, reactive, and apparent power
  - Power factor analysis
  - Total Harmonic Distortion (THD)
  - Frequency measurement (±0.1Hz accuracy)

- **Real-time safety monitoring**
  - Overvoltage/undervoltage protection
  - Overcurrent detection
  - Power quality grading (A-F scale)
  - Emergency alert transmission (<100ms response)

- **Advanced signal processing**
  - 4096-sample ADC buffer for accurate RMS calculations
  - Simple FFT for harmonic analysis
  - Zero-crossing detection
  - Phase angle measurements

**Electrical Specifications:**
```c
// Measurement capabilities
Voltage Range: 0-500V AC/DC (±0.5% accuracy)
Current Range: 0-100A AC/DC (±1% accuracy)  
Power Range: 0-50kW (±1% accuracy)
Frequency: 45-55Hz (±0.1Hz accuracy)
THD Measurement: 0-20% (±0.1% accuracy)
Power Factor: 0.00-1.00 (±0.01 accuracy)
```

**Safety Features:**
```c
// Emergency response system
if (safety_alert & (OVERVOLTAGE | OVERCURRENT | OVERPOWER)) {
    // Immediate LoRaWAN emergency transmission
    send_emergency_packet();
    // Visual/audible alarm activation
    emergency_led_pattern();
}
```

**Use Cases:**
- Electrical grid monitoring
- Industrial power quality analysis
- Solar panel performance monitoring
- Electric vehicle charging stations
- Critical infrastructure protection

**Memory Footprint:**
- Flash: ~12KB (75% of CH32V003 16KB)
- RAM: ~1.6KB (80% of CH32V003 2KB)
- **4KB ADC buffer** for high-speed sampling

---

### 4. Water Infrastructure Platform (main_water.c)

**Target Hardware:** CH32V003F4U6 + waterproof sensors
**Communication:** LoRaWAN only
**Design:** IP68 waterproof rating capability

**Key Features:**
- **Multi-parameter water monitoring**
  - Pressure monitoring (0-10 bar, ±0.25% accuracy)
  - Flow rate measurement (0-100 L/min, ±2% accuracy)
  - pH analysis (6.0-9.0 pH, ±0.1 accuracy)
  - Temperature compensation
  - Water turbidity measurement

- **Advanced leak detection**
  - Real-time pressure trend analysis
  - **Sub-second leak detection** (<500ms response)
  - Emergency alert transmission
  - Adaptive monitoring frequency
  - Pressure history buffer (10 samples)

- **Water quality analysis**
  - Automated quality grading (A-F scale)
  - pH range compliance monitoring
  - Turbidity threshold alerts
  - Temperature optimization tracking

**Leak Detection Algorithm:**
```c
// Pressure trend analysis
pressure_trend = (current_pressure - historical_average) / time_interval;

if (pressure_trend < -leak_threshold) {
    // Leak detected - immediate response
    send_emergency_alert();
    increase_monitoring_frequency();
    activate_visual_alarm();
}
```

**Water Quality Grading:**
```c
// Multi-parameter quality assessment
grade = 0;  // Start with A grade
if (pH < 6.8 || pH > 8.2) grade += 1;        // B grade
if (turbidity > 1.0 NTU) grade += 1;         // B grade  
if (temperature < 5°C || > 30°C) grade += 1; // B grade
// Result: A=Excellent, B=Good, C=Acceptable, D=Poor, E=Bad, F=Unacceptable
```

**Use Cases:**
- Municipal water distribution monitoring
- Industrial water system surveillance
- Agricultural irrigation management
- Leak detection in pipelines
- Water quality compliance monitoring

**Memory Footprint:**
- Flash: ~11KB (69% of CH32V003 16KB)
- RAM: ~1.4KB (70% of CH32V003 2KB)
- **Optimized for waterproof operation**

---

### Firmware Selection Guide

#### Choose **Universal Platform (main.c)** when:
- ✅ Need BLE connectivity for configuration/maintenance
- ✅ Require multiple communication protocols
- ✅ Building gateway or aggregation nodes
- ✅ Need maximum flexibility and features
- ✅ Power is not the primary constraint
- ✅ Budget allows for dual-MCU configuration

#### Choose **LoRaWAN-Only (main_lorawan_only.c)** when:
- ✅ **Battery life is critical** (>5 years required)
- ✅ Cost optimization is priority
- ✅ Remote deployment with difficult access
- ✅ Large-scale deployments (100+ units)
- ✅ Simple environmental monitoring needs
- ✅ **Single sensor type per node**

#### Choose **Electrical Platform (main_electrical.c)** when:
- ✅ **High-precision electrical measurements** required
- ✅ Power quality analysis needed
- ✅ Safety monitoring is critical
- ✅ **Real-time response** required (<100ms)
- ✅ Electrical grid or industrial applications
- ✅ THD and power factor analysis needed

#### Choose **Water Platform (main_water.c)** when:
- ✅ **Leak detection** is primary requirement
- ✅ Water quality monitoring needed
- ✅ **Waterproof operation** required (IP68)
- ✅ Municipal or industrial water systems
- ✅ Flow measurement and accumulation needed
- ✅ Multi-parameter water analysis required

---

### Development and Deployment Strategy

#### Phase 1: Proof of Concept (Q1 2025)
- **Universal Platform**: 10 units for comprehensive testing
- **LoRaWAN-Only**: 25 units for battery life validation
- **Electrical**: 5 units for power quality verification
- **Water**: 10 units for leak detection validation

#### Phase 2: Pilot Deployment (Q2-Q3 2025)
- **Universal Platform**: 50 units (gateways and research)
- **LoRaWAN-Only**: 200 units (environmental monitoring)
- **Electrical**: 25 units (grid monitoring pilot)
- **Water**: 75 units (municipal water pilot)

#### Phase 3: Commercial Rollout (Q4 2025+)
- **Market-driven production** based on pilot results
- **Cost optimization** through volume manufacturing
- **Continuous firmware updates** and improvements
- **Regional customization** for different markets

This specialized firmware approach ensures **optimal performance**, **cost efficiency**, and **power consumption** for each specific application while maintaining a common development framework and manufacturing pipeline.

---

### Technical Specifications Summary

| Parameter | Universal | LoRaWAN-Only | Electrical | Water |
|-----------|-----------|--------------|------------|-------|
| **MCU** | CH32V003 + GD32VF103 | CH32V003F4U6 | CH32V003 + AFE | CH32V003F4U6 |
| **Communication** | LoRaWAN + BLE + WiFi | LoRaWAN only | LoRaWAN only | LoRaWAN only |
| **Power Consumption** | 50mA active / 10µA sleep | 30mA active / 1µA sleep | 60mA active / 5µA sleep | 35mA active / 2µA sleep |
| **Battery Life** | 2-3 years | 8-10 years | 3-5 years | 5-7 years |
| **Flash Usage** | 14KB (87%) | 10KB (62%) | 12KB (75%) | 11KB (69%) |
| **RAM Usage** | 1.8KB (90%) | 1.2KB (60%) | 1.6KB (80%) | 1.4KB (70%) |
| **Sampling Rate** | Configurable | 5min-1hour | 2kHz (electrical) | 10sec-5min |
| **Payload Size** | 24 bytes | 11 bytes | 24 bytes | 18 bytes |
| **Target Cost** | $45-85 | $12-18 | $25-35 | $18-25 |

This comprehensive firmware strategy provides the flexibility to address multiple market segments while optimizing for the specific requirements of each application domain.
