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


def real_time_electricity_data_specified_by_power(sensor, mean_power, power_span, period, send_span):
    """Real time electricity tick sensor simulator.
    This simulator will mimic a real tick sensor.
    Output from this sensor will be a sinus wave.
    sensor - instance of an ElectricityTickSensor
    mean_power - mean power value (Watt)
    power_span - peak to peak distance (Watt)
    period - time span in seconds for full sinus wave
    send_span - time span in seconds between send to web service
    """

    w_per_tick = 3600.0 / sensor.ticks_per_kWh() *1000

    curve = get_curve(mean_power, power_span)

    real_time_electricity_simulator(sensor, curve, period, send_span)


def get_curve(mean, span):
    return [math.sin(x) * (span / 2) + mean for x in np.linspace(0, 2 * math.pi, num=2000)]


def real_time_electricity_simulator(sensor, curve, period, send_span):
    """Real time electricity tick sensor simulator.
    This simulator will mimic a real tick sensor.
    Output from this sensor will be a sinus wave.
    sensor - instance of an ElectricityTickSensor
    mean - mean value for the sinus wave (time between ticks in seconds)
    span - peak to peak distance (seconds)
    period - time span in seconds for full sinus wave
    send_span - time span in seconds between send to web service
    """

    print "Starting simulator"
    print "------------------------------"
    print "Type: Electricity Tick Sensor"
    print "Max: %f sec" % max(curve)
    print "Min: %f sec" % min(curve)
    print "Period: %i sec" % period
    print "Send Interval: %i" % send_span
    print "-----------------------------"
    print

    t = time()
    last_send= t
    while True:
        i = get_sin_index(t, period, len(curve))
        power = curve[i]
        diff = sensor.convert_to_time(power)
        t += diff
        pause.until(t)
        print "tick time: " + str(diff)
        print "Current load: " + str(power)
        sensor.add_value(power)

        if time() - last_send >= send_span:
            send_test_data(sensor)
            last_send = time()
