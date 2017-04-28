Home Energy Consumption Tracker Web Service
============================================
RESTful webservice that handles sensor reporting and power consumption calculations on requests.

Sensor reporting
----------------
POST /v1/currentLoad/:sensor_id

Resource URL
------------

/v1/currentLoad/:sensor_id

Parameters
--------------

Parameter | Type | Description | Requiered  |
---|---|---|--:|
sensor_id | Int | Sensor id | YES|
sensorType | String | Sensor type | YES |
value | Int | Sensor value | YES|
time| Time string | Read time | YES|

Note: The provided time shall be on format '%Y-%m-%d %H:%M:%S.%f'

Current sensor load
----------------------
GET /v1/currentLoad/:sensor_id

Resource URL
---------------
/v1/currentLoad/:sensor_id

Output Parameters
----------------------

Parameter | Type | Description |
---|---|--:|
sensorId | Int | Sensor ID |
currentLoad | Int | Latest reported load |
sensorType | String | Type of sensor |
sensorUnit | String | Unit for sensor value |
time | Time astring | Sensor value report time |
