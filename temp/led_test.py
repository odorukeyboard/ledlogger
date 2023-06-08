import RPi.GPIO as GPIO
import time
from db import Databse
from datetime import datetime

test_db = Databse()

GPIO.setmode(GPIO.BCM)
GPIO.setup(24,GPIO.OUT)
count = 0

while 1:
    GPIO.output(24, False)
    print('LED OFF')
    now_date = datetime.now().strftime('%Y-%m-%d %H:%M:%S')
    test_db.insert(now_date,'OFF')
    time.sleep(2)
    GPIO.output(24, True)
    print('LED ON')
    now_date = datetime.now().strftime('%Y-%m-%d %H:%M:%S')
    test_db.insert(now_date,'ON')
    time.sleep(2)
    count = count + 1
    if count > 10:
        break
    