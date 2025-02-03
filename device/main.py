import micropython, esp, gc, time, uos, sys
from machine import Pin
from mpu6050 import MPU

esp.osdebug(None)

# Onemogući automatski Garbage Collector i postavi niži threshold
gc.disable()
gc.threshold(1024)  # Povećaj frekvenciju GC

# gc.mem_free()  # Vraća broj slobodnih bajtova u heap-u
# gc.mem_alloc() # Vraća broj alociranih bajtova u heap-u
# gc.compact() # defragmentacija heap-a

# Alociraj bafer za hitne izuzetke
micropython.alloc_emergency_exception_buf(100)
gc.collect()  # Inicijalno čišćenje memorije

# Prealociraj bafer za paket (16 bajtova)
PACKET_SIZE = 17 # sync + 16 bajtova podataka
packet_buffer = bytearray(PACKET_SIZE)  # Statički bafer za paket

# Globalne promenljive
raw_data = None
send_data_flag = False  # Zastavica za slanje podataka
last_time = time.ticks_us()  # Vreme poslednjeg očitavanja (u mikrosekundama)

# Konfiguracija pinova
key = Pin(0, Pin.IN, Pin.PULL_UP)  	# Reset button
led = Pin(15, Pin.OUT)  			# On-board LED

# Sync byte (jedinstven bajt za označavanje početka paketa)
SYNC_BYTE = b'\xAA'

def process_interrupt(raw):
    global send_data_flag, raw_data, last_time
    raw_data = raw
    send_data_flag = True  # Postavite zastavicu za slanje podataka

mpu = MPU(scl_pin=36, sda_pin=38, interrupt_pin=40, interrupt_handler=process_interrupt)

try:
    led.value(1)
    while True:
        if send_data_flag:  # Proverite da li je zastavica postavljena
            if raw_data is not None:
                
                # Izračunajte proteklo vreme u mikrosekundama od poslednjeg očitavanja
                current_time = time.ticks_us()
                time_diff = time.ticks_diff(current_time, last_time)
                last_time = current_time
                
                packet_buffer[0] = SYNC_BYTE[0]  # SYNC byte (0xAA)
                packet_buffer[1:15] = raw_data[:14]  # Prvih 14 bajtova raw_data
                packet_buffer[15] = (time_diff >> 8) & 0xFF  # High byte (big-endian)
                packet_buffer[16] = time_diff & 0xFF         # Low byte (big-endian)

                # Pošalji paket
                sys.stdout.buffer.write(packet_buffer)  # Ispis paketa u binarnom obliku

                # Resetuj raw_data nakon slanja
                raw_data = None

                # Ručno pokreni Garbage Collector odmah nakon slanja podataka
                gc.collect()

            # Resetuj zastavicu
            send_data_flag = False

        if key.value() == 0:
            mpu.deinitialize()
            break
finally:
    led.value(0)