import RPi.GPIO as GPIO
from time import time
from datetime import datetime

class Led_module:

    def __init__(self):
        self.pin = False
        self.state = 'Off'
        GPIO.setmode(GPIO.BCM)
        GPIO.setup(24,GPIO.OUT)

    def set_led_off(self):
        self.state = 'Off'

    def set_led_on(self):
        self.state = 'On' 

    def get_led_state(self):
        return self.state