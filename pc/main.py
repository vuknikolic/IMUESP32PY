import serial

ser = serial.Serial('/dev/tty.usbmodem14201', 115200)
while True:
    data = ser.readline()
    print(data)