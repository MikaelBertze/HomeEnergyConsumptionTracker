# -*- coding: utf-8 -*-

import threading
import paho.mqtt.client as mqtt
import requests
from loguru import logger
from datetime import datetime, timedelta
import time

class MqttUpdater(threading.Thread):

    def __init__(self, subject):
        self.subject = subject
        threading.Thread.__init__(self)

    def run(self):
        logger.info("Starting MQTT updater thread")
        client = mqtt.Client(userdata = self)
        client.on_connect = MqttUpdater.on_connect
        client.on_message = MqttUpdater.on_message
        client.connect("broker.hivemq.com", 1883, 60)
        client.loop_forever()

    @staticmethod
    def on_connect(client, userdata, flags, rc):
        logger.info("Connected with result code  " +str(rc))
        # Subscribing in on_connect() means that if we lose the connection and
        # reconnect then subscriptions will be renewed.
        client.subscribe("/megatron/electricityTicker")
        client.subscribe("/megatron/temperature")

    @staticmethod
    def on_message(client, userdata, msg):
        try:
            recieved = msg.payload.decode('ascii')

            if msg.topic == "/megatron/electricityTicker":
                tps, cs = recieved.split('|')

                for s in [tps, cs]:
                    key, value = (x.strip() for x in s.split(':'))
                    if key == 'tickPeriod':
                        v = int(value)
                        wh_per_hit = 1 / float(1000) * 1000
                        power = wh_per_hit * 3600 / float(v / 1000)
                        userdata.subject.on_next(('power', f"{str(int(power))}W"))

            if msg.topic == "/megatron/temperature":
                key, value = (x.strip() for x in recieved.split(':'))
                if key == 'temp':
                    userdata.subject.on_next(('temp', f"{value}°C"))

        except Exception as ex:
            logger.error("Exception in mqtt thread: " + str(ex))


class WeatherUpdater(threading.Thread):
    def __init__(self, update_subject):
        self.update_subject = update_subject
        threading.Thread.__init__(self)

    def run(self):
        while True:
            try:
                logger.info("Fetching weather data...")
                response = requests.get("https://opendata-download-metfcst.smhi.se/api/category/pmp3g/version/2/geotype/point/lon/13.441438/lat/59.383517/data.json")
                logger.info("Fetching weather status: " + str(response.status_code))
                data = response.json()
                data = data['timeSeries']
                now = datetime.now()
                midnight = datetime(now.year, now.month, now.day, 23, 59, 59)
                day0 = (now, midnight)
                day1 = midnight + timedelta(seconds=1)
                day1 = (day1, day1 + timedelta(days=1))
                day2 = (day1[1], day1[1] + timedelta(days=1))
                r_data = []
                for d in [day0, day1, day2]:
                    datapoints = [x for x in data if d[0] < datetime.fromisoformat(x['validTime'][:-1]) < d[1]]
                    temperatures = []
                    for da in datapoints:
                        temp = next(t for t in da['parameters'] if t['name'] == 't')
                        temperatures.append(temp['values'][0])

                    r = [f"{d[0].day}/{d[0].month}", max(temperatures), min(temperatures)]
                    r_data.append(r)

                self.update_subject.on_next(("weather", (datetime.now(), r_data)))
            except Exception as ex:
                logger.error("Exception in weather thread: " + str(ex))
                logger.info(data)

            finally:
                time.sleep(10*60)  # 10 minutes

