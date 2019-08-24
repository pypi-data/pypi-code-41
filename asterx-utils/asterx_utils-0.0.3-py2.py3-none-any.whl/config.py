import os


class Config():
    DEFAULT_CONFIG = {}

    def __init__(self, env_var_config=None):
        if env_var_config:
            self.DEFAULT_CONFIG.update(**env_var_config)

    def __getattr__(self, item):
        default_val = self.DEFAULT_CONFIG.get(item, None)
        val = os.environ.get(item, default_val)
        setattr(self, item, val)

        if val is None:
            raise AttributeError('Missing required environment variable %s' % item)

        return val


config = Config()
