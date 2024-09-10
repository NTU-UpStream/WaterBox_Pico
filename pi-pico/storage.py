from sdcard import SDCard
from machine import SPI, Pin
import uos
import logging
import shutil
import json
from config import default_config



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

class Storage():
    
    __slots__ = ('spi', 'cs', 'root_dir', 'logger', 'use_sd')

    def __init__(self, spi: SPI = SPI(0), cs: Pin = Pin(17)):
        self.spi = spi
        self.cs = cs
        self.logger = logger
        self.use_sd = False

    def mount(self):
        try:
            sd = SDCard(self.spi, self.cs)
            vfs = uos.VfsFat(sd)

            # If /external exist. Check if it is a mount point.
            if 'external' in uos.listdir():
                try:
                    uos.umount("/external")
                except Exception as e:
                    self.logger.error(f"Error unmounting /external. Please do not create the /external directory manually.: {e}")

            uos.mount(vfs, "/external")
            self.use_sd = True
            logger.info("SD Card mounted")

        except Exception as e:
            self.use_sd = False
            self.logger.error(f"Unexpected error mounting SDCard: {e}")

    def umount(self):
        try:
            uos.umount("/external")
            self.use_sd = False
            logger.info("SD Card unmounted")
        except Exception as e:
            self.logger.error(f"Unexpected error unmounting SDCard: {e}")

    def save_config(self, config: dict, name: str):
        try:
            with open(name, 'w') as f:
                json.dump(config, f)
        except Exception as e:
            self.logger.warning(f"Error saving config to {name}: {e}")

    def load_config(self) -> dict:
        config_buffer = default_config.copy()
        config = None
        if "external" in uos.listdir('/'):
            config = self._load_config_sdcard()

        if config is None:
            config = self._load_config_internal()
        
        # Merge config with default config
        if config is not None:
            config_buffer.update(config)

        self.save_config(config_buffer, "/config.json")

        return config_buffer

    def _load_config_sdcard(self):
        try:
            with open('/external/config.json', 'r') as f:
                config = json.load(f)
            return config
        except Exception as e:
            self.logger.warning(f"Error loading config from sdcard: {e}")
            return None

    def _load_config_internal(self):
        try:
            with open('/config.json', 'r') as f:
                config = json.load(f)
            return config
        except Exception as e:
            self.logger.warning(f"Error loading config from internal storage: {e}")
            return None

    def save_measurement(self, measurement: dict):
        pass







