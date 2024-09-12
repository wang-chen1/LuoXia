import os
import shutil
import socket
from functools import lru_cache

import toml

root_dir = os.path.dirname(os.path.dirname(os.path.dirname(os.path.realpath(__file__))))
config_file = f"{root_dir}/config.toml"


class Configuration:

    def __init__(self):
        self._config = None
        self.hostname = socket.gethostname()

    @property
    @lru_cache()
    def config(self):
        if os.path.isdir(config_file):
            shutil.rmtree(config_file)
        if not os.path.isfile(config_file):
            example_file = f"{root_dir}/config.example.toml"
            if os.path.isfile(example_file):
                shutil.copyfile(example_file, config_file)
        #         logger.debug(f"copy config.example.toml to config.toml")
        # logger.debug(f"load config from file: {config_file}")

        if self._config is None:
            with open(config_file, mode="r", encoding="utf-8-sig") as f:
                self._config = toml.load(f)
        return self._config

    def __getattr__(self, name):
        if name in self.config:
            value = self.config[name]
            if isinstance(value, dict):
                return Configuration.from_dict(value)
            return value
        raise AttributeError(f"No such attribute: {name}")

    @classmethod
    def from_dict(cls, config_dict):
        instance = cls()
        instance._config = config_dict
        return instance
