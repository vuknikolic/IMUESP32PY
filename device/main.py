import micropython, esp, gc, time
from machine import Pin
from mpu6050 import MPU

esp.osdebug(None)
gc.collect()

raw_data = None

key = Pin(0, Pin.IN, Pin.PULL_UP)  	# Reset button
led = Pin(15, Pin.OUT)  			# On-board LED

def process_interrupt(raw):
    global send_data_flag, raw_data
    raw_data = raw

mpu = MPU(scl_pin=36, sda_pin=38, interrupt_pin=40, interrupt_handler=process_interrupt)

try:
    led.value(1)
    prev_time = time.ticks_us()
    while True:

        sys.stdout.write("1000Hz data\n")

        if key.value() == 0:
            mpu.deinitialize()
            break
finally:
    led.value(0)
