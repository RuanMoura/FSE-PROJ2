import smbus2
import bme280

class BME_CLASS():
    def __init__(self) -> None:
        port = 1
        address = 0x76
        bus = smbus2.SMBus(port)
        calibration_params = bme280.load_calibration_params(bus, address)
        self.data = bme280.sample(bus, address, calibration_params)

    def get_temperature(self):
        return self.data.temperature

    def get_pressure(self):
        return self.data.pressure

    def get_humidity(self):
        return self.data.humidity
