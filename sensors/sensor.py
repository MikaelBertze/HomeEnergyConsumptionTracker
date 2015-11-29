from datetime import datetime

class Sensor(object):
    """Sensor base class"""

    __sensorId = -1
    __sensorUnit = ''
    __sensorType = ''
    __values = []


    def __init__(self, sensorId, sensorType, sensorUnit):
        self.__sensorId = sensorId
        self.__sensorType = sensorType
        self.__sensorUnit = sensorUnit

    def sensorId(self):
        """Gets the sensor Id for this sensor"""
        return self.__sensorId

    def addValue(self, value, time = None):
        """Add a sensor value
        value - sensor value
        time - value read time. If None, time at function call is used"""
        time = time if time != None else datetime.now()
        self.__values.append((time, value))

    def canPopMessage(self):
        return len(self.__values) > 0

    def popDataMessage(self):
        """Build the sensor message for one value
        The reported value will be removed from the internal list of values
        """
        if len(self.__values) == 0:
            return None

        value = self.__values.pop(0)
        assert len(value) == 2, "unexpected value lenght."

        return {
                    'sensorType' : self.__sensorType,
                    'sensorUnit' : self.__sensorUnit,
                    'value' : int(value[1]),
                    'time' : value[0].strftime('%Y-%m-%d %H:%M:%S.%f')[:-3]
               }

    





