import ujson as json
import uos
import config
import logutils
import sdcard
from machine import SPI, Pin

SD_SCK = 18
SD_CS = 17
SD_MOSI = 19
SD_MISO = 16

class WaterBox():
    def __init__(self):
        self.logger = logutils.get_logger("WaterBox")

    def init_sdcard(self):
        try:
            self.sdcard = sdcard.SDCard(SPI(0, sck=Pin(SD_SCK), mosi=Pin(SD_MOSI), miso=Pin(SD_MISO)), Pin(SD_CS))
            storage = uos.VfsFat(self.sdcard)
            uos.mount(storage, "/sd")
        except Exception as e:
            self.logger.error(f"Error initializing SD card: {e}", fn="WaterBox.init_sdcard()")
            self.sdcard = None
            return

    def setup(self, **kwargs):
        self.init_sdcard()

        config_path = kwargs.get("config", 'waterbox_config.json')
        self._load_config(config_path)

    def _load_config(self, config_path: str):
        if config_path in uos.listdir("/"):
            with open(config_path, "r") as f:
                try:
                    loaded_config = json.load(f)
                except Exception as e:
                    self.logger.error(f"Error loading config file: {e}, Using default config", fn="WaterBox._load_config()")
                    return
                self.config = config.parse_config(loaded_config)
            return
        elif "/sd" in uos.listdir("/") and config_path in uos.listdir("/sd"):
            with open(f"/sd/{config_path}", "r") as f:
                try:
                    loaded_config = json.load(f)
                except Exception as e:
                    self.logger.error(f"Error loading config file: {e}, Using default config", fn="WaterBox._load_config()")
                    return
                self.config = config.parse_config(loaded_config)
            return
        else:
            self.logger.error(f"Config file not found: {config_path}, Using default config", fn="WaterBox._load_config()")
            self.config = config.default_config