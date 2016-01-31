from bottle import route, run, template, request
import databaseUtils
import json
import ConfigParser
import measurements
import deliveryService
from datetime import datetime


config = ConfigParser.RawConfigParser()
config.read('webservice.cfg')

port = config.getint("Site", "port")
url = config.get("Site", "url")
databaseUtils.databaseUser = config.get("DB", "user")
databaseUtils.databasePass = config.get("DB", "pass")
databaseUtils.databaseDb = config.get("DB", "database")
DEBUG = config.get("Site", "Debug") == "TRUE"


@route('/v1/currentLoad/<sensor_id:int>', method='GET')
def current_load_get(sensor_id):
    debug("currentLoadGet")
    current_load = measurements.get_current_load(sensor_id)

    result = {
               'sensorId': sensor_id,
               'currentLoad': current_load['sensor_value'],
               'sensorType': current_load['sensor_type'],
               'sensorUnit': current_load['sensor_unit']
             }

    print result
    return json.dumps(result)


@route('/v1/currentLoad/<sensor_id:int>', method='POST')
def current_load_post(sensor_id):
    debug("currentLoadPost")

    
    sensor_value = request.forms.get("value")
    date_time_str = request.forms.get("time")
    sensor_type = request.forms.get("sensorType")
    date_time= datetime.strptime(date_time_str, '%Y-%m-%d %H:%M:%S.%f')
    debug([sensor_id, sensor_type, sensor_value, date_time])
    deliveryService.current_load_delivery(sensor_id, sensor_type, sensor_value, date_time)


@route('/v1/consumption/<sensor_id:int>', method='GET')
def consumption(sensor_id):
    current_load = measurements.get_current_load(sensor_id)

    result = {
               'Sensor_id': sensor_id,
               'current_load': current_load,
               'current_load_unit': 'kWh'
             }

    return json.dumps(result)


def debug(message):
  if DEBUG:
    print message

debug("debug") 
run(host='localhost', port=4000)
