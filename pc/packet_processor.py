class PacketProcessor:
    def process_packet(self, packet: bytes):
        print(f"Received raw data (hex): {packet.hex()}")