from sensor import Sensor


class ElectricityTickSensor(Sensor):
    """Electricity tick sensor"""

    __ticksPerKWh = -1

    def __init__(self, sensor_id, ticks_per_kWh):
        """Constructor

        Parameters
        ----------
        sensor_id : int
                    sensor ID
        ticks_per_kWh : float
                        ticks per kWh
        """
        super(ElectricityTickSensor, self).__init__(sensor_id, 'ElectricityTickSensor', 'Watt')
        self.__ticksPerKWh = ticks_per_kWh

    def ticks_per_kWh(self):
        """Ticks per kWh"""
        return self.__ticksPerKWh

    def add_value_with_time_span(self, time_span):
        """Add value using a timeSpan.

        Parameters
        ----------
        time_span : float
                    time span in seconds
        """
        self.add_value(self.convert_to_watt(time_span))

    def convert_to_watt(self, time_span):
        """Convert a timeSpan to Watts
        Parameters
        ----------
        time_span : float
                    time span in seconds
        """
        wh_per_hit = 1 / float(self.__ticksPerKWh) * 1000
        return wh_per_hit * 3600/float(time_span)






    
