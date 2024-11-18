import micropython, esp, gc 
from machine import Pin, SoftI2C

esp.osdebug(None)
gc.collect()

key = Pin(0,Pin.IN, Pin.PULL_UP) # reset taster
led = Pin(15,Pin.OUT) # on-board led

# MPU adresa
ADDRESS = 0x68
    
# Scale Modifiers
ACCEL_SCALE_MODIFIER_2G = 16384.0
ACCEL_SCALE_MODIFIER_4G = 8192.0
ACCEL_SCALE_MODIFIER_8G = 4096.0
ACCEL_SCALE_MODIFIER_16G = 2048.0
 
GYRO_SCALE_MODIFIER_250DEG = 131.0
GYRO_SCALE_MODIFIER_500DEG = 65.5
GYRO_SCALE_MODIFIER_1000DEG = 32.8
GYRO_SCALE_MODIFIER_2000DEG = 16.4

# Pre-defined ranges
ACCEL_RANGE_2G = 0x00
ACCEL_RANGE_4G = 0x08
ACCEL_RANGE_8G = 0x10
ACCEL_RANGE_16G = 0x18

GYRO_RANGE_250DEG = 0x00
GYRO_RANGE_500DEG = 0x08
GYRO_RANGE_1000DEG = 0x10
GYRO_RANGE_2000DEG = 0x18

# MPU6050 registri
PWR_MGMT_1 = 0x6B
PWR_MGMT_2 = 0x6C
  
# raw data 14 bajtova nema potrebe da se uzima pojedinacno iz svakog registra
ACCEL_XOUT0 = 0x3B
ACCEL_XOUT1 = 0x3C
ACCEL_YOUT0 = 0x3D
ACCEL_YOUT1 = 0x3E
ACCEL_ZOUT0 = 0x3F
ACCEL_ZOUT1 = 0x40
TEMP_OUT0 = 0x41
TEMP_OUT1 = 0x42
GYRO_XOUT0 = 0x43
GYRO_XOUT1 = 0x44
GYRO_YOUT0 = 0x45
GYRO_YOUT1 = 0x46
GYRO_ZOUT0 = 0x47
GYRO_ZOUT1 = 0x48

CONFIG = 0x1A
GYRO_CONFIG = 0x1B
ACCEL_CONFIG = 0x1C


i2c = SoftI2C(scl=Pin(36), sda=Pin(38), freq=400000)
i2c.start()
i2c.writeto(ADDRESS, bytearray([PWR_MGMT_1, 0x00]))
i2c.writeto(ADDRESS, bytearray([ACCEL_CONFIG, ACCEL_RANGE_2G]))
i2c.writeto(ADDRESS, bytearray([GYRO_CONFIG, GYRO_RANGE_250DEG]))
i2c.writeto(ADDRESS, bytearray([CONFIG, 0x00]))
i2c.stop()

loop = True
led.value(1)

while loop:

    i2c.start()
    raw = i2c.readfrom_mem(ADDRESS, ACCEL_XOUT0, 14)
    i2c.stop()
    
    print(raw)
    
    if key.value() == 0:
        loop = False

led.value(0)
