
import databaseUtils
from datetime import datetime


def current_load_delivery(sensor_id, type, sensor_value, date_time):
    query = "INSERT INTO `measurements` (`sensor_id`, `sensor_type`, `sensor_value`, `date_time`) VALUES(%s, %s, %s, %s)"
    date_time_str = date_time.strftime('%Y-%m-%d %H:%M:%S.%f')[:-3]
    data = [(str(sensor_id), type, str(sensor_value), date_time_str)]
    print(data)
    databaseUtils.insert_many(query, data)
