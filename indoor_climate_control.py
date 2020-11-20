# Copyright (c) 2020 Vu Anh Vu
#
# This file is part of IndoorClimateControl.
#
# IndoorClimateControl is free software: you can redistribute it and/or modify
# it under the terms of the GNU General Public License as published by
# the Free Software Foundation, either version 3 of the License, or
# (at your option) any later version.
#
# IndoorClimateControl is distributed in the hope that it will be useful,
# but WITHOUT ANY WARRANTY; without even the implied warranty of
# MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
# GNU General Public License for more details.
#
# You should have received a copy of the GNU General Public License
# along with IndoorClimateControl.  If not, see <https://www.gnu.org/licenses/>.

import time
import sys
sys.path.append('./drive')
import subprocess
import sqlite3 as sl
import datetime
import aqi
import threading

import sensor_bme280 as BME280_SENSOR
import sensor_sds011 as SDS011_SENSOR
import display_ssd1305 as SSD1305_DISPLAY

import IFTTT_webhook as DEVICE_TRIGGER

DB_NAME = 'air-monitor-v2.db'

SAMPLING_INTERVAL = 15*60 - 60 # seconds
HISTORY_THRESHOLD = 12 # hours
LED_REFRESH_INTERVAL = 5*60 # seconds
DEVICE_CONTROL_INTERVAL = 1*60 # seconds

PURIFIER_ON_THRESHOLD = 2
PURIFIER_OFF_THRESHOLD = 0

def update_bme280():
    status_bme280 = False
    try:
        con = sl.connect(DB_NAME, detect_types=sl.PARSE_DECLTYPES | sl.PARSE_COLNAMES)
        cursorObj = con.cursor()
    except Exception as error:
        print("update_bme280 DB " + str(error))

    while True:
        bme280_data = BME280_SENSOR.get_sensor_data()
        if (bme280_data):
            temperature = bme280_data.temperature
            humidity = bme280_data.humidity
            air_pressure = bme280_data.pressure
            status_bme280 = True
        else:
            status_bme280 = False

        now = datetime.datetime.now()
        if status_bme280 :
            try:
                sqlite_insert_with_param = """INSERT INTO 'bme280_info'
                                          ('timestamp', 'temperature', 'humidity', 'air_pressure') 
                                          VALUES (?, ?, ?, ?);"""

                data_tuple = (
                    now, temperature, humidity, air_pressure)
                cursorObj.execute(sqlite_insert_with_param, data_tuple)
                con.commit()
                print("bme280 data added successfully \n")
            except Exception as error:
                print("Insert " + str(error))

        time.sleep(SAMPLING_INTERVAL)
    cursorObj.close()
    con.close()


def update_sds011():
    
    try:
        con = sl.connect(DB_NAME, detect_types=sl.PARSE_DECLTYPES | sl.PARSE_COLNAMES)
        cursorObj = con.cursor()
    except Exception as error:
        print("update_sds011 DB " + str(error))

    while True:
        try:
            sds011_data = SDS011_SENSOR.get_sensor_data()
        except Exception, exc:
            print(exc)
            status_sds011 = False

        if (sds011_data[0] and sds011_data[1]):
            aqi_index = aqi.to_aqi([
                (aqi.POLLUTANT_PM25, sds011_data[0]),
                (aqi.POLLUTANT_PM10, sds011_data[1])
            ])
            status_sds011 = True
        else:
            status_sds011 = False

        now = datetime.datetime.now()
        if status_sds011:
            try:
                sqlite_insert_with_param = """INSERT INTO 'sds011_info'
                                          ('timestamp','pm25','pm10','aqi_index') 
                                          VALUES (?, ?, ?, ?);"""

                data_tuple = (
                    now, sds011_data[0], sds011_data[1], int(aqi_index))
                cursorObj.execute(sqlite_insert_with_param, data_tuple)
                con.commit()
                print("sds011 data added successfully \n")
            except Exception as error:
                print("Insert " + str(error))

        thisdict = {
            "brand": "Ford",
            "model": "Mustang",
            "year": 1964
        }
        
        time.sleep(SAMPLING_INTERVAL)
    cursorObj.close()
    con.close()



