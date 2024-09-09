import ujson as json
import uos
import config
import logging
from machine import SPI, Pin
from webpage import app
import network
import time
import usys

from storage import Storage
from hardware_config import SD_CS, SD_MOSI, SD_MISO, SD_SCK, POWER_PIN


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

class WaterBox():

    __slots__ = ('logger', 'storage', 'power', 'config', 'webpage', 'ap')

    def __init__(self):
        self.logger = logger
        self.power = Pin(POWER_PIN, Pin.OUT)
        self.power.off()
        self.storage = Storage(SPI(0, sck=Pin(SD_SCK), mosi=Pin(SD_MOSI), miso=Pin(SD_MISO)), Pin(SD_CS))
        self.webpage = app
        self.ap = network.WLAN(network.AP_IF)

    def setup(self, **kwargs):
        self.power.on()
        self.storage.mount()
        self.config = self.storage.load_config()

    def access_mode(self):
        try:
            self.logger.info("Entering access mode...")
            
            # Disable the station interface if it's active
            sta_if = network.WLAN(network.STA_IF)
            if sta_if.active():
                sta_if.active(False)
            
            # Configure the access point
            self.ap.active(True)
            ssid = self.config.get('wifi_ssid', 'WaterBox')
            password = self.config.get('wifi_password', 'waterbox')
            
            self.ap.config(essid=ssid, password=password)
            
            # Wait for the access point to be active
            while not self.ap.active():
                time.sleep(0.1)
            
            self.logger.info(f"Access Point active. SSID: {ssid}, IP: {self.ap.ifconfig()}")
            
            # Start the configuration web server
            self.webpage.run(debug=True)
        
        except Exception as e:
            self.logger.error(f"Error in access mode: {str(e)}")
        finally:
            # Clean up and exit access mode
            self.ap.active(False)
            self.logger.info("Exiting access mode")

    def run(self):
        pass

