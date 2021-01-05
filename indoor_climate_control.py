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
import logging

import sensor_bme280 as ATMOSPHERIC_SENSOR
import sensor_sds011 as DUST_SENSOR
import display_ssd1305 as LED_DISPLAY
import sensor_mhz19 as CO2_SENSOR
import web_dashboard as WEB_DASHBOARD
import IFTTT_webhook as DEVICE_TRIGGER

######################################
LOG_LEVEL = logging.DEBUG

DB_NAME = 'air-monitor-v3.db'

SAMPLING_INTERVAL = 1*60 # seconds
HISTORY_THRESHOLD = 12 # hours
LED_REFRESH_INTERVAL = 2*60 # seconds
DEVICE_CONTROL_INTERVAL = 15*60 # seconds

PURIFIER_ON_THRESHOLD = 50
PURIFIER_OFF_THRESHOLD = 20

######################################

purifier_on = False

######################################

def update_atmosphere():
    status_atmosphere = False
    try:
        con = sl.connect(DB_NAME, detect_types=sl.PARSE_DECLTYPES | sl.PARSE_COLNAMES)
        cursorObj = con.cursor()
    except Exception as error:
        logging.error("update_atmosphere DB " + str(error))

    while True:
        atmosphere_data=None
        try:
            atmosphere_data = ATMOSPHERIC_SENSOR.get_sensor_data()
        except Exception, exc:
            logging.error(exc)
            status_atmosphere = False
        
        if (atmosphere_data):
            temperature = atmosphere_data.temperature
            humidity = atmosphere_data.humidity
            air_pressure = atmosphere_data.pressure
            status_atmosphere = True
        else:
            status_atmosphere = False

        now = datetime.datetime.now()
        if status_atmosphere :
            try:
                sqlite_insert_with_param = """INSERT INTO 'atmosphere_info'
                                          ('timestamp', 'temperature', 'humidity', 'air_pressure') 
                                          VALUES (?, ?, ?, ?);"""

                data_tuple = (
                    now, temperature, humidity, air_pressure)
                cursorObj.execute(sqlite_insert_with_param, data_tuple)
                con.commit()
                logging.info("atmosphere data added successfully \n")
            except Exception as error:
                logging.error("Insert " + str(error))

        time.sleep(SAMPLING_INTERVAL)
    cursorObj.close()
    con.close()


def update_dust():
    
    try:
        con = sl.connect(DB_NAME, detect_types=sl.PARSE_DECLTYPES | sl.PARSE_COLNAMES)
        cursorObj = con.cursor()
    except Exception as error:
        logging.error("update_dust DB " + str(error))

    while True:
        dust_data=None
        try:
            dust_data = DUST_SENSOR.get_sensor_data()
        except Exception, exc:
            logging.error(exc)
            status_dust = False

        if (dust_data and dust_data[0] and dust_data[1]):
            aqi_index = aqi.to_aqi([
                (aqi.POLLUTANT_PM25, dust_data[0]),
                (aqi.POLLUTANT_PM10, dust_data[1])
            ])
            status_dust = True
        else:
            status_dust = False

        now = datetime.datetime.now()
        if status_dust:
            try:
                sqlite_insert_with_param = """INSERT INTO 'dust_info'
                                          ('timestamp','pm25','pm10','aqi_index') 
                                          VALUES (?, ?, ?, ?);"""

                data_tuple = (
                    now, dust_data[0], dust_data[1], int(aqi_index))
                cursorObj.execute(sqlite_insert_with_param, data_tuple)
                con.commit()
                logging.info("dust data added successfully \n")
            except Exception as error:
                logging.error("Insert " + str(error))


        time.sleep(SAMPLING_INTERVAL)
    cursorObj.close()
    con.close()

