import datetime as dt
import paho.mqtt.client as mqtt
import json
a = dt.datetime(2021, 1, 27, 23,22,15)
b = dt.datetime(2021, 11, 29, 6, 22, 0)
now = dt.datetime.now()

client = mqtt.Client()

def on_connect(client, userdata, flags, rc):
    if rc == 0:
        print('connected')
    else:
        print('connect failed')
def on_message(client, userdata, message):
    print(message.topic)
    print(message.payload.decode('utf-8'))
    client.disconnect()

def strfdelta(tdelta):
    d={"D":tdelta.days}
    hours, rem= divmod(tdelta.seconds, 3600)
    minutes, seconds = divmod(rem,60)

    d['H']='{:02d}'.format(hours)
    d['M']='{:02d}'.format(minutes)
    #if d['D']>0:
    #    d['H'] = int(d['H'])+int(d['D'])*24
    return "{}:{}".format(d['H'], d['M'])

#connection 준비
client.on_connect=on_connect
client.on_message = on_message
client.connect('3.94.177.16', 1883)


# test publish function
data = dict()
data["user_id"]="test1"
data["date"]=a.strftime("%Y-%m-%d")
data["break_count"]=3
data["sleep_time"]=a.strftime("%H:%M")
data["wake_time"]=b.strftime("%H:%M")
data["sleep_count"] = strfdelta(b-a)
#print(json.dumps(data))
client.publish("record",json.dumps(data), 1)



# test subscribe function
client.subscribe('/setting/qwerty123')
client.loop_forever()

client.disconnect()