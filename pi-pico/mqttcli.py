from mqtt import MQTTClient
import asyncio
import logging

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

class WaterBoxMQTTClient():
    def __init__(self):
        self.logger = logger
    
    def setup(self, **kwargs):
        self.client = MQTTClient(**kwargs)
    
    def connect(self):
        try:
            result = self.client.connect()
            return result
        except Exception as e:
            self.logger.error(f"Error connecting to MQTT: {e}")
            return False

    def disconnect(self):
        try:
            self.client.disconnect()
        except Exception as e:
            self.logger.error(f"Error disconnecting from MQTT: {e}")

    def publish(self, topic, msg, retain=False, qos=0):
        try:
            self.client.publish(topic, msg, retain=retain, qos=qos)
        except Exception as e:
            self.logger.error(f"Error publishing to MQTT: {e}")
