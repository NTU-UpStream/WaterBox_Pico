import ujson as json
import uos
import config as cfg
from sdcard import sdcard
from machine import SPI, Pin

SD_SCK = 18
SD_CS = 17
SD_MOSI = 19
SD_MISO = 16


class WaterBox():
    def __init__(self, config: str | dict | None = None):
        self.init_sdcard()
        
        if config is None:
            self.config = cfg.default_config
        if isinstance(config, dict):
            self.config = cfg.parse_config(config)
        
        

    def init_sdcard(self):
        self.sdcard = sdcard.SDCard(SPI(0, sck=Pin(SD_SCK), mosi=Pin(SD_MOSI), miso=Pin(SD_MISO)), Pin(SD_CS))
        self.storage = uos.VfsFat(self.sdcard)
        uos.mount(self.storage, "/sd")

    def setup(self):
        pass
        