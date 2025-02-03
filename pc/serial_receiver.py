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
        # Staticki alociran bafer od 100 bajtova
        self.capacity = 100
        self.buffer = bytearray(self.capacity)
        self.buf_len = 0  # Trenutni broj bajtova u baferu
        self.packet_callback = None
        self._running = False

    def set_packet_callback(self, callback: Callable[[bytes], None]):
        self.packet_callback = callback

    def start(self):
        self._running = True
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

    def stop(self):
        self._running = False

    def _read_loop(self):
        while self._running:
            raw_data = self.ser.read(self.ser.in_waiting or 1)
            if raw_data:
                self._write_to_buffer(raw_data)
                self._process_buffer()

    def _write_to_buffer(self, data: bytes):
        data_len = len(data)
        free_space = self.capacity - self.buf_len
        if data_len > free_space:
            # Ako nema dovoljno mesta, premeštamo preostale bajtove na početak
            if self.buf_len > 0:
                self.buffer[:self.buf_len] = self.buffer[self.capacity - self.buf_len:self.capacity]
            free_space = self.capacity - self.buf_len
            if data_len > free_space:
                data = data[:free_space]
                data_len = len(data)
        self.buffer[self.buf_len:self.buf_len+data_len] = data
        self.buf_len += data_len

    def _process_buffer(self):
        packet_length = 1 + self.raw_data_length
        i = 0
        while i < self.buf_len:
            if self.buffer[i] == self.sync_byte[0]:
                if self.buf_len - i >= packet_length:
                    packet_view = memoryview(self.buffer)[i+1:i+packet_length]
                    if self.packet_callback:
                        self.packet_callback(packet_view)
                    i += packet_length
                    continue
                else:
                    break
            else:
                i += 1
        if i > 0:
            remaining = self.buf_len - i
            self.buffer[:remaining] = self.buffer[i:self.buf_len]
            self.buf_len = remaining
