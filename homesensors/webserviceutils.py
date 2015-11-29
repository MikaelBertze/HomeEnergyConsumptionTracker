import requests
import json

url = ""
DEBUG = False


def buildMessageAndSend(deliveryType, data):
	"""Build data message and send to web service
	data - json sensor measurment data"""
	
	sendMessage(buildMessage(deliveryType, data))

def buildMessage(deliveryType, data):
	"""Build data message to be consumed by web service
	data - json sensor measurment data"""

	jsonData = {"service" : "Delivery", "type" : deliveryType, "data" : data}
	return json.dumps(jsonData, sort_keys=False, indent=2)

def sendMessage(message, sensor_id):
	"""Send to web service helper function
	message - web service POST data"""
	
	payload = {"data" : json.dumps(message)}
	debug(payload)
	try:
		r = requests.post(url + str(sensor_id), data=payload)
		return True
	except:
		debug("WebService is down...")
		return False

def debug(message):
	if DEBUG:
		print "webserviceutils: " + str(message)