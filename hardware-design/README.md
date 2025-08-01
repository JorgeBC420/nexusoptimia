# Hardware Design - NexusOptim IA
# Especificaciones técnicas y esquemas de PCB para sensores Edge AI

## 📋 Resumen de Componentes

### 🔌 Sensor de Voltaje/Corriente v1.0
- **Microcontrolador**: Raspberry Pi Pico W (RP2040)
- **Comunicación**: RFM95W LoRa (915MHz)
- **ADC**: ADS1115 (16-bit, I2C)
- **Sensor Corriente**: SCT-013-000 (100A no invasivo)
- **Alimentación**: 18650 Li-ion + Solar (opcional)
- **Certificación**: SUTEL Costa Rica (915MHz ISM)

## 🔧 Lista de Materiales (BOM)

| Componente | Especificación | Cantidad | Proveedor CR | Costo Unitario |
|------------|----------------|----------|--------------|----------------|
| Raspberry Pi Pico W | RP2040 + WiFi | 1 | Steren | $8.00 |
| RFM95W LoRa | 915MHz, SX1276 | 1 | AliExpress | $12.00 |
| ADS1115 | 16-bit ADC, I2C | 1 | Electrocomponentes | $7.00 |
| SCT-013-000 | 100A CT | 1 | Arduino CR | $15.00 |
| Batería 18650 | 3.7V, 3000mAh | 1 | Universal Electrónicos | $5.00 |
| PCB Custom | 50x50mm, 2 capas | 1 | PCB CR / JLCPCB | $3.00 |
| Enclosure IP65 | Plástico resistente | 1 | Proveedores locales | $8.00 |

**Total por sensor: ~$58.00 USD**

## 📐 Especificaciones Eléctricas

### Alimentación
- **Voltaje Operación**: 3.3V DC
- **Consumo Activo**: 120mA (transmisión LoRa)
- **Consumo Sleep**: 2µA (deep sleep)
- **Autonomía**: 2+ años con batería 18650

### Sensores
- **Rango Voltaje**: 0-750V AC (divisor 30:1)
- **Rango Corriente**: 0-100A AC (SCT-013)
- **Precisión**: ±0.5% FS
- **Frecuencia Muestreo**: 1kHz (detección picos)

### Comunicación LoRa
- **Frecuencia**: 915MHz (Costa Rica ISM)
- **Potencia TX**: 14dBm (25mW máximo SUTEL)
- **Alcance**: 15km línea vista / 3km urbano
- **Protocolo**: LoRaWAN 1.0.3

## 🔌 Diagrama de Conexiones

```
Raspberry Pi Pico W Pinout:
┌─────────────────────┐
│ 3V3  ┌───┐     VBUS │ ← Batería/USB
│ GND  │RP │      GND │
│ GP0  │2040│      GP1 │ ← I2C SDA (ADS1115)
│ GP1  │   │      GP0 │ ← I2C SCL (ADS1115)
│ GP2  │   │      GP7 │ ← SPI MOSI (LoRa)
│ GP3  │USB│      GP6 │ ← SPI SCK (LoRa)
│ GP4  └───┘      GP5 │ ← SPI CS (LoRa)
│ GP5           GP4   │ ← SPI MISO (LoRa)
└─────────────────────┘
```

### Conexiones ADS1115 (Medición Voltaje)
```
ADS1115    →    Pico W
VDD        →    3V3
GND        →    GND
SCL        →    GP1 (I2C Clock)
SDA        →    GP0 (I2C Data)
A0         →    Divisor Voltaje (1MΩ:33kΩ)
```

### Conexiones SCT-013 (Medición Corriente)
```
SCT-013    →    ADS1115
Terminal 1 →    GND
Terminal 2 →    A1 (via burden resistor 33Ω + bias 1.65V)
```

### Conexiones RFM95W (Comunicación LoRa)
```
RFM95W     →    Pico W
VCC        →    3V3
GND        →    GND
SCK        →    GP6 (SPI Clock)
MISO       →    GP4 (SPI MISO)
MOSI       →    GP7 (SPI MOSI)
NSS        →    GP5 (Chip Select)
RST        →    GP3 (Reset)
DIO0       →    GP2 (Interrupt)
```

