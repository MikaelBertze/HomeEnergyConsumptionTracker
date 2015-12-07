import requests
import json

url = ""
DEBUG = False


def build_message_and_send(delivery_type, data):
    """Build data message and send to web service
    data : json sensor measurment data"""
    send_message(build_message(delivery_type, data))


def build_message(delivery_type, data):
    """Build data message to be consumed by web service
    data - json sensor measurment data"""
    jsonData = {"service": "Delivery", "type": delivery_type, "data": data}
    return json.dumps(jsonData, sort_keys=False, indent=2)


def send_message(message, sensor_id):
    """Send to web service helper function
    message - web service POST data

    Parameters
    ----------
    message
    sensor_id"""

    payload = {"data": json.dumps(message)}
    __debug(payload)
    try:
        r = requests.post(url + str(sensor_id), data=payload)
        return True
    except:
        __debug("WebService is down...")
        return False


def __debug(message):
    if DEBUG:
        print "webserviceutils: " + str(message)
