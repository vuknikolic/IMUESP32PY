class PacketProcessor:
    def __init__(self):
        # Konstante za konverziju
        self.ACCEL_SCALE = 16384.0  # Za ±2g
        self.GYRO_SCALE = 131.0     # Za ±250°/s

    def process_packet(self, packet: bytes):
        """Obradi raw paket i prikaži stvarne vrednosti."""
        if len(packet) != 14:
            print("Invalid packet length!")
            return

        # Parsiranje raw podataka
        accel_x = self._bytes_to_int(packet[0], packet[1])
        accel_y = self._bytes_to_int(packet[2], packet[3])
        accel_z = self._bytes_to_int(packet[4], packet[5])

        temp = self._bytes_to_int(packet[6], packet[7])

        gyro_x = self._bytes_to_int(packet[8], packet[9])
        gyro_y = self._bytes_to_int(packet[10], packet[11])
        gyro_z = self._bytes_to_int(packet[12], packet[13])

        # Konverzija u stvarne vrednosti
        accel_x_g = accel_x / self.ACCEL_SCALE
        accel_y_g = accel_y / self.ACCEL_SCALE
        accel_z_g = accel_z / self.ACCEL_SCALE

        temp_c = (temp / 340.0) + 36.53

        gyro_x_dps = gyro_x / self.GYRO_SCALE
        gyro_y_dps = gyro_y / self.GYRO_SCALE
        gyro_z_dps = gyro_z / self.GYRO_SCALE

        print("Accelerometer (g): X={:.2f}, Y={:.2f}, Z={:.2f}".format(accel_x_g, accel_y_g, accel_z_g))
        # print("Temperature (°C): {:.2f}".format(temp_c))
        # print("Gyroscope (°/s): X={:.2f}, Y={:.2f}, Z={:.2f}".format(gyro_x_dps, gyro_y_dps, gyro_z_dps))

    def _bytes_to_int(self, high_byte: int, low_byte: int) -> int:
        value = (high_byte << 8) | low_byte
        if value > 32767:  # provera za negativne vrednosti (two's complement)
            value -= 65536
        return value