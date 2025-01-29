import micropython, esp, gc, time, uos, sys
from machine import Pin
from mpu6050 import MPU

esp.osdebug(None)
gc.collect()

raw_data = None
send_data_flag = False  

key = Pin(0, Pin.IN, Pin.PULL_UP)  	# Reset button
led = Pin(15, Pin.OUT)  			# On-board LED

# Sync byte 
SYNC_BYTE = b'\xAA'

def process_interrupt(raw):
    global send_data_flag, raw_data
    raw_data = raw
    send_data_flag = True 

mpu = MPU(scl_pin=36, sda_pin=38, interrupt_pin=40, interrupt_handler=process_interrupt)

try:
    led.value(1)
    while True:
        if send_data_flag:  
            if raw_data is not None:                
                packet = SYNC_BYTE + raw_data if isinstance(raw_data, (bytes, bytearray)) else SYNC_BYTE + bytes(raw_data)
                sys.stdout.buffer.write(packet)  
                raw_data = None  
            send_data_flag = False

        if key.value() == 0:
            mpu.deinitialize()
            break
finally:
    led.value(0)