## 🛡️ Circuito de Protección

### Protección Voltaje
- **Optoacopladores**: HCPL-3700 (aislamiento 5kV)
- **Divisor Resistivo**: 1MΩ + 33kΩ (precisión 0.1%)
- **Clamp Diodes**: 3.3V Zener

### Protección Corriente
- **Burden Resistor**: 33Ω (1W)
- **Bias Network**: 10kΩ + 10kΩ (1.65V)
- **Filter**: RC 150Hz cutoff

## 📄 Archivos de Diseño

### Disponibles en este repositorio:
- `hardware-design/pcb/nexusoptim-sensor-v1.kicad_pro` - Proyecto KiCad
- `hardware-design/pcb/gerbers/` - Archivos Gerber para fabricación
- `hardware-design/3d-models/` - Modelos 3D de enclosures
- `hardware-design/datasheets/` - Hojas de datos de componentes
- `hardware-design/assembly/` - Instrucciones de ensamblaje

### Para Descargar:
- **Gerber Files**: [nexusoptim-sensor-gerbers.zip](./pcb/gerbers/)
- **3D Models**: [enclosure-models.step](./3d-models/)
- **Assembly Guide**: [assembly-instructions.pdf](./assembly/)

## 🏭 Proceso de Fabricación

### PCB
1. **Fabricación**: JLCPCB / PCB Costa Rica
2. **Especificaciones**: 
   - 2 capas, FR4, 1.6mm espesor
   - Acabado HASL sin plomo
   - Máscara verde, serigrafía blanca
   - Vías tapadas para mejor soldadura

### Ensamblaje
1. **SMD Components**: Pasta de soldeo + horno reflow
2. **Through-hole**: Soldadura manual
3. **Testing**: Protocolo automatizado
4. **Calibración**: Ajuste por software

## 🧪 Pruebas y Validación

### Pruebas Eléctricas
- **Aislamiento**: 5kV durante 1 minuto
- **Precisión**: ±0.5% en rango completo
- **Linealidad**: <0.1% error
- **Deriva Térmica**: <100ppm/°C

### Pruebas Ambientales
- **Temperatura**: -10°C a +70°C
- **Humedad**: 0-95% RH sin condensación
- **Vibración**: 10G, 10-2000Hz
- **IP Rating**: IP65 (polvo/agua)

### Pruebas RF (LoRa)
- **Potencia TX**: 14dBm ±1dB
- **Sensibilidad RX**: -137dBm
- **Armónicos**: <-40dBc
- **Certificación SUTEL**: En proceso

## 🌍 Consideraciones Costa Rica

### Regulaciones
- **SUTEL**: Homologación obligatoria 915MHz
- **Potencia Máxima**: 1W EIRP (estamos usando 25mW)
- **Banda**: 902-928MHz (ISM libre)

### Proveedores Locales
- **PCB**: ProtoLab UCR, TEC Electrónica
- **Componentes**: Steren, Electrocomponentes CR
- **Ensamblaje**: Servicios TEC, contratistas

### Costos Optimizados
- **Volumen 100 unidades**: $45/sensor
- **Volumen 1000 unidades**: $35/sensor
- **Fabricación local**: +20% costo, -50% lead time

## 🔄 Roadmap de Hardware

### v1.0 (Actual)
- ✅ Diseño básico funcional
- ✅ Prototipo validado
- ⏳ Certificación SUTEL

### v1.1 (Q3 2025)
- 🔄 Optimización consumo (<1µA sleep)
- 🔄 Antena integrada PCB
- 🔄 USB-C para programación

### v2.0 (Q4 2025)
- 🔮 Edge AI dedicado (NPU)
- 🔮 Comunicación mesh
- 🔮 Sensor temperatura integrado
- 🔮 Solar cell integrado

## 📞 Soporte Técnico

- **Hardware Lead**: Jorge Brenes Castro
- **Email**: hardware@opennexus.cr
- **Documentación**: https://docs.opennexus.cr/hardware
- **Issues**: https://github.com/OpenNexus/nexusoptimia/issues
