# -*- coding: utf-8 -*-
from loguru import logger
from rx import create

from controlpanel.frames import MainApp
from rx.subject import Subject

from controlpanel.updaters import MqttUpdater, WeatherUpdater


def get_config():
    config = {}
    with open('home_display.cfg', 'r') as config_file:
        content = config_file.readlines()
    for c in content:
        row = [x.strip() for x in c.split(':')]
        config[row[0]] = row[1]
    return config

if __name__ == '__main__':
    logger.add("home_display.log", retention="5 days")
    logger.info("Starting up!")
    config = get_config()
    logger.info("Configuration: " + str(config))

    updates = Subject()
    updates.subscribe(lambda x: print(x))

    mqtt_updater = MqttUpdater(updates)
    mqtt_updater.start()

    weather_updater = WeatherUpdater(updates)
    weather_updater.start()

    app = MainApp(updates)
    if config['fullscreen'] == "YES":
        app.attributes("-fullscreen", True)
    app.geometry("720x480")
    app.mainloop()