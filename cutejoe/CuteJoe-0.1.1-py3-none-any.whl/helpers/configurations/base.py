import os


class Singleton(type):
    _instances = {}

    def __call__(cls, *args, **kwargs):
        if cls not in cls._instances:
            cls._instances[cls] = super().__call__(*args, **kwargs)

        return cls._instances[cls]


class BaseConfigFactory(metaclass=Singleton):

    def __init__(self):
        self._configs = {}

    def register(self, version, config):
        self._configs[version] = config

    def create(self, version, **kwargs):
        Config = self._configs.get(version)

        if not Config:
            raise ValueError(version)  # TODO

        return Config(**kwargs)


class ChangelogConfigFactory(BaseConfigFactory):
    pass


class Config:

    def __init__(self, **kwargs):
        self.version = kwargs.get("version", 1)
        self.changelog = kwargs.get("changelog", {})

    @property
    def changelog(self):
        return self._changelog

    @changelog.setter
    def changelog(self, changelog):
        self._changelog = ChangelogConfigFactory().create(self.version, **changelog)

    @staticmethod
    def get_default_file_path() -> str:
        # TODO Change to settings file
        # Default are keepachangelog labels with semver versioning
        default_path = os.path.dirname(__file__)
        default_path = os.path.abspath(default_path)
        default_file = os.path.join(default_path, ".default_config.yml")

        return default_file


class BaseChangelogConfig:

    def get_title(self, kind=None):
        raise NotImplementedError

    def get_version(self, kind=None):
        raise NotImplementedError

    def get_kind(self, label=None):
        raise NotImplementedError
