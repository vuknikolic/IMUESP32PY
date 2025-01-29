import serial

SERIAL_PORT = '/dev/tty.usbmodem14201'
BAUD_RATE = 115200

SYNC_BYTE = b'\xAA'


def main():
    try:
        ser = serial.Serial(SERIAL_PORT, BAUD_RATE, timeout=1)

        buffer = bytearray()

        while True:
            raw_data = ser.read(ser.in_waiting or 1)
            if raw_data:
                buffer.extend(raw_data)

                while SYNC_BYTE in buffer:
                    sync_index = buffer.find(SYNC_BYTE)

                    # odbaci bajtove pre SYNC-a
                    if sync_index > 0: 
                        buffer = buffer[sync_index:]

                    # da li imamo jos jedan SYNC na za kraj
                    next_sync_index = buffer.find(SYNC_BYTE, sync_index + 1)

                    if next_sync_index != -1:
                        # ceo paket izmedju dva SYNC-a
                        packet = buffer[sync_index + 1:next_sync_index]
                        print("Received raw data (hex):", packet.hex())

                        # odbaci obradjne bajtove
                        buffer = buffer[next_sync_index:]
                    else:
                        # nema ceo paket, cekaj
                        break

    except serial.SerialException as e:
        print(f"Error opening serial port: {e}")
    except KeyboardInterrupt:
        print("\nProgram terminated by user.")
    finally:
        if 'ser' in locals() and ser.is_open:
            ser.close()
            print("Serial port closed.")

if __name__ == "__main__":
    main()
