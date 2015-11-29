from sensor import Sensor

class ElectricityTickSensor(Sensor):
    """Electricity tick sensor"""

    __ticksPerKWh = -1


    def __init__(self, sensorId, ticksPerKWh):
        """Constructor
        sensorId - sensor id (int)
        ticksPerKWh - number of ticks per kWh
        """
        super(ElectricityTickSensor, self).__init__(sensorId, 'ElectricityTickSensor', 'Watt')
        self.__ticksPerKWh = ticksPerKWh

    def ticksPerKwh(self):
        """Ticks per kWh"""
        return self.__ticksPerKWh

    def addValueWithTimeSpan(self, timeSpan):
        """Add value using a timeSpan."""
        self.addValue(self.convertToWatt(timeSpan))

    def convertToWatt(self, timeSpan):
        """Convert a timeSpan to Watts
        timeSpan - time span in seconds
        """
        WhPerHit = 1 / float(self.__ticksPerKWh) * 1000
        return WhPerHit * 3600/float(timeSpan)






    
