import math
import RPi.GPIO as GPIO

import SPI
import SSD1305
from PIL import Image
from PIL import ImageDraw
from PIL import ImageFont



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



def display(displayed_data):
    low_temperature =  displayed_data["low_temperature"]
    low_humidity =  displayed_data["low_humidity"]
    low_aqi_index =  displayed_data["low_aqi_index"]
    high_temperature =  displayed_data["high_temperature"]
    high_humidity  =  displayed_data["high_humidity"]
    high_aqi_index =  displayed_data["high_aqi_index"]
    temperature =  displayed_data["temperature"]
    humidity =  displayed_data["humidity"]
    aqi_index =  displayed_data["aqi_index"]
    status_bme280 =  displayed_data["status_bme280"]
    status_sds011 =  displayed_data["status_sds011"]

    print("MIN: ", low_temperature, low_humidity, low_aqi_index)
    print("MAX: ", high_temperature, high_humidity, high_aqi_index)
    print("Current: ", temperature, humidity, aqi_index)
    print("Refreshing display ...")
    # Draw a black filled box to clear the image.
    draw.rectangle((0, 0, width, height), outline=0, fill=0)

    draw.text((x, top), "Temp" + u'\u00B0' + "C", font=header_font, fill=255)
    draw.text((x + 44, top), "Humid%", font=header_font, fill=255)
    draw.text((x + 88, top), "AQI", font=header_font, fill=255)
    draw.text((x + 114, top), "L" if status_bme280 else "X", font=header_font, fill=255)
    draw.text((x + 121, top), "Y" if status_sds011 else "X", font=header_font, fill=255)

    draw.text((x, top + 9), "{:.1f}".format(temperature), font=main_font, fill=255)
    draw.text((x + 44, top + 9), "{:.1f}".format(humidity), font=main_font, fill=255)
    draw.text((x + 88, top + 9), "{:.0f}".format(aqi_index), font=main_font, fill=255)

    draw.text((x, top + 23), "{:.0f}-{:.0f}".format(math.floor(low_temperature), math.ceil(high_temperature)),
              font=footer_font, fill=255)
    draw.text((x + 44, top + 23), "{:.0f}-{:.0f}".format(math.floor(low_humidity), math.ceil(high_humidity)),
              font=footer_font, fill=255)
    draw.text((x + 88, top + 23), "{:.0f}-{:.0f}".format(math.floor(low_aqi_index), math.ceil(high_aqi_index)),
              font=footer_font, fill=255)

    # Display image.
    disp.image(image)
    disp.display()
