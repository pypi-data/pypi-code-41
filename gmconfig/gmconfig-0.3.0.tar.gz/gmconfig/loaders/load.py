from gmconfig.configuration import Configuration
from gmconfig.utils import createLogger


logger = createLogger("gmconfig.loader")


def getLoaders() -> list:
    # loaders
    from gmconfig.loaders.load_yaml import loadYaml
    from gmconfig.loaders.load_toml import loadToml

    return [loadYaml, loadToml]


def loadFile(path: str) -> dict:
    """ Load configuration from path
    """
    logger.debug("Configuration file :: " + path)

    for loader in getLoaders():
        try:
            data = loader(path)
            logger.debug("Successfully parsed file using :: " + str(loader))
            return data
        except Exception as err:
            logger.debug("Parsing error :: " + str(err))

    raise Exception("Unknown configuration type")


def loadFiles(*paths) -> dict:
    return {}
