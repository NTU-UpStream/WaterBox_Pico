from sdcard import SDCard
from machine import SPI, Pin
import uos
import logging
import shutil

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

            # If /sdcard exist. Check if it is a mount point.
            if 'sdcard' in uos.listdir():
                try:
                    uos.umount("/sdcard")
                except Exception as e:
                    self.logger.error(f"Error unmounting /sdcard. Please do not create the /sdcard directory manually.: {e}")

            uos.mount(vfs, "/sdcard")
            self.use_sd = True
            logger.info("SD Card mounted")

        except Exception as e:
            self.use_sd = False
            self.logger.error(f"Unexpected error mounting SDCard: {e}")

    def umount(self):
        try:
            uos.umount("/sdcard")
            self.use_sd = False
            logger.info("SD Card unmounted")
        except Exception as e:
            self.logger.error(f"Unexpected error unmounting SDCard: {e}")

    def save_config(self, config: dict, name: str):
        pass

    def load_config(self, name: str):
        pass

    def save_measurement(self, measurement: dict):
        pass







