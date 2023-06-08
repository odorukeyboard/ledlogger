import RPi.GPIO as GPIO
from time import time
from datetime import datetime
from db import Databse

PIN = 9
OUT_PIN = 12
test_db = Databse()


class IrModule:

    def __init__(self):
        self.LED_ON =False
        GPIO.setmode(GPIO.BCM)  # Numbers GPIOs by physical location
        GPIO.setup(PIN, GPIO.IN, pull_up_down=GPIO.PUD_DOWN)
        GPIO.setup(OUT_PIN,GPIO.OUT)

    def binary_aquire(self, pin, duration):
        # aquires data as quickly as possible
        t0 = time()
        results = []
        while (time() - t0) < duration:
            results.append(GPIO.input(pin))
        return results


    def on_ir_receive(self, pinNo, bouncetime=150):
        # when edge detect is called (which requires less CPU than constant
        # data acquisition), we acquire data as quickly as possible
        data = self.binary_aquire(pinNo, bouncetime/1000.0)
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


    def destroy(self):
        GPIO.cleanup()
    
    def get_ir_status(self):
        return self.LED_ON
    
    def start(self):
        try:
            print("Starting IR Listener")
            while True:
                print("Waiting for signal")
                GPIO.wait_for_edge(PIN, GPIO.FALLING)
                code = self.on_ir_receive(PIN)
                if code:
                    print('Input Signal',str(hex(code)))
                    if str(hex(code)) == "0x2fd629d":
                        print('Signal Match Success!!')
                        if self.LED_ON == False:
                            print('LED OFF')
                            GPIO.output(OUT_PIN, True)
                            self.LED_ON = True
                            #now_date = datetime.now().strftime('%Y-%m-%d %H:%M:%S')
                            #test_db.insert(now_date,'OFF')
                            
                        else:
                            print('LED ON')
                            GPIO.output(OUT_PIN, False)
                            self.LED_ON = False
                            #now_date = datetime.now().strftime('%Y-%m-%d %H:%M:%S')
                            #test_db.insert(now_date,'ON')
                            
                            
                else:
                    print("Invalid code")
        except KeyboardInterrupt:
            pass
        except RuntimeError:
            # this gets thrown when control C gets pressed
            # because wait_for_edge doesn't properly pass this on
            pass
        print("Quitting")
        self.destroy()


