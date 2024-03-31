import yaml
from .logger import LOG

class ConfigLoader:
    def __init__(self, config_path):
        self.config_path = config_path

    def load_config(self):
        LOG.info("Loading config from {}".format(self.config_path))
        with open(self.config_path, "r") as f:
            config = yaml.safe_load(f)
        return config