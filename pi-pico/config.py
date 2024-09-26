default_config = {
    "id": "WaterBox",
    "sample_period": 300, # seconds
    "wifi": {
        "boot_as": "ap",
        "sta": {
            "ssid": "waterbox",
            "password": "waterbox",
            "max_attempts": 10,
        },
        "ap": {
            "ssid": "WaterBox",
            "password": "waterbox",
        }
    },
    "mqtt": {
        "host": "broker.emqx.io",
        "port": 1883,
    }
}

class ConfigValidator():
    def __init__(self, config):
        self.config = config