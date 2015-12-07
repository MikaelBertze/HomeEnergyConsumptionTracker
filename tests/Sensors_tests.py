from nose.tools import *
from homesensors.sensor import Sensor
from datetime import datetime


def setup():
    pass

def teardown():
    pass

def test_sensorId():
    sensor = Sensor(12, "testSensor", "Q")
    assert sensor.sensor_id() == 12, "wrong id"

def test_peakDataMessage():
    sensor = Sensor(12, "testSensor", "Q")
    sensor.add_value(1)
    
    assert sensor.peak_data_message()['value'] == 1, "Wrong message got peaked?"
    assert sensor.peak_data_message()['value'] == 1, "Should be possible to peak multiple times"
    assert sensor.pop_data_message()['value'] == 1, "Wrong message got popped?"
    assert sensor.peak_data_message() == None, "Should return none when list is empty"

def test_popDataMessage():
    sensor = Sensor(12, "testSensor", "Q")
    sensor.add_value(1)
    assert sensor.pop_data_message()['value'] == 1, "Wrong message got popped?"
    assert sensor.pop_data_message() == None, "Should return none when list is empty"

def test_popDataMessage_shall_be_FIFO():
    sensor = Sensor(12, "testSensor", "Q")
    value_order = [1, 8, 23, 56, 12, 87, 4, 67, 90, 12]
    [sensor.add_value(x) for x in value_order]

    for expected_value in value_order:
        assert sensor.pop_data_message()['value'] == expected_value, "Wrong message got popped"
        

def test_addValue_using_current_time():
    sensor = Sensor(12, "testSensor", "Q")
    sensor.add_value(1)
    sensor.add_value(2)

def test_addValue_using_provided_time():
    sensor = Sensor(12, "testSensor", "Q")
    t = datetime.now()
    sensor.add_value(1, t)
    sensor.add_value(2, t)


        

