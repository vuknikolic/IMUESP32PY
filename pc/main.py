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

                while len(buffer) > 0:
                    sync_index = buffer.find(SYNC_BYTE)
                    if sync_index == -1:
                        break  # nije bilo SYNC-a

                    if len(buffer) >= sync_index + 1 + len(raw_data):  # prilagodi duzinu raw_data
                        packet = buffer[sync_index:sync_index + 1 + len(raw_data)]
                        buffer = buffer[sync_index + 1 + len(raw_data):]  # ukloni obradjene bajtove

                        raw_data = packet[1:]  # preskoci SYNC bajt
                        print("Received raw data (hex):", raw_data.hex())

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