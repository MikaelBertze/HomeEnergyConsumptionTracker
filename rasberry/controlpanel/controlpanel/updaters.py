# -*- coding: utf-8 -*-

import threading
import paho.mqtt.client as mqtt
import requests
from loguru import logger
from datetime import datetime, timedelta
import numpy as np
import time

from rx.subject import Subject


class Updater:

    def __init__(self):
        self.temp_updater = TemperatureUpdater()
        self.power_updater = PowerUpdater()
        self.weather_updater = WeatherUpdater()

    def start(self):
        self.temp_updater.start()
        self.power_updater.start()
        self.weather_updater.start()


class MqttUpdater(threading.Thread):

    def __init__(self, server, topic, on_message):
        threading.Thread.__init__(self)
        self._server = server
        self._topic = topic
        self._on_message = on_message

    def run(self):
        logger.info("Starting MQTT updater thread")
        client = mqtt.Client(userdata=self)
        client.on_connect = MqttUpdater.on_connect
        client.on_message = self._on_message
        client.connect(self._server, 1883, 60)
        client.loop_forever()

    @staticmethod
    def on_connect(client, userdata, flags, rc):
        logger.info("HEJ!")
        logger.info("Connected with result code  " +str(rc))
        logger.info(userdata._topic)
        client.subscribe(userdata._topic)

class PowerUpdater(MqttUpdater):
    def __init__(self):
        MqttUpdater.__init__(self, "broker.hivemq.com", "/megatron/electricityTicker", PowerUpdater.on_message)
        self.whenPowerReported = Subject()
        self.whenHourUsageReported = Subject()
        self.currentHourUsage = []

    @staticmethod
    def on_message(client, userdata, msg):
        try:
            received = msg.payload.decode('ascii')
            tps, cs = received.split('|')

            for s in [tps, cs]:

                key, value = (x.strip() for x in s.split(':'))
                if key == 'tickPeriod':
                    v = int(value)
                    wh_per_hit = 1 / float(1000) * 1000
                    power = wh_per_hit * 3600 / float(v / 1000)

                    userdata.whenPowerReported.on_next(power)

                    # hourly usage
                    now = datetime.now()
                    delta = timedelta(minutes=now.minute, seconds=now.second, microseconds=now.microsecond)
                    if len(userdata.currentHourUsage) > 0 and userdata.currentHourUsage[-1][0] > delta.total_seconds():
                        logger.info("new hour!")
                        userdata.currentHourUsage = []
                    userdata.currentHourUsage.append((delta.total_seconds(), power))
                    values = [x[1] / 1000 for x in userdata.currentHourUsage]
                    times = [x[0] / 60 / 60 for x in userdata.currentHourUsage]
                    currentHourUsage = np.trapz(values, times)

                    userdata.whenHourUsageReported.on_next(currentHourUsage)

        except Exception as ex:
            logger.error("Exception in mqtt thread: " + str(ex))


class TemperatureUpdater(MqttUpdater):
    def __init__(self):
        MqttUpdater.__init__(self, "broker.hivemq.com", "/megatron/temperature", TemperatureUpdater.on_message)
        self.whenTemperatureReported = Subject()

    @staticmethod
    def on_message(client, userdata, msg):
        try:
            logger.info("message!")
            received = msg.payload.decode('ascii')
            logger.info(received)
            key, value = (x.strip() for x in received.split(':'))
            if key == 'temp':
                userdata.whenTemperatureReported.on_next(float(value))

        except Exception as ex:
            logger.error("Exception in mqtt thread: " + str(ex))


class WeatherUpdater(threading.Thread):
    def __init__(self):
        threading.Thread.__init__(self)
        self.when_weather_updated = Subject()


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

                self.when_weather_updated.on_next(("weather", (datetime.now(), r_data)))

            except Exception as ex:
                logger.error("Exception in weather thread: " + str(ex))
                logger.info(data)

            finally:
                time.sleep(10*60)  # 10 minutes

