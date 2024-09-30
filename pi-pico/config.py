from microdot import MultiDict
import logging

try:
    from typing import Union, Optional
except ImportError:
    pass

default_config = {
    "id": "WaterBox",
    "sample_period": "300", # seconds
    "wifi": {
        "boot_as": "ap",
        "sta": {
            "ssid": "waterbox",
            "password": "waterbox",
            "max_attempts": "10",
        },
        "ap": {
            "ssid": "WaterBox",
            "password": "waterbox",
        }
    },
    "mqtt": {
        "host": "broker.emqx.io",
        "port": "1883",
    }
}

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

class WaterBoxConfig(dict):
    def __init__(self, config: Optional[dict] = None):
        self.logger = logger
        if config is not None:
            super().__init__(config)
        else:
            super().__init__(default_config)

    def update(self, config: Union[dict, MultiDict]) -> bool:
        if isinstance(config, MultiDict):
            self.update_multidict(self, config)
        elif isinstance(config, dict):
            self.update_dict(self, config)
        else:
            return False
        
        
        return True
    
    @staticmethod
    def update_dict(config, update_config: dict):
        for key, value in update_config.items():
            if isinstance(value, dict):
                config[key] = WaterBoxConfig.update_dict(config.get(key, {}), value)
            elif isinstance(value, MultiDict):
                config[key] = WaterBoxConfig.update_multidict(config.get(key, {}), value)
            else:
                if not isinstance(config.get(key), type(value)):
                    logger.error(f"Invalid config type for key {key}. Expected {type(config.get(key))}, got {type(value)} with value {value}")
                    continue
                config[key] = value
        return config
    
    @staticmethod
    def update_multidict(config, update_config: MultiDict):
        for key, value in update_config.items():
            if isinstance(value, list):
                value = value[0]

            if isinstance(value, MultiDict):
                config[key] = WaterBoxConfig.update_multidict(config.get(key, {}), value)
            elif isinstance(value, dict):
                config[key] = WaterBoxConfig.update_dict(config.get(key, {}), value)
            else:
                if not isinstance(config.get(key), type(value)):
                    logger.error(f"Invalid config type for key {key}. Expected {type(config.get(key))}, got {type(value)} with value {value}")
                    continue
                config[key] = value
        return config
