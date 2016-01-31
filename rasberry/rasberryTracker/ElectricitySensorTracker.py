from homesensors.electricitysensors import ElectricityTickSensor
import RPi.GPIO as GPIO
from time import time, sleep
import json
import sys

sensors = {}

def triggHandlerDigital(channel):
    t = time()
    sensor = sensor[channel]
    if sensor.last_tick > 0:
        timeDiff = t - sensor.last_tick
        sensor.add_value_with_time_span(timeDiff)
	sensor.last_tick  = t
	print "TICK: {}".format(sensor.sensor_id())


def get_settings(fileName, app):
    json_data=open(fileName)
    settings = json.load(json_data)
    json_data.close()
    return settings[app]


if __name__ == '__main__':
    if len(sys.argv) != 2:
        print "Start with path to config"
        exit()

    GPIO.setmode(GPIO.BCM)
    settingsFile = sys.argv[1]
    settings = sensorUtils.getSettings(settingsFile, "ElectroMeter")
    sendInterval = int(settings["SendInterval"])

    print "Setting up sensors..."
    for s in settings["Sensors"]:
        pin = int(s["Pin"])
        ticks_per_kWh = int(s["HitsPerKwh"])
        sensor_id = s["SensorId"]
        sensorType = s["Type"]
        sensor = ElectricityTickSensor(sensor_id, ticks_per_kWh)
        sensors[pin] = sensor
        sensor.last_tick = -1
        GPIO.setup(pin, GPIO.IN)
    	GPIO.add_event_detect(pin, GPIO.RISING, callback=triggHandlerDigital, bouncetime=100)

	print "Done!"
	print "Waiting for a tick..."
    try:
        while(True):
            sleep(sendInterval)
            if dataToSend():
                print "sending data..."
                data = sensorUtils.buildMessageAndSend("ElectricityTicks", buildDataMessage())
    except:
        print "Exiting..."
        GPIO.cleanup()       # clean up GPIO on CTRL+C exit
        GPIO.cleanup()           # clean up GPIO on normal exit

