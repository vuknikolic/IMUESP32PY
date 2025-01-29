import serial

SERIAL_PORT = '/dev/tty.usbmodem14201'
BAUD_RATE = 115200

SYNC_BYTE = b'\xAA'
RAW_DATA_LENGTH = 14

def main():
    try:
        ser = serial.Serial(SERIAL_PORT, BAUD_RATE, timeout=1)

        buffer = bytearray()

        while True:
            raw_data = ser.read(ser.in_waiting or 1)
            if raw_data:
                buffer.extend(raw_data)

                while True:
                    sync_index = buffer.find(SYNC_BYTE)

                    if sync_index == -1:  
                        break  # nije bilo SYNC-a, cekaj

                    if len(buffer) >= sync_index + 1 + RAW_DATA_LENGTH:
                        # ima dovoljno za ceopaket (SYNC_BYTE + 14 bajtova)
                        packet = buffer[sync_index + 1 : sync_index + 1 + RAW_DATA_LENGTH]
                        
                        print("Received raw data (hex):", packet.hex())

                        # odbaci obradjne bajtove
                        buffer = buffer[sync_index + 1 + RAW_DATA_LENGTH:]
                    else:
                        break  # nema ceo paket, cekaj

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
