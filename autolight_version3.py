import RPi.GPIO as GPIO
import board
import os
import time
import neopixel
import datetime as dt
from gpiozero import Button
import paho.mqtt.client as mqtt
import json

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
        self.serial = stream.read().split()[2]
        self.user_id = 'null'
        self.sleep = False
        self.sleep_start = 0
        self.sleep_end = 0
        self.doNotDisturb = False
        self.color = (255,240,255)
        self.break_count = 0
        self.human = False
        self.human_time = 0
        self.dist = 0
        self.desired_sleep=dt.datetime(2021,11,29,23,59,59)
        self.desired_wake=dt.datetime(2021,11,30,6,0,0)

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

# mqtt functions

def strfdelta(tdelta):
    d={"D":tdelta.days}
    hours, rem= divmod(tdelta.seconds, 3600)
    minutes, seconds = divmod(rem,60)

    d['H']='{:02d}'.format(hours)
    d['M']='{:02d}'.format(minutes)
    #if d['D']>0:
    #    d['H'] = int(d['H'])+int(d['D'])*24
    return "{}:{}".format(d['H'], d['M'])


def on_message(client, userdata, message):
    print("Received message: {}, {}".format(message.topic, message.payload))
    global user_id, color, doNotDisturb, sleep, wake_up, setting
    if len(message.payload) <200:
        user_id = str(message.payload).split("'")[1]
        setting=False
    else:
        setting= True
        setting_info = (json.loads(message.payload))
        user_id = setting_info["user_id"]
        color = hex_to_rgb(setting_info["device"]["color"])
        doNotDisturb=setting_info["device"]["doNotDisturb"]
        sleep = dt.datetime.strptime(setting_info["device"]["sleep"], '%H:%M:%S')
        wake_up = dt.datetime.strptime(setting_info["device"]["wake_up"], '%H:%M:%S')
    client.disconnect()

def main():
    temp = 0
    usr = Info()

    # mqtt setting
    client = mqtt.Client()
    client.on_message = on_message
    client.connect('3.94.177.16', 1883)

    # user_id
    print(usr.serial)
    client.subscribe("setting/{}".format(usr.serial))
    client.loop_forever()
    usr.user_id=user_id
    if setting:
        usr.color = color
        if doNotDisturb=="true":
            usr.doNotDisturb =True
        usr.desired_sleep = sleep
        usr.desired_wake = wake_up
        print(usr.user_id, usr.color, usr.desired_sleep)
    while True:
        client.connect('3.94.177.16', 1883)
        # make usr object
        #usr.color = hex_to_rgb(usr.hex)
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

            # after desired sleep time, start sleep_mode
            now = dt.datetime.now()
            usr.desired_sleep = usr.desired_sleep.replace(year = now.year, month = now.month, day = now.day)
            if now>=usr.desired_sleep:
                print('sleep start', usr.desired_sleep)
                usr.sleep_mode()
        else: # while sleeping
            now = dt.datetime.now()
            usr.desired_wake = usr.desired_wake.replace(year = usr.sleep_start.year, month= usr.sleep_start.month, day=usr.sleep_start.day+1)
            #if now.hour<6:
            #    td6am = now.replace(day = now.day, hour = 6, minute=0, second=0, microsecond=0)
            #else:
            #    td6am = now.replace(day = now.day+1, hour = 6, minute=0, second=0, microsecond=0)
            while True: #wait until end of sleep
                now = dt.datetime.now()

                usr.human_check()
                print(usr.human)
                if not usr.human:
                    if now > usr.desired_wake:
                    #if current time is later than 6am
                        usr.sleep_end = now # end sleep session
                        usr.sleep = False
                        print("wake up")

                        # publish sleep data
                        data = dict()
                        data["user_id"]=usr.user_id
                        data["date"]=usr.sleep_start.strftime("%Y-%m-%d")
                        data["break_count"]=usr.break_count
                        data["sleep_time"]=usr.sleep_start.strftime("$H:%M")
                        data["wake_time"]=usr.sleep_end.strftime("%H:%M")
                        data["sleep_count"]=strfdelta(usr.sleep_end-usr.sleep_start)
                        client.publish("record", json.dumps(data), 0)
                        break
                    elif now < usr.desired_wake:
                    # elif current time is earlier than 6am and not doNotDisturb
                        usr.break_count+=1
                        # light on until human come back
                        while not usr.human and not usr.doNotDisturb:
                            lighton(usr.color)
                            usr.human_check()
                            time.sleep(1)
                        lightoff()
                        print("break out")
                        break
                time.sleep(1)
        time.sleep(1)
        client.disconnect()
if __name__ == "__main__":
    main()