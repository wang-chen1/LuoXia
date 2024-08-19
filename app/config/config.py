import os
import socket
import toml
import shutil
from loguru import logger
from abc import ABC, abstractmethod

root_dir = os.path.dirname(os.path.dirname(os.path.dirname(os.path.realpath(__file__))))
config_file = f"{root_dir}/config.toml"

class ConfigBase(ABC):

    @abstractmethod
    def _load_config(self):
        pass
    
    @abstractmethod
    def __getitem__(self):
        pass
    
    @abstractmethod
    def get(self):
        pass


class Config(ConfigBase):

    def __init__(self):
        self.config = None
        self.hostname = socket.gethostname()

    def _load_config(self):
        if self._config:
            return

        if os.path.isdir(config_file):
            shutil.rmtree(config_file)
        if not os.path.isfile(config_file):
            example_file = f"{root_dir}/config.example.toml"
            if os.path.isfile(example_file):
                shutil.copyfile(example_file, config_file)
                logger.info(f"copy config.example.toml to config.toml")
        logger.info(f"load config from file: {config_file}")

        try:
            self._config = toml.load(config_file)
        except Exception as e:
            logger.warning(f"load config failed: {str(e)}, try to load as utf-8-sig")
            # with open(config_file, mode="r", encoding="utf-8-sig") as fp:
            #     _cfg_content = fp.read()
            #     _config_ = toml.loads(_cfg_content)
        return self._config

    def __getitem__(self, item):
        config = self._load_config()
        return config.get(item)

    def get(self, item, default=None):
        config = self._load_config()
        return config.get(item, default)

