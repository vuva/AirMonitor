import time
import sys
sys.path.append('./drive')
import SPI
import SSD1305
import RPi.GPIO as GPIO

from PIL import Image
from PIL import ImageDraw
from PIL import ImageFont

import subprocess

import sqlite3 as sl
import datetime
import math
import aqi
import sensor_bme280 as BME280_SENSOR
import sensor_sds011 as SDS011_SENSOR

SAMPLING_INTERVAL = 120 - 60 # seconds
HISTORY_THRESHOLD = 12 # hours

# Raspberry Pi pin configuration:
RST = 25     # on the PiOLED this pin isnt used
# Note the following are only used with SPI:
DC = 24
SPI_PORT = 0
SPI_DEVICE = 0

# Beaglebone Black pin configuration:
# RST = 'P9_12'
# Note the following are only used with SPI:
# DC = 'P9_15'
# SPI_PORT = 1
# SPI_DEVICE = 0

# 128x32 display with hardware I2C:
#disp = SSD1305.SSD1305_128_32(rst=RST)

# 128x64 display with hardware I2C:
# disp = SSD1305.SSD1305_128_64(rst=RST)

# Note you can change the I2C address by passing an i2c_address parameter like:
# disp = SSD1305.SSD1305_128_64(rst=RST, i2c_address=0x3C)

# Alternatively you can specify an explicit I2C bus number, for example
# with the 128x32 display you would use:
# disp = SSD1305.SSD1305_128_32(rst=RST, i2c_bus=2)

# 128x32 display with hardware SPI:
#disp = SSD1305.SSD1305_128_32(rst=RST, dc=DC, spi=SPI.SpiDev(SPI_PORT, SPI_DEVICE, max_speed_hz=8000000))

# 128x64 display with hardware SPI:
# disp = SSD1305.SSD1305_128_64(rst=RST, dc=DC, spi=SPI.SpiDev(SPI_PORT, SPI_DEVICE, max_speed_hz=8000000))

# Alternatively you can specify a software SPI implementation by providing
# digital GPIO pin numbers for all the required display pins.  For example
# on a Raspberry Pi with the 128x32 display you might use:
disp = SSD1305.SSD1305_128_32(rst=RST, dc=DC, sclk=11, din=10, cs=8)

# Initialize library.
disp.begin()

# Clear display.
disp.clear()
disp.display()

# Create blank image for drawing.
# Make sure to create image with mode '1' for 1-bit color.
width = disp.width
height = disp.height
image = Image.new('1', (width, height))
# Get drawing object to draw on image.
draw = ImageDraw.Draw(image)

# Draw a black filled box to clear the image.
draw.rectangle((0,0,width,height), outline=0, fill=0)

# Draw some shapes.
# First define some constants to allow easy resizing of shapes.
padding = 0
top = padding
bottom = height-padding
# Move left to right keeping track of the current x position for drawing shapes.
x = 0


# Load default font.
#font = ImageFont.load_default()

# Alternatively load a TTF font.  Make sure the .ttf font file is in the same directory as the python script!
# Some other nice fonts to try: http://www.dafont.com/bitmap.php
header_font = ImageFont.truetype('fonts/Minecraftia-Regular.ttf',8)
main_font = ImageFont.truetype('fonts/C&C Red Alert [INET].ttf',16)
footer_font = ImageFont.truetype('fonts/PIXEARG_.TTF',8)

# Database
try:
    con = sl.connect('air-monitor.db')
    cursorObj = con.cursor()
    cursorObj.execute(
        "CREATE TABLE air_info(id integer PRIMARY KEY, timestamp datetime, temperature FLOAT, humidity FLOAT, air_pressure FLOAT,pm25 FLOAT,pm10 FLOAT,aqi_index integer, status_bme280 bool, status_sds011 bool)")
except Exception as error:
    print("Create table " + str(error))



