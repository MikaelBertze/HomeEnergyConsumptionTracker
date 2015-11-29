from datetime import datetime

class Sensor(object):
    """Sensor base class"""
    
    def __init__(self, sensorId, sensorType, sensorUnit):
        """ Constructor
        Parameters
        ----------
        sensorId : int
        sensorType : string
        sensorUnit : string
        """
        self.__sensorId = sensorId
        self.__sensorType = sensorType
        self.__sensorUnit = sensorUnit
        self.__values = []

    def sensorId(self):
        """Gets the sensor Id for this sensor"""
        return self.__sensorId

    def addValue(self, value, time = None):
        """Add a sensor value
        Parameters
        ----------
        value : int
                sensor value in the sensor specific unit
        time  : datetime, optional
                value read time. If not provide, time at function call is used
        """
        time = time if time != None else datetime.now()
        self.__values.append((time, value))

    def canPopMessage(self):
        return len(self.__values) > 0

    def peakDataMessage(self):
        """Build the sensor message for one value
        The reported value will not be removed from the internal list of values
        """
        if len(self.__values) == 0:
            return None
        return self.__buildDataMessage(self.__values[0])


    def popDataMessage(self):
        """Build the sensor message for one value
        The reported value will be removed from the internal list of values
        """
        if len(self.__values) == 0:
            return None
        return self.__buildDataMessage(self.__values.pop(0))

    def __buildDataMessage(self, value):
        assert len(value) == 2, "unexpected value lenght."
        return {
                    'sensorType' : self.__sensorType,
                    'sensorUnit' : self.__sensorUnit,
                    'value' : int(value[1]),
                    'time' : value[0].strftime('%Y-%m-%d %H:%M:%S.%f')[:-3]
               }

    





