"""
Robot Pinout & Wiring Configuration

Format:
VARIABLE_NAME = BCM_GPIO_INT  # [Pi Physical Pin] -Wire Color-> [Destination Header/Pin]

Format gotten from chatGPT. Mine was ugly af and I had problems understanding it post writing. 
"""

# ==========================================
# Power & Logic References (Hardware Only)
# ==========================================
# (These pins do not have GPIO numbers; documented for wiring reference)
# [Pi Pin 1]  -Red->    J12 3V3  (Logic reference)
# [Pi Pin 2]  -Red->    J2 5V    (Pi 5V power from RovMotPow)
# [Pi Pin 6]  -Black->  J2 GND   (System common ground)
# [Pi Pin 9]  -Black->  Breadboard (-) Rail
# [Pi Pin 17] -Red->    Breadboard (+) Rail (3.3V)

# ==========================================
# Motor Driver (DRV8833 Sleep Control)
# ==========================================
PIN_SLP = 17                  # [Pi Pin 11] -Purple-> J12 SLP

# ==========================================
# Left Motor (MOTB / J6)
# ==========================================
PIN_MOTOR_LEFT_FWD = 18       # [Pi Pin 35] -Orange-> MOTB Pin 1 (BIN1)
PIN_MOTOR_LEFT_BWD = 19       # [Pi Pin 12] -White->  MOTB Pin 2 (BIN2)
PIN_ENC_LEFT_A = 21           # [Pi Pin 38] -Green->  MOTB Pin 3 (C1)
PIN_ENC_LEFT_B = 20           # [Pi Pin 40] -Yellow-> MOTB Pin 4 (C2)

# ==========================================
# Right Motor (MOTA / J3)
# ==========================================
PIN_MOTOR_RIGHT_FWD = 13      # [Pi Pin 33] -Orange-> MOTA Pin 1 (AIN1)
PIN_MOTOR_RIGHT_BWD = 12      # [Pi Pin 32] -White->  MOTA Pin 2 (AIN2)
PIN_ENC_RIGHT_A = 5           # [Pi Pin 29] -Green->  MOTA Pin 3 (C1)
PIN_ENC_RIGHT_B = 6           # [Pi Pin 31] -Yellow-> MOTA Pin 4 (C2)

# ==========================================
# I2C Bus & Sensors
# ==========================================
# Shared Bus Pins on Pi:
# [Pi Pin 3] (GPIO 2 - SDA) -Blue->  Breadboard Row 23 (Col J)
# [Pi Pin 5] (GPIO 3 - SCL) -Green-> Breadboard Row 22 (Col J)

I2C_SDA = 2                   # BCM GPIO 2
I2C_SCL = 3                   # BCM GPIO 3

# I2C Device Addresses
I2C_ADDR_COLOR = 0x29         # TCS34725 Color Sensor
I2C_ADDR_OLED  = 0x3C         # SSD1306 Display
I2C_ADDR_IMU   = 0x68         # ICM-20948 9-Axis IMU (AD0 left open/GND)

#==========================================
# SPI Bus & MCP3008 ADC (Analog Distance)
# ==========================================
# Hardware SPI0 Pins:
SPI_MOSI = 10                 # [Pi Pin 19] -> MCP3008 Pin 11 (DIN)
SPI_MISO = 9                  # [Pi Pin 21] -> MCP3008 Pin 12 (DOUT)
SPI_SCLK = 11                 # [Pi Pin 23] -> MCP3008 Pin 13 (CLK)
SPI_CE0  = 8                  # [Pi Pin 24] -> MCP3008 Pin 10 (CS/SHDN)

# MCP3008 Analog Channels:
ADC_CH_IR_DISTANCE = 0        # MCP3008 Pin 1 (CH0) <- Yellow wire from Sharp IR sensor

# ==========================================
# Breadboard Layout Reference
# ==========================================
# Positive Rail (+): 3.3V from Pi Pin 17
#   - OLED VCC
#   - TCS34725 3V3 (Purple wire)
#   - ICM-20948 VCC (Red wire from 4-pin plug)
#   - MCP3008 Pin 16 (VDD) & Pin 15 (VREF)
#
# Negative Rail (-): GND from Pi Pin 9
#   - OLED GND
#   - TCS34725 GND (Brown wire)
#   - ICM-20948 GND (Black wire from 4-pin plug)
#   - MCP3008 Pin 9 (DGND) & Pin 14 (AGND)
#   - GP2Y0A21YK0F IR Ground (Black wire)
#
# Row 22 (SCL):
#   - Pi Pin 5 (Green) [Col J], OLED SCL, TCS SCL (Grey), ICM SCL (Yellow)
#
# Row 23 (SDA):
#   - Pi Pin 3 (Blue) [Col J], OLED SDA, TCS SDA (Blue), ICM SDA (Blue)
#
# Sharp GP2Y0A21YK0F Sensor:
#   - Red:    5V Power (RovMotPow 5V / Pi Pin 4)
#   - Black:  Negative Rail (-)
#   - Yellow: MCP3008 Pin 1 (CH0)
