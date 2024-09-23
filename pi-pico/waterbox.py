try:
    from typing import Optional
except ImportError:
    pass

import logging
from machine import SPI, Pin
from webpage import WaterBoxWebPage
import network
import time
import asyncio
import aiorepl

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

    __slots__ = ('logger', 'storage', 'power', 'config', 'webpage', 'ap', 'access_ctrl', 'breathe_led', 'access_mode_task')

    def __init__(self):
        self.logger = logger
        self.power = Pin(POWER_PIN, Pin.OUT)
        self.power.off()
        self.storage = Storage(SPI(0, sck=Pin(SD_SCK), mosi=Pin(SD_MOSI), miso=Pin(SD_MISO)), Pin(SD_CS))
        self.webpage = WaterBoxWebPage(self)
        self.ap = network.WLAN(network.AP_IF)
        self.access_ctrl = Pin(7, Pin.IN, Pin.PULL_UP)
        self.breathe_led = Pin(20, Pin.OUT)
        self.access_mode_task: Optional[asyncio.Task] = None

    def setup(self, **kwargs):
        self.power.on()
        self.storage.mount()
        self.config = self.storage.load_config()

    async def breathing(self):
        while True:
            self.breathe_led.on()
            await asyncio.sleep(0.01)
            self.breathe_led.off()
            await asyncio.sleep(1)

    async def start_operation(self):
        self.access_mode_task = None
        breathe_task = asyncio.create_task(self.breathing())
        repl = asyncio.create_task(aiorepl.task())
        try:
            while True:
                self.check_access_mode()
                
                # Your main WaterBox process logic here
                await asyncio.sleep(1)  # Adjust as needed
        
        except asyncio.CancelledError:
            self.logger.info("Operation cancelled")

    def check_access_mode(self) -> None:
        if self.access_ctrl.value() == 1:
            if (self.access_mode_task is not None) and (not self.access_mode_task.done()):
                return
            
            self.access_mode_task = asyncio.create_task(self.access_on())
            self.logger.info("Access mode started")
        else:
            if (self.access_mode_task is None) or self.access_mode_task.done():
                return
            
            self.access_mode_task.cancel()
            self.logger.info("Access mode stopped")
            self.access_mode_task = None

    async def access_on(self):
        try:
            self.logger.info("Entering access mode...")
            
            # Disable the station interface if it's active
            sta_if = network.WLAN(network.STA_IF)
            if sta_if.active():
                sta_if.active(False)
            
            # Configure the access point
            ssid = self.config.get('wifi_ssid', 'WaterBox')
            password = self.config.get('wifi_password', 'waterbox')
            self.ap.config(essid=ssid, password=password)
            self.ap.active(True)

            # Wait for the access point to be active
            while not self.ap.active():
                await asyncio.sleep(0.1)
            
            self.logger.info(f"Access Point active. SSID: {ssid}, IP: {self.ap.ifconfig()[0]}")
            
            # Start the configuration web server
            await self.webpage.start_server(debug=True)
        
        except asyncio.CancelledError:
            self.logger.info("Access mode cancelled")

            # Clean up and exit access mode
            self.webpage.shutdown()

        finally:
            # Clean up and exit access mode
            self.ap.active(False)
            self.logger.info("Exiting access mode")

    def run(self):
        asyncio.run(self.start_operation())

