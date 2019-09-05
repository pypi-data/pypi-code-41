from toml import load as tomlLoad

from gmconfig.configuration import Configuration
from gmconfig.utils import createLogger
from gmconfig.utils.basicimporter import basicImporter


logger = createLogger("gmconfig.loader.toml")


def loadToml(path: str):
    with open(path, "r") as handle:
        data = basicImporter(tomlLoad(handle))
    return Configuration(data)
