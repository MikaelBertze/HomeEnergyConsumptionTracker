# -*- coding: utf-8 -*-
import os
from loguru import logger
from controlpanel.frames import MainApp
from controlpanel.updaters import Updater

if __name__ == '__main__':
    logger.add("home_display.log", retention="5 days")
    logger.info("Starting up!")
    updater = Updater()
    updater.start()
    app = MainApp(updater)

    if os.getenv('CONTROLPANEL_FULLSCREEN') == '1':
        logger.info("Setting full screen mode")
        app.attributes("-fullscreen", True)

    app.geometry("720x480")
    app.mainloop()