from datetime import datetime
import paho.mqtt.client as mqtt
from homesensors.electricitysensors import ElectricityTickSensor
import deliveryService
import configparser
import databaseUtils

def send_data(sensor):
    while sensor.can_pop_message():
        message = sensor.pop_data_message()

        date_time= datetime.strptime(message['time'], '%Y-%m-%d %H:%M:%S.%f')
    
        deliveryService.current_load_delivery(sensor.sensor_id(), message['sensorType'], message['value'], date_time)



# The callback for when the client receives a CONNACK response from the server.
def on_connect(client, userdata, flags, rc):
    print("Connected with result code "+str(rc))

    # Subscribing in on_connect() means that if we lose the connection and
    # reconnect then subscriptions will be renewed.
    client.subscribe("/megatron/electicityTicker")

# The callback for when a PUBLISH message is received from the server.
def on_message(client, userdata, msg):
    try:
        print(msg.topic+" "+str(msg.payload))
        s = msg.payload.decode('ascii')
        key, value = (x.strip() for x in s.split(':'))
        if key == 'tickPeriod':
            v = int(value)
            wh_per_hit = 1 / float(1000) * 1000
            power = wh_per_hit * 3600/float(v/1000)
            print(power)
            sensor.add_value(power)
            send_data(sensor)
    except Exception as ex:
        print(ex)
        

sensor = ElectricityTickSensor(1, 1000)
#webutils.url = "http://127.0.0.1:4000/v1/currentLoad/"
#webutils.DEBUG = True

config = configparser.RawConfigParser()
config.read('mqtt-client.cfg')

#port = config.getint("Site", "port")
#url = config.get("Site", "url")
databaseUtils.databaseUser = config.get("DB", "user")
databaseUtils.databasePass = config.get("DB", "pass")
databaseUtils.databaseDb = config.get("DB", "database")

client = mqtt.Client()
client.on_connect = on_connect
client.on_message = on_message

client.connect("broker.hivemq.com", 1883, 60)

# Blocking call that processes network traffic, dispatches callbacks and
# handles reconnecting.
# Other loop*() functions are available that give a threaded interface and a
# manual interface.

client.loop_forever()