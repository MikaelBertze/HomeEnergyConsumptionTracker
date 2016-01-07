from time import time
import numpy as np
import math
import pause
import homesensors.webserviceutils as webutils

webutils.url = "http://127.0.0.1:4000/v1/currentLoad/"
webutils.DEBUG = True


def build_add_data_message(data):
    datamsg = {"type": "ElectricityTicks", "data": data}
    return datamsg


def send_test_data(sensor):
    stop = False
    while stop is False and sensor.can_pop_message():
        message = sensor.peak_data_message()
        stop = not webutils.send_message(message, sensor.sensor_id())
        if not stop:
            sensor.pop_data_message()


def get_sin_index(t, span, len):
    tprim = t % span
    index = float(tprim) / span * len
    return int(index)


def real_time_electricity_data(sensor, mean, span, period, sendSpan):
    """Real time electricity tick sensor simulator.
    This simulator will mimic a real tick sensor.
    Output from this sensor will be a sinus wave.
    sensor - instance of an ElectricityTickSensor
    mean - mean value for the sinus wave
    span - peak to peak distance
    period - time span in seconds for full sinus wave
    sendSpan - time span in seconds between send to web service
    """

    print "Starting simulator"
    print "------------------------------"
    print "Type: Electricity Tick Sensor"
    print "Mean: %i sec" % mean
    print "Span: %i Watt" % span
    print "Period: %i sec" % period
    print "Send Interval: %i" % sendSpan
    print "-----------------------------"
    print

    data = [math.sin(x) * (span / 2) + mean for x in np.linspace(0, 2 * math.pi, num=2000)]
    t = time()
    last_send= t
    while True:
        i = get_sin_index(t, period, len(data))
        delta = data[i]
        t += delta
        pause.until(t)
        w = sensor.convert_to_watt(delta)
        print "Current load: " + str(w)
        sensor.add_value(w)

        if time() - last_send >= sendSpan:
            send_test_data(sensor)
            last_send = time()
