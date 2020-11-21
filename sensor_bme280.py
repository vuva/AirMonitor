import smbus2
import bme280
import logging

port = 1
address = 0x76
bus = smbus2.SMBus(port)


def get_sensor_data():
    try:
        calibration_params = bme280.load_calibration_params(bus, address)

        # the sample method will take a single reading and return a
        # compensated_reading object
        data = bme280.sample(bus, address, calibration_params)

                # there is a handy string representation too
        logging.info(data)
        return data
    except Exception as error:
        logging.error('Caught this error: ' + repr(error))

    return None
