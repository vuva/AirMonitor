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

import sensor_bme280 as BME280_SENSOR
import sensor_sds011 as SDS011_SENSOR

SAMPLING_INTERVAL = 120 - 70
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
footer_font = ImageFont.truetype('fonts/PIXELADE.TTF',8)

status="V"
temperature = -271.13
humidity = 0
air_pressure = 0
aqi_index = -1

while True:

    # Draw a black filled box to clear the image.
    draw.rectangle((0,0,width,height), outline=0, fill=0)

    # Get temp, humis, and air pressure data


    # Write two lines of text.
    draw.text((x, top),    "Temp" + u'\u00B0' +"C"   ,  font=header_font, fill=255)
    draw.text((x, top),  "Humid%" ,  font=header_font, fill=255)
    draw.text((x, top), "AQI", font=header_font, fill=255)
    draw.text((x, top), status , font=header_font, fill=255)



    # Display image.
    disp.image(image)
    disp.display()
    time.sleep(SAMPLING_INTERVAL)
