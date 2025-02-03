class PacketProcessor:
    def __init__(self):
        # Konstante za konverziju
        self.ACCEL_SCALE = 16384.0  # Za ±2g
        self.GYRO_SCALE = 131.0     # Za ±250°/s

        self.accel_x_g = 0.0
        self.accel_y_g = 0.0
        self.accel_z_g = 0.0
        self.temp_c = 0.0
        self.gyro_x_dps = 0.0
        self.gyro_y_dps = 0.0
        self.gyro_z_dps = 0.0
        self.time_diff = 0

    def process_packet(self, packet: bytes):
        """Obradi raw paket i prikaži stvarne vrednosti."""
        if len(packet) != 16:
            print("Invalid packet length!")
            return

        # Parsiranje raw podataka
        accel_x = self._bytes_to_int16_s(packet[0], packet[1])
        accel_y = self._bytes_to_int16_s(packet[2], packet[3])
        accel_z = self._bytes_to_int16_s(packet[4], packet[5])

        temp = self._bytes_to_int16_s(packet[6], packet[7])

        gyro_x = self._bytes_to_int16_s(packet[8], packet[9])
        gyro_y = self._bytes_to_int16_s(packet[10], packet[11])
        gyro_z = self._bytes_to_int16_s(packet[12], packet[13])

        self.time_diff = self._bytes_to_uint16(packet[14],packet[15])

        # Konverzija u stvarne vrednosti
        self.accel_x_g = accel_x / self.ACCEL_SCALE
        self.accel_y_g = accel_y / self.ACCEL_SCALE
        self.accel_z_g = accel_z / self.ACCEL_SCALE

        self.temp_c = (temp / 340.0) + 36.53

        self.gyro_x_dps = gyro_x / self.GYRO_SCALE
        self.gyro_y_dps = gyro_y / self.GYRO_SCALE
        self.gyro_z_dps = gyro_z / self.GYRO_SCALE

    def _bytes_to_uint16(self,high_byte: int, low_byte: int) -> int:
        return (high_byte << 8) | low_byte

    def _bytes_to_int16_s(self,high_byte: int, low_byte: int) -> int:
        value = (high_byte << 8) | low_byte
        return value - 65536 if value > 32767 else value