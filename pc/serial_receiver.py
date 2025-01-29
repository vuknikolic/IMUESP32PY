import serial
import time
from typing import Callable

class SerialReceiver:
    def __init__(self, port: str, baud_rate: int, sync_byte: bytes, raw_data_length: int):
        self.port = port
        self.baud_rate = baud_rate
        self.sync_byte = sync_byte
        self.raw_data_length = raw_data_length
        self.ser = None
        self.buffer = bytearray()
        self.packet_callback = None

    def set_packet_callback(self, callback: Callable[[bytes], None]):
        self.packet_callback = callback

    def start(self):
        try:
            self.ser = serial.Serial(self.port, self.baud_rate, timeout=1)
            self._read_loop()
        except serial.SerialException as e:
            print(f"Error opening serial port: {e}")
        except KeyboardInterrupt:
            print("\nSerial receiver terminated by user.")
        finally:
            if self.ser and self.ser.is_open:
                self.ser.close()
                print("Serial port closed.")

    def _read_loop(self):
        while True:
            raw_data = self.ser.read(self.ser.in_waiting or 1)
            if raw_data:
                self.buffer.extend(raw_data)
                self._process_buffer()

    def _process_buffer(self):
        while True:
            sync_index = self.buffer.find(self.sync_byte)
            if sync_index == -1:
                break  # # nije bilo SYNC-a, cekaj

            if len(self.buffer) >= sync_index + 1 + self.raw_data_length:
                # ima dovoljno za ceo paket (SYNC_BYTE + 14 bajtova)
                packet = self.buffer[sync_index + 1 : sync_index + 1 + self.raw_data_length]
                if self.packet_callback:
                    self.packet_callback(packet)  # callback sa primljenim paketom

                # Odbaci obrađene bajtove
                self.buffer = self.buffer[sync_index + 1 + self.raw_data_length :]
            else:
                break  # nema ceo paket, cekaj