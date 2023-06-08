import serial

class ArduSerial:

    def __init__(self):
        self.port = '/dev/ttyACM0'
        self.brate = 9600 #boudrate
        self.seri = serial.Serial(self.port, baudrate = self.brate, timeout = None)

    def get_data(self):
        if self.seri.in_waiting != 0 :
            content = self.seri.readline()
            print(content[:-2].decode())
            return content[:-2].decode()
