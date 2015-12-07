from datetime import datetime


class Sensor(object):
    """Sensor base class"""
    
    def __init__(self, sensor_id, sensor_type, sensor_unit):
        """ Constructor
        Parameters
        ----------
        sensor_id : int
        sensor_type : string
        sensor_unit : string
        """
        self.__sensorId = sensor_id
        self.__sensorType = sensor_type
        self.__sensorUnit = sensor_unit
        self.__values = []

    def sensor_id(self):
        """Gets the sensor Id for this sensor"""
        return self.__sensorId

    def add_value(self, value, time=None):
        """Add a sensor value
        Parameters
        ----------
        value : int
                sensor value in the sensor specific unit
        time  : datetime, optional
                value read time. If not provide, time at function call is used
        """
        time = time if time is not None else datetime.now()
        self.__values.append((time, value))

    def can_pop_message(self):
        return len(self.__values) > 0

    def peak_data_message(self):
        """Build the sensor message for one value
        The reported value will not be removed from the internal list of values
        """
        if len(self.__values) == 0:
            return None
        return self.__build_data_message(self.__values[0])

    def pop_data_message(self):
        """Build the sensor message for one value
        The reported value will be removed from the internal list of values
        """
        if len(self.__values) == 0:
            return None
        return self.__build_data_message(self.__values.pop(0))

    def __build_data_message(self, value):
        assert len(value) == 2, "unexpected value lenght."
        return {
                    'sensorType': self.__sensorType,
                    'sensorUnit': self.__sensorUnit,
                    'value': int(value[1]),
                    'time': value[0].strftime('%Y-%m-%d %H:%M:%S.%f')[:-3]
               }
