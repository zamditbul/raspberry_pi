import RPi.GPIO as GPIO
import board
import os
import time
import neopixel
import datetime as dt
from gpiozero import Button


#ultrasonic sensor
usleep = lambda x:time.sleep(x/100000.0)
TP=4
EP=17
GPIO.setmode(GPIO.BCM)
GPIO.setup(TP,GPIO.OUT, initial = GPIO.LOW)
GPIO.setup(EP, GPIO.IN)


#photo resistor
GPIO.setup(23, GPIO.IN)

#neopixel
num_pixels=16
pixel_pin=board.D18
ORDER=neopixel.GRB
pixels = neopixel.NeoPixel(pixel_pin, num_pixels, brightness=0.5,auto_write=False,pixel_order=ORDER)

#button setting
button = Button(21)

# measuring ditance using ultrasonic sensor
def getDistance():
    fDistance=0.0
    nStartTime, nEndTime=0,0
    GPIO.output(TP, GPIO.LOW)
    usleep(2)
    GPIO.output(TP, GPIO.HIGH)
    usleep(10)
    GPIO.output(TP, GPIO.LOW)
    while(GPIO.input(EP)==GPIO.LOW):
        pass
    nStartTime=dt.datetime.now()
    while(GPIO.input(EP)==GPIO.HIGH):
        pass
    nEndTime=dt.datetime.now()
    fDistance = (nEndTime-nStartTime).microseconds/29./2.
    return fDistance

def hex_to_rgb(hex):
    hex = hex.lstrip('#')
    hlen = len(hex)
    return tuple(int(hex[i:i+hlen//3], 16) for i in range(0, hlen, hlen//3))

def lighton(color):
    pixels.fill(color)
    pixels.show()

def lightoff():
    for i in range(num_pixels):
        pixels[i]=(0,0,0,0)
        pixels.show()

class Info():
    def __init__(self):
        stream = os.popen('cat /proc/cpuinfo | grep Serial | awk "{print $3}"')
        self.ID = stream.read()
        self.sleep = False
        self.sleep_start = 0
        self.sleep_end = 0
        self.doNotDisturb = False
        self.hex = '#fff0aa'
        self.color = (255,240,255)
        self.break_count = 0
        self.human = False
        self.human_time = 0
        self.dist = 0

    def sleep_mode(self):
        lightoff()
        self.sleep_start = dt.datetime.now()
        self.sleep = True

    def human_check(self):
        fDistance=getDistance()
        #Distance Check
        if self.dist!=0: # if temp value exists,
            if abs(fDistance - self.dist)  > 50:
                # if the difference is greater than 100
                if self.human: # switch human value
                    self.human = False
                else:
                    self.human = True
                    self.human_time = dt.datetime.now()
        print("distance: ", self.dist, "human: ", self.human, "time: ", self.human_time)
        # to compare previous value and current value
        self.dist = fDistance

def main():
    temp = 0
    usr = Info()
    while True:
        # make usr object
        usr.color = hex_to_rgb(usr.hex)

        # light control by light sensor
        if not usr.sleep: # if not in  sleep mode
            current = GPIO.input(23)
            print("light: ", current)
            if current==1:
                lighton(usr.color)
            elif current==0:
                lightoff()

            usr.human_check()
            if usr.human:
                # human exists, then after 1 hour, turn off the light
                if (dt.datetime.now() - usr.human_time).seconds / 3600 > 1:
                    usr.sleep_mode()

            button.when_pressed= lambda : usr.sleep_mode()

        else: # while sleeping
            now = dt.datetime.now()
            if now.hour<6:
                td6am = now.replace(day = now.day, hour = 6, minute=0, second=0, microsecond=0)
            else:
                td6am = now.replace(day = now.day+1, hour = 6, minute=0, second=0, microsecond=0)
            while True: #wait until end of sleep
                now = dt.datetime.now()
                print(now, td6am)
                usr.human_check()
                print(usr.human)
                if not usr.human:
                    if now > td6am:
                    #if current time is later than 6am
                        usr.sleep_end = now # end sleep session
                        usr.sleep = False
                        print("wake up")
                        break
                    elif now < td6am and not usr.doNotDisturb:
                    # elif current time is earlier than 6am and not doNotDisturb
                        usr.break_count+=1
                        # light on until human come back
                        while not usr.human:
                            lighton(usr.color)
                            usr.human_check()
                            time.sleep(1)
                        lightoff()
                        print("break out")
                        break
                time.sleep(1)
        time.sleep(1)


if __name__ == "__main__":
    main()
