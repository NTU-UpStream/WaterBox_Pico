try:
    from typing import Optional
except ImportError:
    pass

import logging
from machine import SPI, Pin, I2C
from webpage import WaterBoxWebPage
from wifiman import WiFiManager
from microdot import Microdot
from analog import WaterBoxAnalog
from mqttcli import WaterBoxMQTTClient
from config import WaterBoxConfig
import network
import time
import asyncio
import aiorepl

from storage import Storage
from hardware_config import SD_CS, SD_MOSI, SD_MISO, SD_SCK, POWER_PIN
from rp2 import bootsel_button


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

    __slots__ = ('logger', 'storage', 'power', 'config', 'webpage', 'adc_ctrl', 'wifiman', 'breathe_led', 'analog', 'mqtt')

    def __init__(self):
        self.logger = logger
        self.power = Pin(POWER_PIN, Pin.OUT)
        self.power.off()
        self.breathe_led = Pin(20, Pin.OUT)
        self.adc_ctrl = Pin(8, Pin.OUT)

        self.storage = Storage(SPI(0, sck=Pin(SD_SCK), mosi=Pin(SD_MOSI), miso=Pin(SD_MISO)), Pin(SD_CS))
        self.webpage = WaterBoxWebPage(self)
        self.wifiman = WiFiManager(Pin(15, Pin.OUT))
        self.analog = WaterBoxAnalog(I2C(0, scl=Pin(5), sda=Pin(4)))
        self.mqtt = WaterBoxMQTTClient()
        self.config = WaterBoxConfig()

    def setup(self, **kwargs):
        self.adc_ctrl.on()
        self.power.on()
        self.storage.mount()
        self.config.update(self.storage.load_config())
        self.mqttsetup()
        # self.mqtt.setup(client_id=self.wifiman.mac(), server=

    def run(self):
        asyncio.run(self.start_operation())

    def reload_config(self):
        self.config.update(self.storage.load_config())

    def mqttsetup(self):
        client_id = "WaterBox-"+self.wifiman.mac()
        server = self.config.get('mqtt', {}).get('host', 'broker.emqx.io')
        port = self.config.get('mqtt', {}).get('port', 1883)
        self.mqtt.setup(client_id=client_id, server=server, port=port)

    async def start_operation(self):
        breathe_task = asyncio.create_task(self.breathing())
        repl = asyncio.create_task(aiorepl.task())
        webpage = asyncio.create_task(self.webpage.start_server(debug=True))
        wifi = asyncio.create_task(self.wifi_manager())

        try:
            while True:
                # Your main WaterBox process logic here
                await asyncio.sleep(1)  # Adjust as needed
        
        except asyncio.CancelledError:
            self.logger.info("Operation cancelled")

    async def breathing(self):
        while True:
            self.breathe_led.on()
            await asyncio.sleep(0.01)
            self.breathe_led.off()
            await asyncio.sleep(1)
    
    async def wifi_manager(self):
        mode = self.config.get('wifi', {}).get('boot_as', 'sta').lower()
        ap_ssid = self.config.get('wifi', {}).get('ap', {}).get('ssid', 'WaterBox')
        ap_passwd = self.config.get('wifi', {}).get('ap', {}).get('password', 'waterbox')
        sta_ssid = self.config.get('wifi', {}).get('sta', {}).get('ssid', '')
        sta_passwd = self.config.get('wifi', {}).get('sta', {}).get('password', '')

        self.logger.info(f"Starting WiFi Manager in {mode} mode")
        if mode == 'ap':
            await self.wifiman.switch_mode(ap_ssid, ap_passwd, mode='ap')
        elif mode == 'sta':
            await self.wifiman.switch_mode(sta_ssid, sta_passwd, mode='sta')

        while True:
            if bootsel_button():
                ap_ssid = self.config.get('wifi', {}).get('ap', {}).get('ssid', 'WaterBox')
                ap_passwd = self.config.get('wifi', {}).get('ap', {}).get('password', 'waterbox')
                sta_ssid = self.config.get('wifi', {}).get('sta', {}).get('ssid', '')
                sta_passwd = self.config.get('wifi', {}).get('sta', {}).get('password', '')
                if mode == 'ap':
                    mode = 'sta'
                    result = await self.wifiman.switch_mode(sta_ssid, sta_passwd, mode='sta')
                    if result is False:
                        self.logger.error("Failed to connect to WiFi. Falling back to AP mode.")
                        await self.wifiman.switch_mode(ap_ssid, ap_passwd, mode='ap')
                        mode = 'ap'

                elif mode == 'sta':
                    await self.wifiman.switch_mode(ap_ssid, ap_passwd, mode='ap')
                    mode = 'ap'
                
                # Wait for the button to be released
                while bootsel_button():
                    await asyncio.sleep(0.1)
                
            await asyncio.sleep(1)

