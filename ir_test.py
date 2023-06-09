import RPi.GPIO as GPIO
from time import time
import json
from datetime import datetime
from app.models.db import get_db, t_led, t_report_definition
import requests

#from db import Databse

PIN = 9
OUT_PIN = 12
LED_ON =False

def setup():
    GPIO.setmode(GPIO.BCM)  # Numbers GPIOs by physical location
    GPIO.setup(PIN, GPIO.IN, pull_up_down=GPIO.PUD_DOWN)
    GPIO.setup(OUT_PIN,GPIO.OUT)


def binary_aquire(pin, duration):
    # aquires data as quickly as possible
    t0 = time()
    results = []
    while (time() - t0) < duration:
        results.append(GPIO.input(pin))
    return results


def on_ir_receive(pinNo, bouncetime=150):
    # when edge detect is called (which requires less CPU than constant
    # data acquisition), we acquire data as quickly as possible
    data = binary_aquire(pinNo, bouncetime/1000.0)
    if len(data) < bouncetime:
        return
    rate = len(data) / (bouncetime / 1000.0)
    pulses = []
    i_break = 0
    # detect run lengths using the acquisition rate to turn the times in to microseconds
    for i in range(1, len(data)):
        if (data[i] != data[i-1]) or (i == len(data)-1):
            pulses.append((data[i-1], int((i-i_break)/rate*1e6)))
            i_break = i
    # decode ( < 1 ms "1" pulse is a 1, > 1 ms "1" pulse is a 1, longer than 2 ms pulse is something else)
    # does not decode channel, which may be a piece of the information after the long 1 pulse in the middle
    outbin = ""
    for val, us in pulses:
        if val != 1:
            continue
        if outbin and us > 2000:
            break
        elif us < 1000:
            outbin += "0"
        elif 1000 < us < 2000:
            outbin += "1"
    try:
        return int(outbin, 2)
    except ValueError:
        # probably an empty code
        return None


def destroy():
    GPIO.cleanup()

def insert_data(state):
    url = "http://0.0.0.0:5000/led/save"
    headers = {'Content-type': 'application/json', 'Accept': 'text/plain'}
    data = dict()
    req_data = dict()
    req_data['id'] = ''
    req_data['date'] = ''
    req_data['state'] = state
    data['led'] = req_data
    requests.post(url,headers=headers, data=json.dumps(data))
    '''
    with db_engine.begin() as connection:
        values = dict()
        values['state'] = state
        values['date'] = datetime.now()
        connection.execute(
            t_led.insert()
            .values(**values)
        )
        '''

if __name__ == "__main__":
    setup()
    try:
        print("Starting IR Listener")
        while True:
            print("Waiting for signal")
            GPIO.wait_for_edge(PIN, GPIO.FALLING)
            code = on_ir_receive(PIN)
            if code:
                print('Input Signal',str(hex(code)))
                if str(hex(code)) == "0x2fd629d":
                    print('Signal Match Success!!')
                    if LED_ON == False:
                        print('LED OFF')
                        GPIO.output(OUT_PIN, True)
                        LED_ON = True
                        #now_date = datetime.now().strftime('%Y-%m-%d %H:%M:%S')
                        #test_db.insert(now_date,'OFF')
                        insert_data('OFF')
                        
                    else:
                        print('LED ON')
                        GPIO.output(OUT_PIN, False)
                        LED_ON = False
                        #now_date = datetime.now().strftime('%Y-%m-%d %H:%M:%S')
                        #test_db.insert(now_date,'ON')
                        insert_data('ON')
                        
                        
            else:
                print("Invalid code")
    except KeyboardInterrupt:
        pass
    except RuntimeError:
        # this gets thrown when control C gets pressed
        # because wait_for_edge doesn't properly pass this on
        pass
    print("Quitting")
    destroy()