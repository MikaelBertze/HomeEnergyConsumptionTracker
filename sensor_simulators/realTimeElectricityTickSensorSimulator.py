import sensorSimulatorUtils
import thread
from homesensors.electricitysensors import ElectricityTickSensor


def start_simulator(sensor_id, mean_value, span, period, sendSpan):
    sensor = ElectricityTickSensor(sensor_id, 1000)
    sensorSimulatorUtils.real_time_electricity_data(sensor, mean_value, span, period, sendSpan)
    # thread.start_new_thread(sensorSimulatorUtils.RealTimeElectricityData, (sensor, mean_value, span, period, sendSpan))


start_simulator(1, 2, 2, 240, 10)

while 1:
    pass
