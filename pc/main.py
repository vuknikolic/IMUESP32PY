import serial  # type: ignore
import time

SERIAL_PORT = '/dev/tty.usbmodem14201'
BAUD_RATE = 115200

SYNC_BYTE = b'\xAA'
RAW_DATA_LENGTH = 14

def main():
    try:
        ser = serial.Serial(SERIAL_PORT, BAUD_RATE, timeout=1)

        buffer = bytearray()
        packet_count = 0
        start_time = time.time()
        last_packet_time = start_time
        time_differences = []  # Lista za čuvanje vremenskih razlika između paketa

        while True:
            raw_data = ser.read(ser.in_waiting or 1)
            if raw_data:
                buffer.extend(raw_data)

                while True:
                    sync_index = buffer.find(SYNC_BYTE)

                    if sync_index == -1:  
                        break  # nije bilo SYNC-a, cekaj

                    if len(buffer) >= sync_index + 1 + RAW_DATA_LENGTH:
                        # ima dovoljno za ceo paket (SYNC_BYTE + 14 bajtova)
                        packet = buffer[sync_index + 1 : sync_index + 1 + RAW_DATA_LENGTH]
                        
                        # Uvecaj brojac paketa
                        packet_count += 1

                        # Izracunaj vreme izmedju paketa
                        current_time = time.time()
                        time_diff = current_time - last_packet_time
                        time_differences.append(time_diff)
                        last_packet_time = current_time

                        # print("Received raw data (hex):", packet.hex())

                        # Odbaci obradjene bajtove
                        buffer = buffer[sync_index + 1 + RAW_DATA_LENGTH:]
                    else:
                        break  # nema ceo paket, cekaj

            # Proveri proteklo vreme
            elapsed_time = time.time() - start_time
            if elapsed_time >= 60:  # Proveri da li je proteklo 60 sekundi
                packets_per_minute = packet_count / (elapsed_time / 60)
                print(f"Packets per minute: {packets_per_minute:.2f}")

                if time_differences:
                    min_time = min(time_differences)
                    max_time = max(time_differences)
                    avg_time = sum(time_differences) / len(time_differences)
                    print(f"Min time between packets: {min_time:.6f} s")
                    print(f"Max time between packets: {max_time:.6f} s")
                    print(f"Avg time between packets: {avg_time:.6f} s")
                else:
                    print("No packets received in the last minute.")

                # Resetuj brojac i vreme
                packet_count = 0
                time_differences = []
                start_time = time.time()

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