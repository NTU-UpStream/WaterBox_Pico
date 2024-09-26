from machine import I2C, Pin
from ads1x15 import ADS1115
import logging
import utime

logger: logging.Logger = logging.getLogger(__name__)
logger.setLevel(logging.INFO)

stream_handler = logging.StreamHandler()
file_handler = logging.FileHandler("logging.log")

stream_handler.setLevel(logging.INFO)
file_handler.setLevel(logging.WARNING)

formatter = logging.Formatter('%(asctime)s - %(name)s - %(levelname)s - %(message)s')

stream_handler.setFormatter(formatter)
file_handler.setFormatter(formatter)

logger.addHandler(stream_handler)
logger.addHandler(file_handler)

class WaterBoxAnalog():
    def __init__(self, i2c: I2C):
        self.logger = logger
        self.ads = ADS1115(i2c, address=0x48, gain=1)
    
    def read_all(self) -> list[float]:
        values = []
        try:
            for channel in range(4):
                value = self.ads.read(channel1=channel)
                voltage = self.ads.raw_to_v(value)
                values.append(voltage)
            return values
        except Exception as e:
            self.logger.error(f"Error reading analog values: {e}")
            return [0, 0, 0, 0]