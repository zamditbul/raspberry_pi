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

def sleep_start(usr):
    lightoff()
    usr.sleep_start = dt.datetime.now()
    usr.sleep = True



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
    @property
    def sleep_time(self):
        return self.sleep_time

    @sleep_time.setter
    def sleep_time(self, value):
        self.sleep_time=value

def main():
    human = False
    temp = 0
    usr = Info()
    usr.color = hex_to_rgb(usr.hex)
    while True:
        if not usr.sleep: # if not in  sleep mode
            current = GPIO.input(23)
            print("light: ", current)
            if current==1:
                lighton(usr.color)
            elif current==0:
                lightoff()
        fDistance=getDistance()
        #Distance Check
        if temp!=0: # if temp value exists,
            if fDistance - temp > 100: # if the difference is greater than 100
                if human: # switch human value
                    human = False
                else:
                    human = True
        # to compare previous value and current value
        temp = fDistance
        print("distance: ", fDistance)
        #if human:
        # human exists, then after 1 hour, turn off the light

        button.when_pressed= lambda : sleep_start(usr)
        if usr.sleep:
            print(usr.ID)
            print(usr.sleep)
            print(usr.sleep_start)
            print("sleep mode")
            continue
        time.sleep(1)

        while True:
            now = dt.datetime.now()
            td6am = now.replace(hour = 6, minute=0, second=0, microsecond=0)
            if now > td6am:
            #if current time is later than 6am
                if not human:
                    usr.sleep_end = now # end sleep session
                    usr.sleep = False
                print("wake up")
                break
            elif now < td6am and not usr.doNotDisturb:
            # elif current time is earlier than 6am and not doNotDisturb
                if not human:
                    usr. break_count+=1
                    lighton(usr.color)
                print("break out")
                break



if __name__ == "__main__":
    main()
