import json
from time import time, sleep
import numpy as np
import math
import pause
import homesensors.webserviceutils as webutils 

webutils.url = "http://127.0.0.1:4000/v1/currentLoad/"
webutils.DEBUG = True

def buildAddDataMessage(data):
	dataMsg = {"type" : "ElectricityTicks", "data" : data}
	return dataMsg

def sendTestData(sensor):
	stop = False
	while stop == False and sensor.canPopMessage():
		message = sensor.peakDataMessage()
		#print message
		data = buildAddDataMessage(message)
		stop = not webutils.sendMessage(message, sensor.sensorId())
		if not stop:
			sensor.popDataMessage()

def getSinIndex(t, span, len):
	tprim = t%span
	index = float(tprim)/span * len
	return int(index)

def Make240minSquareWawe(channel, mean, span, period):
	data = [mean - span/2, mean + span/2]
	tStop = time()
	t = tStop - 240*60
	while t < tStop:
		i = getSinIndex(t, period, len(data))
		addEdgeTime(channel,t)
		t = t + data[i]

	sendTestData(1000)

	return data

def Make240minSinusData(channel, mean, span, period):
	data = [math.sin(x) * (span/2) + mean for x in np.linspace(0,2*math.pi, num=2000)]
	#print data
	tStop = time()
	t = tStop - 60*240
	while t < tStop:
		i = getSinIndex(t, period, len(data))
		addEdgeTime(channel,t, 1000)
		t = t + data[i]

	sendTestData(1000)


def RealTimeElectricityData(sensor, mean, span, period, sendSpan):
	"""Real time electricity tick sensor simulator.
	This simulator will mimic a real tick sensor.
	Output from this sensor will be a sinus wave.
	sensor - instance of an ElectricityTickSensor
	mean - mean value for the sinus wave
	span - peak to peak distance
	period - time span in seconds for full sinus wave
	sendSpan - time span in seconds between send to web service
	"""

	print "Starting simulator"
	print "------------------------------"
	print "Type: Electricity Tick Sensor"
	print "Mean: %i sec"%mean
	print "Span: %i Watt"%span
	print "Period: %i sec"%period
	print "Send Interval: %i"%sendSpan
	print "-----------------------------"
	print

	data = [math.sin(x) * (span/2) + mean for x in np.linspace(0,2*math.pi, num=2000)]
	t = time()
	lastSend = t
	while True:
		i = getSinIndex(t, period, len(data))
		delta = data[i]
		t = t + delta
		pause.until(t)
		w = sensor.convertToWatt(delta)
		print "Current load: " + str(w)
		sensor.addValue(w)

		if time() - lastSend >= sendSpan:
			sendTestData(sensor)
			lastSend = time()
			

