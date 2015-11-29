import sensorSimulatorUtils
import thread
from homesensors.electricitysensors import ElectricityTickSensor

def StartSimulator(sensor_id, mean_value, span, period, sendSpan):
    
    sensor = ElectricityTickSensor(sensor_id, 1000)
    sensorSimulatorUtils.RealTimeElectricityData(sensor, mean_value, span, period, sendSpan)
    #thread.start_new_thread(sensorSimulatorUtils.RealTimeElectricityData, (sensor, mean_value, span, period, sendSpan))

StartSimulator(1, 2, 2, 240, 10)

while 1:
   pass
