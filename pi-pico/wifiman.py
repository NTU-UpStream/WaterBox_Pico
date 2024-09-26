import network
import asyncio
import time
import logging
import ubinascii
from machine import Pin

try:
    from waterbox import WaterBox
except ImportError:
    pass

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

class WiFiManager:
    def __init__(self, status_led: Pin):
        self.wlan = network.WLAN(network.STA_IF)
        self.ap = network.WLAN(network.AP_IF)
        self.status_led = status_led
        self.logger = logger
        self.sta_ip = None

    async def connect_sta(self, ssid, passwd, max_attempts=10):
        self.wlan.active(True)
        self.logger.info(f"Connecting to WiFi... SSID: {ssid}, Password: {passwd}")

        for _ in range(max_attempts):
            if self.wlan.isconnected():
                return True

            self.wlan.connect(ssid, passwd)
            for _ in range(10):
                self.status_led.on()
                await asyncio.sleep(0.01)
                self.status_led.off()
    
                if self.wlan.isconnected():
                    self.logger.info(f"Connected to WiFi: {ssid}, IP: {self.wlan.ifconfig()[0]}")
                    self.sta_ip = self.wlan.ifconfig()[0]
                    return True
                await asyncio.sleep(1)
            self.logger.warning("Failed to connect to WiFi. Retrying...")

        self.logger.error("Failed to connect to WiFi.")
        self.wlan.active(False)        
        return False
    
    async def setup_ap(self, ssid, passwd):
        self.ap.config(ssid=ssid, password=passwd)
        self.ap.active(True)
        self.logger.info(f"Setting up Access Point... SSID: {ssid}, Password: {passwd}")

        while not self.ap.active():
            self.status_led.on()
            await asyncio.sleep(0.01)
            self.status_led.off()
            await asyncio.sleep(1)
        
        self.logger.info(f"Access Point activated: {ssid}, IP: {self.ap.ifconfig()[0]}")
        return True
    
    async def switch_mode(self, ssid, passwd, mode='sta'):
        self.wlan.disconnect()
        self.wlan.active(False)
        self.ap.active(False)
        self.ap.disconnect()

        await asyncio.sleep(1)

        if mode == 'sta':
            return await self.connect_sta(ssid, passwd)
        elif mode == 'ap':
            return await self.setup_ap(ssid, passwd)
        else:
            self.logger.error(f"Invalid mode: {mode}")
            return False
        
    def status(self):
        if self.wlan.active():
            if self.wlan.isconnected():
                return "Connected"
            else:
                return "Connecting"
        elif self.ap.active():
            return "AP Mode"
        else:
            return "Inactive"

    def mac(self):
        mac = self.wlan.config('mac')
        return mac_bytes_to_string(mac)        

def mac_bytes_to_string(mac_bytes):
    return ':'.join(['{:02x}'.format(b) for b in mac_bytes])