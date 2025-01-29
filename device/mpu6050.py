from machine import Pin, SoftI2C

class MPU:
    ADDRESS = 0x68

    PWR_MGMT_1 = 0x6B
    ACCEL_CONFIG = 0x1C
    GYRO_CONFIG = 0x1B
    CONFIG = 0x1A
    INT_ENABLE = 0x38
    SMPLRT_DIV = 0x19
    INT_PIN_CFG = 0x37
    ACCEL_XOUT0 = 0x3B

    ACCEL_RANGE_2G = 0x00
    GYRO_RANGE_250DEG = 0x00

    def __init__(self, scl_pin, sda_pin, interrupt_pin, interrupt_handler):
        self.i2c = SoftI2C(scl=Pin(scl_pin), sda=Pin(sda_pin), freq=400000)
        self.interrupt_pin = Pin(interrupt_pin, Pin.IN, Pin.PULL_UP)
        self.interrupt_handler = interrupt_handler

        self.initialize_device()
        self.interrupt_pin.irq(trigger=Pin.IRQ_FALLING, handler=self.handle_interrupt)

    def initialize_device(self):
        self.i2c.start()
        self.i2c.writeto(self.ADDRESS, bytearray([self.PWR_MGMT_1, 0x00]))  
        self.i2c.writeto(self.ADDRESS, bytearray([self.ACCEL_CONFIG, self.ACCEL_RANGE_2G]))
        self.i2c.writeto(self.ADDRESS, bytearray([self.GYRO_CONFIG, self.GYRO_RANGE_250DEG]))
        self.i2c.writeto(self.ADDRESS, bytearray([self.CONFIG, 0x00]))  
        self.i2c.writeto(self.ADDRESS, bytearray([self.INT_ENABLE, 0x01]))  
        self.i2c.writeto(self.ADDRESS, bytearray([self.SMPLRT_DIV, 0x07]))  
        self.i2c.writeto(self.ADDRESS, bytearray([self.INT_PIN_CFG, 0x10])) 
        self.i2c.stop()

    def deinitialize(self):
        self.interrupt_pin.irq(handler=None) 
        self.i2c.stop()

    def handle_interrupt(self, pin):
        raw = self.i2c.readfrom_mem(self.ADDRESS, self.ACCEL_XOUT0, 14)
        self.interrupt_handler(raw)
