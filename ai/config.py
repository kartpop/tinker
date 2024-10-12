import yaml


class Config:
    _instance = None

    def __new__(cls):
        if cls._instance is None:
            cls._instance = super(Config, cls).__new__(cls)
            cls._instance._load_config()
        return cls._instance

    def _load_config(self):
        with open("config.yml", "r") as file:
            self.config = yaml.safe_load(file)

    def get(self, key, default=None):
        keys = key.split(".")
        value = self.config
        for k in keys:
            value = value.get(k, default)
            if value is default:
                break
        return value


config = Config()