def update_display():

    try:
        con = sl.connect(DB_NAME, detect_types=sl.PARSE_DECLTYPES | sl.PARSE_COLNAMES)
        cursorObj = con.cursor()
    except Exception as error:
        print("update_display DB " + str(error))

    status_bme280 = False
    status_sds011 = False

    temperature = -271.13
    humidity = 0
    air_pressure = 0
    aqi_index = -1

    low_temperature = -271.13
    low_humidity = 0
    low_air_pressure = 0
    low_aqi_index = -1

    high_temperature = -271.13
    high_humidity = 0
    high_air_pressure = 0
    high_aqi_index = -1
    while True:
        time.sleep(LED_REFRESH_INTERVAL)
        # Get data
        now = datetime.datetime.now()
        try:
            bme280_query = """SELECT timestamp,temperature,humidity from bme280_info order by timestamp desc LIMIT 1 """
            bme280_min_max_query = """SELECT MIN(temperature), MIN(humidity), MAX(temperature), MAX(humidity) from bme280_info where timestamp> ? """
            sds011_query = """SELECT timestamp,aqi_index from sds011_info order by timestamp desc LIMIT 1 """
            sds011_min_max_query = """SELECT MIN(aqi_index),MAX(aqi_index) from sds011_info where timestamp> ?  """

            cursorObj.execute(bme280_query)
            records = cursorObj.fetchone()
            # print(records)

            if records is not None and records[0] is not None and records[1] is not None and records[2] is not None and records[0] >= now - datetime.timedelta(seconds=SAMPLING_INTERVAL):
                status_bme280 = True
                temperature = records[1]
                humidity = records[2]
            else:
                status_bme280 = False

            cursorObj.execute(bme280_min_max_query, (now - datetime.timedelta(hours=HISTORY_THRESHOLD),))
            records = cursorObj.fetchone()
            # print (records)

            if  records is not None and records[0] is not None and records[1] is not None and records[2] is not None and records[3]:
                low_temperature = records[0]
                low_humidity = records[1]
                high_temperature = records[2]
                high_humidity = records[3]


            cursorObj.execute(sds011_query)
            records = cursorObj.fetchone()
            # print(records)

            if records is not None and records[0] is not None and records[1] is not None and records[0] >= now - datetime.timedelta(seconds=SAMPLING_INTERVAL):
                aqi_index = records[1]
                status_sds011 = True
            else:
                status_sds011 = False

            cursorObj.execute(sds011_min_max_query, (now - datetime.timedelta(hours=HISTORY_THRESHOLD),))
            records = cursorObj.fetchone()
            # print(records)

            if records is not None and records[0] is not None and records[1] is not None :
                low_aqi_index = records[0]
                high_aqi_index = records[1]

        except Exception as error:
            print("Query " + str(error))
            continue

        displayed_data = {
            "status_bme280": status_bme280,
            "status_sds011": status_sds011,
            "temperature": temperature,
            "low_temperature": low_temperature,
            "high_temperature": high_temperature,
            "humidity": humidity,
            "low_humidity": low_humidity,
            "high_humidity": high_humidity,
            "aqi_index": aqi_index,
            "low_aqi_index": low_aqi_index,
            "high_aqi_index": high_aqi_index,

        }
        SSD1305_DISPLAY.display(displayed_data)

    cursorObj.close()
    con.close()

def control_devices():

    purifier_on = False

    try:
        con = sl.connect(DB_NAME, detect_types=sl.PARSE_DECLTYPES | sl.PARSE_COLNAMES)
        cursorObj = con.cursor()
    except Exception as error:
        print("control_devices DB " + str(error))

    while True:
        time.sleep(DEVICE_CONTROL_INTERVAL)
        # Get data
        now = datetime.datetime.now()
        try:
            bme280_query = """SELECT timestamp,temperature,humidity from bme280_info order by timestamp desc LIMIT 1 """
            sds011_query = """SELECT timestamp,aqi_index from sds011_info order by timestamp desc LIMIT 1 """           

            cursorObj.execute(bme280_query)
            records = cursorObj.fetchone()
            
            if records is not None and records[0] is not None and records[1] is not None and records[2] is not None and records[0] >= now - datetime.timedelta(seconds=SAMPLING_INTERVAL):
                status_bme280 = True
                temperature = records[1]
                humidity = records[2]
            else:
                status_bme280 = False

            cursorObj.execute(sds011_query)
            records = cursorObj.fetchone()

            if records is not None and records[0] is not None and records[1] is not None and records[0] >= now - datetime.timedelta(seconds=SAMPLING_INTERVAL):
                aqi_index = records[1]
                status_sds011 = True
            else:
                status_sds011 = False
        except Exception as error:
            print("Query " + str(error))
            continue

        if not status_sds011 or not status_sds011:
            continue

        # Control logic
        if not purifier_on and aqi_index > PURIFIER_ON_THRESHOLD:
            result = DEVICE_TRIGGER.turn_on_device(DEVICE_TRIGGER.PURIFIER)
            if result:
                purifier_on = True
        elif purifier_on and aqi_index < PURIFIER_OFF_THRESHOLD:
            DEVICE_TRIGGER.turn_off_device(DEVICE_TRIGGER.PURIFIER)
            if result:
                purifier_on = False

    cursorObj.close()
    con.close()

if __name__ == "__main__":
    # Database
    try:
        con = sl.connect(DB_NAME)
        cursorObj = con.cursor()
        cursorObj.execute("CREATE TABLE bme280_info(id integer PRIMARY KEY, timestamp timestamp, temperature FLOAT, humidity FLOAT, air_pressure FLOAT)")
        cursorObj.execute("CREATE TABLE sds011_info(id integer PRIMARY KEY, timestamp timestamp, pm25 FLOAT,pm10 FLOAT,aqi_index integer)")
    except Exception as error:
        print("Create table " + str(error))
    cursorObj.close()
    con.close()

    bme280_thread = threading.Thread(target=update_bme280, args=())
    print("Updating Temp and Humidity ...")
    bme280_thread.start()

    sds011_thread = threading.Thread(target=update_sds011, args=())
    print("Updating PM2.5 ...")
    sds011_thread.start()

    display_thread = threading.Thread(target=update_display, args=())
    print("Updating LED display ...")
    display_thread.start()

    device_control_thread = threading.Thread(target=control_devices, args=())
    print("Controlling devices ...")
    device_control_thread.start()