default_config = {
    "id": "WaterBox",
    "sample_period": 300, # seconds
    "wifi_ssid": "WaterBox",
    "wifi_password": "waterbox",
}

def parse_config(config: dict) -> dict:
    return config