status_bme280=False
status_sds011=False

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

    # Get temp, humis, and air pressure data
    bme280_data = BME280_SENSOR.get_sensor_data()
    if (bme280_data):
        temperature = bme280_data.temperature
        humidity = bme280_data.humidity
        air_pressure = bme280_data.pressure
        status_bme280 = True
    else:
        status_bme280 = False

    # Get PM2.5 and PM10 data
    sds011_data = SDS011_SENSOR.get_sensor_data()
    if (sds011_data[0] and sds011_data[1]):
        aqi_index = aqi.to_aqi([
            (aqi.POLLUTANT_PM25, sds011_data[0]),
            (aqi.POLLUTANT_PM10, sds011_data[1])
        ])
        status_sds011 = True
    else:
        status_sds011 = False

    now=datetime.datetime.now()
    if status_bme280 or status_sds011 :
        try:
            sqlite_insert_with_param = """INSERT INTO 'air_info'
                                      ('timestamp', 'temperature', 'humidity', 'air_pressure','pm25','pm10','aqi_index', 'status_bme280','status_sds011') 
                                      VALUES (?, ?, ?, ? ,? ,? ,? ,?, ?);"""

            data_tuple = (now,temperature, humidity, air_pressure, sds011_data[0], sds011_data[1], int(aqi_index), status_bme280, status_bme280)
            cursorObj.execute(sqlite_insert_with_param, data_tuple)
            con.commit()
            print("Data added successfully \n")
        except Exception as error:
            print("Insert " + str(error))

    # Get history data
    try:
        sqlite_select_query = """SELECT MIN(temperature), MIN(humidity),MIN(aqi_index) from air_info where timestamp> ? and status_bme280=1 and status_sds011 =1 """
        cursorObj.execute(sqlite_select_query, (now - datetime.timedelta(hours=HISTORY_THRESHOLD),))
        records = cursorObj.fetchall()

        for row in records:
            low_temperature = row[0]
            low_humidity = row[1]
            low_aqi_index= row[2]
        print("MIN: ", low_temperature, low_humidity, low_aqi_index)

        sqlite_select_query = """SELECT MAX(temperature), MAX(humidity), MAX(aqi_index) from air_info where timestamp> ?"""
        cursorObj.execute(sqlite_select_query, (now - datetime.timedelta(hours=HISTORY_THRESHOLD),))
        records = cursorObj.fetchall()
    
        for row in records:
            high_temperature = row[0]
            high_humidity = row[1]
            high_aqi_index = row[2]

        print("MAX: ", high_temperature, high_humidity, high_aqi_index)
    except Exception as error:
        print("Query " + str(error))

    # Draw a black filled box to clear the image.
    draw.rectangle((0, 0, width, height), outline=0, fill=0)

    draw.text((x, top),    "Temp" + u'\u00B0' +"C"   ,  font=header_font, fill=255)
    draw.text((x+44, top),  "Humid%" ,  font=header_font, fill=255)
    draw.text((x+88, top), "AQI", font=header_font, fill=255)
    draw.text((x+114, top), "V" if status_bme280 else "X" , font=header_font, fill=255)
    draw.text((x + 121, top), "V" if status_sds011 else "X", font=header_font, fill=255)

    draw.text((x, top + 9), "{:.1f}".format(temperature), font=main_font, fill=255)
    draw.text((x + 44, top + 9), "{:.1f}".format(humidity), font=main_font, fill=255)
    draw.text((x + 88, top + 9), "{:.0f}".format(aqi_index), font=main_font, fill=255)

    draw.text((x, top+ 23), "{:.0f}-{:.0f}".format(math.floor(low_temperature),math.ceil(high_temperature)), font=footer_font, fill=255)
    draw.text((x + 44, top + 23), "{:.0f}-{:.0f}".format(math.floor(low_humidity),math.ceil(high_humidity)), font=footer_font, fill=255)
    draw.text((x + 88, top + 23), "{:.0f}-{:.0f}".format(math.floor(low_aqi_index),math.ceil(high_aqi_index)), font=footer_font, fill=255)



    # Display image.
    disp.image(image)
    disp.display()
    time.sleep(SAMPLING_INTERVAL)

cursorObj.close()
con.close()
