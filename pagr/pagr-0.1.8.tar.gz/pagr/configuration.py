import os


class ConfigurationProvider:
    def __init__(self):
        self.config = dict()
        self.image_name = None
        self.metric_pod_metric_list = []

        self.load_from_env()

    def load_from_env(self):
        for key, value in os.environ.items():
            if key.startswith('PAGR_'):
                self.config[key[5:]] = value

    def __getitem__(self, item):
        return self.config[item]
