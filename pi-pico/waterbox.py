import ujson as json
import uos
import config
import logging
from machine import SPI, Pin

from storage import Storage
from hardware_config import SD_CS, SD_MOSI, SD_MISO, SD_SCK, POWER_PIN


logger = logging.getLogger(__name__)

stream_handler = logging.StreamHandler()
file_handler = logging.FileHandler("logging.log")

stream_handler.setLevel(logging.INFO)
file_handler.setLevel(logging.WARNING)

formatter = logging.Formatter('%(asctime)s - %(name)s - %(levelname)s - %(message)s')

stream_handler.setFormatter(formatter)
file_handler.setFormatter(formatter)

logger.addHandler(stream_handler)
logger.addHandler(file_handler)

class WaterBox():

    __slots__ = ('logger', 'storage', 'power')

    def __init__(self):
        self.logger = logger
        self.storage = Storage(SPI(0, sck=Pin(SD_SCK), mosi=Pin(SD_MOSI), miso=Pin(SD_MISO)), Pin(SD_CS))
        self.power = Pin(POWER_PIN, Pin.OUT)

    def setup(self, **kwargs):
        self.power.on()
        self.storage.mount()
