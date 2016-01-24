import databaseUtils as db_utils


def get_current_load(sensor_id):
    query = __get_current_load_query(sensor_id)
    print query
    result = db_utils.query_for_data(query)
    return {
            'sensor_value': result[0][1],
            'sensor_id': sensor_id,
            'date_time': result[0][0],
            'sensor_type': result[0][2],
            'sensor_unit': __get_unit_for_sensor(result[0][2])
           }


def __get_current_load_query(sensor_id):
    return "SELECT `date_time`, `sensor_value`, `sensor_type` FROM `measurements` WHERE `sensor_id` = '%s' " \
           "ORDER BY `id` DESC LIMIT 1" % sensor_id


def __get_unit_for_sensor(sensor_type):
    conversions = {'ElectricityTickSensor': 'Watt'}
    if type in conversions.keys():
        return conversions[sensor_type]
    return "Undefined"