def update_co2():

    try:
        con = sl.connect(DB_NAME, detect_types=sl.PARSE_DECLTYPES | sl.PARSE_COLNAMES)
        cursorObj = con.cursor()
    except Exception as error:
        logging.error("update_co2 DB " + str(error))

    while True:
        co2_data=None
        try:
            co2_data = CO2_SENSOR.get_sensor_data()
        except Exception, exc:
            logging.error(exc)
            status_dust = False
        if (co2_data):
            temperature = co2_data["temperature"]
            co2_ppm= co2_data["co2"]
            status_co2 = True
        else:
            status_co2 = False

        if status_co2 :
            now = datetime.datetime.now()
            try:
                sqlite_insert_with_param = """INSERT INTO 'co2_info'
                                          ('timestamp', 'co2_ppm','temperature') 
                                          VALUES (?, ?, ?);"""

                data_tuple = (
                    now, co2_ppm, temperature)
                cursorObj.execute(sqlite_insert_with_param, data_tuple)
                con.commit()
                logging.info("co2 data added successfully \n")
            except Exception as error:
                logging.error("Insert " + str(error))

        time.sleep(SAMPLING_INTERVAL)
    cursorObj.close()
    con.close()

def update_display():

    try:
        con = sl.connect(DB_NAME, detect_types=sl.PARSE_DECLTYPES | sl.PARSE_COLNAMES)
        cursorObj = con.cursor()
    except Exception as error:
        logging.error("update_display DB " + str(error))

    status_atmosphere = False
    status_dust = False

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
        # Get data
        now = datetime.datetime.now()
        try:
            atmosphere_query = """SELECT timestamp,temperature,humidity from atmosphere_info order by timestamp desc LIMIT 1 """
            atmosphere_min_max_query = """SELECT MIN(temperature), MIN(humidity), MAX(temperature), MAX(humidity) from atmosphere_info where timestamp> ? """
            dust_query = """SELECT timestamp,aqi_index from dust_info order by timestamp desc LIMIT 1 """
            dust_min_max_query = """SELECT MIN(aqi_index),MAX(aqi_index) from dust_info where timestamp> ?  """

            cursorObj.execute(atmosphere_query)
            records = cursorObj.fetchone()
            logging.debug(records)

            if records is not None and records[0] is not None and records[1] is not None and records[2] is not None and records[0] >= now - datetime.timedelta(seconds=SAMPLING_INTERVAL):
                status_atmosphere = True
                temperature = records[1]
                humidity = records[2]
            else:
                status_atmosphere = False

            cursorObj.execute(atmosphere_min_max_query, (now - datetime.timedelta(hours=HISTORY_THRESHOLD),))
            records = cursorObj.fetchone()
            logging.debug(records)

            if  records is not None and records[0] is not None and records[1] is not None and records[2] is not None and records[3]:
                low_temperature = records[0]
                low_humidity = records[1]
                high_temperature = records[2]
                high_humidity = records[3]

            cursorObj.execute(dust_query)
            records = cursorObj.fetchone()
            logging.debug(records)

            if records is not None and records[0] is not None and records[1] is not None and records[0] >= now - datetime.timedelta(seconds=SAMPLING_INTERVAL):
                aqi_index = records[1]
                status_dust = True
            else:
                status_dust = False

            cursorObj.execute(dust_min_max_query, (now - datetime.timedelta(hours=HISTORY_THRESHOLD),))
            records = cursorObj.fetchone()
            logging.debug(records)

            if records is not None and records[0] is not None and records[1] is not None :
                low_aqi_index = records[0]
                high_aqi_index = records[1]

        except Exception as error:
            logging.error("Query " + str(error))
            continue

        displayed_data = {
            "status_atmosphere": status_atmosphere,
            "status_dust": status_dust,
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
        LED_DISPLAY.display(displayed_data)
        time.sleep(LED_REFRESH_INTERVAL)

    cursorObj.close()
    con.close()

def control_devices():

    try:
        con = sl.connect(DB_NAME, detect_types=sl.PARSE_DECLTYPES | sl.PARSE_COLNAMES)
        cursorObj = con.cursor()
    except Exception as error:
        logging.error("control_devices DB " + str(error))

    while True:
        time.sleep(DEVICE_CONTROL_INTERVAL)
        # Get data
        now = datetime.datetime.now()
        try:
            atmosphere_query = """SELECT timestamp,temperature,humidity from atmosphere_info order by timestamp desc LIMIT 1 """
            dust_query = """SELECT timestamp,aqi_index from dust_info order by timestamp desc LIMIT 1 """           

            cursorObj.execute(atmosphere_query)
            records = cursorObj.fetchone()
            
            if records is not None and records[0] is not None and records[1] is not None and records[2] is not None and records[0] >= now - datetime.timedelta(seconds=SAMPLING_INTERVAL):
                status_atmosphere = True
                temperature = records[1]
                humidity = records[2]
            else:
                status_atmosphere = False

            cursorObj.execute(dust_query)
            records = cursorObj.fetchone()

            if records is not None and records[0] is not None and records[1] is not None and records[0] >= now - datetime.timedelta(seconds=SAMPLING_INTERVAL):
                aqi_index = records[1]
                status_dust = True
            else:
                status_dust = False
        except Exception as error:
            logging.error("Query " + str(error))
            continue

        if not status_dust or not status_dust:
            continue

        # Control logic
        if not purifier_on and aqi_index > PURIFIER_ON_THRESHOLD:
            result = DEVICE_TRIGGER.turn_on_device(DEVICE_TRIGGER.PURIFIER)
            if result:
                purifier_on = True
        elif purifier_on and aqi_index < PURIFIER_OFF_THRESHOLD:
            result = DEVICE_TRIGGER.turn_off_device(DEVICE_TRIGGER.PURIFIER)
            if result:
                purifier_on = False

    cursorObj.close()
    con.close()


def run_web_dashboard():
    WEB_DASHBOARD.init_web_dashboard(DB_NAME)
    WEB_DASHBOARD.start_web_dashboard()

################################################################################

if __name__ == "__main__":
    logging.basicConfig(format='%(asctime)s - %(levelname)s - %(message)s',level=LOG_LEVEL, datefmt='%d-%b-%y %H:%M:%S')
    # Database
    try:
        con = sl.connect(DB_NAME)
        cursorObj = con.cursor()
        cursorObj.execute("CREATE TABLE atmosphere_info(id integer PRIMARY KEY, timestamp timestamp, temperature FLOAT, humidity FLOAT, air_pressure FLOAT)")
        cursorObj.execute("CREATE TABLE dust_info(id integer PRIMARY KEY, timestamp timestamp, pm25 FLOAT,pm10 FLOAT,aqi_index integer)")
        cursorObj.execute("CREATE TABLE co2_info(id integer PRIMARY KEY, timestamp timestamp, co2_ppm interger, temperature FLOAT)")
    except Exception as error:
        logging.error("Create table " + str(error))
    cursorObj.close()
    con.close()

    atmosphere_thread = threading.Thread(target=update_atmosphere, args=())
    logging.info("Updating Temp and Humidity ...")
    atmosphere_thread.start()

    dust_thread = threading.Thread(target=update_dust, args=())
    logging.info("Updating PM2.5 ...")
    dust_thread.start()

    co2_thread = threading.Thread(target=update_co2, args=())
    logging.info("Updating CO2 ...")
    co2_thread.start()

    display_thread = threading.Thread(target=update_display, args=())
    logging.info("Updating LED display ...")
    display_thread.start()

    device_control_thread = threading.Thread(target=control_devices, args=())
    logging.info("Controlling devices ...")
    device_control_thread.start()

    web_dashboard_thread = threading.Thread(target=run_web_dashboard, args=())
    logging.info("Running web dashboard ...")
    web_dashboard_thread.start()
