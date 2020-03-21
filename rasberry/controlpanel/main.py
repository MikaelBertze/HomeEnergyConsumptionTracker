# -*- coding: utf-8 -*-
import os
from loguru import logger
from controlpanel.frames import MainApp
from rx.subject import Subject
from controlpanel.updaters import MqttUpdater, WeatherUpdater


if __name__ == '__main__':
    logger.add("home_display.log", retention="5 days")
    logger.info("Starting up!")
    updates = Subject()
    updates.subscribe(lambda x: print(x))

    mqtt_updater = MqttUpdater(updates)
    mqtt_updater.start()
    weather_updater = WeatherUpdater(updates)
    weather_updater.start()

    app = MainApp(updates)

    if os.getenv('CONTROLPANEL_FULLSCREEN') == '1':
        logger.info("Setting full screen mode")
        app.attributes("-fullscreen", True)

    app.geometry("720x480")
    app.mainloop()