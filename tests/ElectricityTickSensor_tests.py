from nose.tools import *
from homesensors.electricitysensors import ElectricityTickSensor


def setup():
    print "ElectricityTickSensor - Tests"


def teardown():
    pass


def test_ticksPerKwh():
    sensor = ElectricityTickSensor(12, 1000)
    assert sensor.ticks_per_kWh() == 1000, "unexpected ticks per kWh"

