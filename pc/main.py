from serial_receiver import SerialReceiver
from packet_processor import PacketProcessor

SERIAL_PORT = '/dev/tty.usbmodem14201'
BAUD_RATE = 115200
SYNC_BYTE = b'\xAA'
RAW_DATA_LENGTH = 14

def main():
    receiver = SerialReceiver(SERIAL_PORT, BAUD_RATE, SYNC_BYTE, RAW_DATA_LENGTH)
    processor = PacketProcessor()

    receiver.set_packet_callback(processor.process_packet)

    receiver.start()

if __name__ == "__main__":
    main()