from machine import UART, Pin
from nbiot import LTEIOT6_Click
import time

config = {"apn": "iot4ga2",
          "mqtt_id": "123456789",
          "mqtt_server_address": "140.112.12.62",
          "mqtt_server_port": "1883",
          "mqtt_topic": "waterbox_pico/test",
          "mqtt_username": "waterbox_pico",
          "mqtt_password": "waterbox_pico",
          }

urt = UART(0, 115200, tx=0, rx=1)
pwr = Pin(2, Pin.OUT, Pin.PULL_DOWN)
urt.init()

iot = LTEIOT6_Click(urt, pwr, config)

def talk(command):
    iot._send_command(command)
    result = iot._rsp_check(timeout=10000)

if __name__ == "__main__":
    iot.init()
    iot.attach()
    iot.send_message("Hello World!")
    iot.power_off()
