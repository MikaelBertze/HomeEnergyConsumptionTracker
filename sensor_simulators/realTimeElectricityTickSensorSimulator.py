import sensorSimulatorUtils
from homesensors.electricitysensors import ElectricityTickSensor


def start_simulator(sensor_id, mean_value, span, period, send_span):
    sensor = ElectricityTickSensor(sensor_id, 1000)
    sensorSimulatorUtils.real_time_electricity_data_specified_by_power(sensor, mean_value, span, period, send_span)

start_simulator(1, 1000, 500, 30, 10)

while 1:
    pass
