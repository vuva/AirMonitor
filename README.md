# Indoor Climate Control
A Raspberry Pi air monitor: temperature, humidity, air pressure, PM2.5, PM10, AQI.
- Use sensor BME280 for temperature, humidity, air pressure via I2C interface.
- Use sensor Nova SDS011 for PM2.5, PM10 via USB interface.
- AQI is calculated with python-aqi EPA algorithm.
- Display using an SSD1305 2.23 inch OLED screen via SPI interface.
- Use IFTTT webhook to control air purifier/conditioner with smart WiFi plugs.

Tutorial: https://www.instructables.com/Raspberry-Pi-Indoor-Climate-Monitoring-and-Control/

## Software Prequisites:

1. Enable I2C and SPI .

2. Install dependancies:
```
$ sudo apt install python-pip

$ pip install python-aqi

$ pip install smbus2
$ pip install RPi-bme280

$ sudo apt-get install python-pil
$ sudo apt-get install python-numpy
$ pip install RPi.GPIO
$ pip install spidev

$ pip install pyserial

$ pip install requests
```

## Usage:
```
$ python indoor_climate_control.py
```
Have fun !
