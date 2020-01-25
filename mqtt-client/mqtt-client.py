import paho.mqtt.client as mqtt
from homesensors.electricitysensors import ElectricityTickSensor
import homesensors.webserviceutils as webutils


def send_data(sensor):
    stop = False
    while stop is False and sensor.can_pop_message():
        message = sensor.peak_data_message()
        stop = not webutils.send_message(message, sensor.sensor_id())
        if not stop:
            sensor.pop_data_message()



# The callback for when the client receives a CONNACK response from the server.
def on_connect(client, userdata, flags, rc):
    print("Connected with result code "+str(rc))

    # Subscribing in on_connect() means that if we lose the connection and
    # reconnect then subscriptions will be renewed.
    client.subscribe("/megatron/electicityTicker")

# The callback for when a PUBLISH message is received from the server.
def on_message(client, userdata, msg):
    print(msg.topic+" "+str(msg.payload))
    s = msg.payload.decode('ascii')
    key, value = (x.strip() for x in s.split(':'))
    if key == 'tickPeriod':
        v = int(value)
        wh_per_hit = 1 / float(1000) * 1000
        power = wh_per_hit * 3600/float(v/1000)
        sensor.add_value(power)
        send_data(sensor)

sensor = ElectricityTickSensor(1, 1000)
webutils.url = "http://127.0.0.1:4000/v1/currentLoad/"
webutils.DEBUG = True

client = mqtt.Client()
client.on_connect = on_connect
client.on_message = on_message

client.connect("broker.hivemq.com", 1883, 60)

# Blocking call that processes network traffic, dispatches callbacks and
# handles reconnecting.
# Other loop*() functions are available that give a threaded interface and a
# manual interface.

client.loop_forever()