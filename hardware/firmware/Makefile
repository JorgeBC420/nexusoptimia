# NexusOptim RISC-V Firmware Development
# FreeRTOS + LoRaWAN Stack for CH32V003

RISCV_TOOLCHAIN = riscv32-unknown-elf-gcc
FREERTOS_VERSION = 10.5.1
LORAWAN_STACK = LoRaMac-node-4.7.0

# Project Configuration
PROJECT_NAME = nexusoptim-riscv-firmware
MCU = CH32V003J4M6
FREQ = 48000000
FLASH_SIZE = 16KB
RAM_SIZE = 2KB

# Source Files
SOURCES = \
	src/main.c \
	src/system_init.c \
	src/lorawan_handler.c \
	src/ble_handler.c \
	src/sensor_manager.c \
	src/power_management.c \
	src/freertos_config.c

# FreeRTOS Sources
FREERTOS_SOURCES = \
	FreeRTOS/Source/tasks.c \
	FreeRTOS/Source/queue.c \
	FreeRTOS/Source/list.c \
	FreeRTOS/Source/timers.c \
	FreeRTOS/Source/portable/GCC/RISC-V/port.c

# LoRaWAN Sources
LORAWAN_SOURCES = \
	LoRaMac/src/mac/LoRaMac.c \
	LoRaMac/src/mac/region/Region.c \
	LoRaMac/src/mac/region/RegionUS915.c \
	LoRaMac/src/system/systime.c

# Include Directories
INCLUDES = \
	-Isrc/include \
	-IFreeRTOS/Source/include \
	-IFreeRTOS/Source/portable/GCC/RISC-V \
	-ILoRaMac/src/mac \
	-ILoRaMac/src/system

# Compiler Flags
CFLAGS = \
	-march=rv32ec \
	-mabi=ilp32e \
	-msmall-data-limit=8 \
	-msave-restore \
	-Os \
	-fmessage-length=0 \
	-fsigned-char \
	-ffunction-sections \
	-fdata-sections \
	-fno-common \
	-Wunused \
	-Wuninitialized \
	-g

# Linker Flags
LDFLAGS = \
	-T Link.ld \
	-nostartfiles \
	-Xlinker --gc-sections \
	-Wl,-Map,$(PROJECT_NAME).map \
	--specs=nano.specs \
	--specs=nosys.specs

# Build Targets
all: $(PROJECT_NAME).elf $(PROJECT_NAME).hex $(PROJECT_NAME).bin

$(PROJECT_NAME).elf: $(SOURCES) $(FREERTOS_SOURCES) $(LORAWAN_SOURCES)
	$(RISCV_TOOLCHAIN) $(CFLAGS) $(INCLUDES) $(SOURCES) $(FREERTOS_SOURCES) $(LORAWAN_SOURCES) $(LDFLAGS) -o $@

$(PROJECT_NAME).hex: $(PROJECT_NAME).elf
	riscv32-unknown-elf-objcopy -O ihex $< $@

$(PROJECT_NAME).bin: $(PROJECT_NAME).elf
	riscv32-unknown-elf-objcopy -O binary $< $@

# Programming
flash: $(PROJECT_NAME).hex
	wch-link -f $<

# Debug
debug: $(PROJECT_NAME).elf
	riscv32-unknown-elf-gdb $< -ex "target remote localhost:3333"

# Clean
clean:
	rm -f *.elf *.hex *.bin *.map

# Dependencies
install-deps:
	# Install RISC-V GCC toolchain
	wget https://github.com/xpack-dev-tools/riscv-none-embed-gcc-xpack/releases/download/v10.2.0-1.2/xpack-riscv-none-embed-gcc-10.2.0-1.2-linux-x64.tar.gz
	tar -xzf xpack-riscv-none-embed-gcc-10.2.0-1.2-linux-x64.tar.gz
	
	# Clone FreeRTOS
	git clone https://github.com/FreeRTOS/FreeRTOS.git
	
	# Clone LoRaWAN stack
	git clone https://github.com/Lora-net/LoRaMac-node.git

# Configuration
config:
	@echo "NexusOptim RISC-V Firmware Configuration"
	@echo "MCU: $(MCU)"
	@echo "Frequency: $(FREQ) Hz"
	@echo "Flash: $(FLASH_SIZE)"
	@echo "RAM: $(RAM_SIZE)"
	@echo "LoRaWAN Region: US915 (Costa Rica)"
	@echo "BLE Version: 5.3"

.PHONY: all flash debug clean install-deps config
