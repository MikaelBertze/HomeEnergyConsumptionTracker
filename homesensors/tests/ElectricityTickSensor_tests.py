from nose.tools import *
from homesensors.electricitysensors import ElectricityTickSensor


def setup():
    print "ElectricityTickSensor - Tests"


def teardown():
    pass


def test_ticksPerKwh():
    sensor = ElectricityTickSensor(12, 1000)
    assert sensor.ticks_per_kWh() == 1000, "unexpected ticks per kWh"

def test_add_value_with_time_span():
    # arrange
    sensor = ElectricityTickSensor(12, 1000)

    # act
    sensor.add_value_with_time_span(.5)
    sensor.add_value_with_time_span(1)
    sensor.add_value_with_time_span(2)
    value1 = sensor.pop_data_message()
    value2 = sensor.pop_data_message()
    value3 = sensor.pop_data_message()

    # assert
    assert value1['value'] == 7200, "unexpected messege from tick report"
    assert value2['value'] == 3600, "unexpected messege from tick report"
    assert value3['value'] == 1800, "unexpected messege from tick report"


def test_convert_to_time():
    # arrange
    sensor = ElectricityTickSensor(12, 1000)

    # act
    value2 = sensor.convert_to_time(3600)
    value3 = sensor.convert_to_time(1800)
    value1 = sensor.convert_to_time(7200)

    #assert
    assert value1 == .5, "unexpected time for 7200W"
    assert value2 == 1.0, "unexpected time for 3600W"
    assert value3 == 2.0, "unexpected time for 1800W"


def test_convert_to_watt():
    # arrange
    sensor = ElectricityTickSensor(12, 1000)

    # act
    value1 = sensor.convert_to_watt(.5)
    value2 = sensor.convert_to_watt(1.0)
    value3 = sensor.convert_to_watt(2.0)

    #assert
    assert value1 == 7200, "unexpected power for .5s"
    assert value2 == 3600, "unexpected power for 1.0s"
    assert value3 == 1800, "unexpected power for 2.0s"



