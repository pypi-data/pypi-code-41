
import yaml
from yaml.constructor import ScalarNode
from yaml.nodes import MappingNode

from gmconfig.configuration import Configuration
from gmconfig.utils import createLogger

try:
    from yaml import CLoader as Loader
except ImportError:
    from yaml import Loader


logger = createLogger('loader')


def load(path: str) -> dict:
    yaml.add_constructor(
        yaml.resolver.BaseResolver.DEFAULT_MAPPING_TAG,
        resolveImports,
        yaml.SafeLoader
    )
    logger.debug(path)

    with open(path, 'r') as handle:
        data = yaml.safe_load(handle)
        logger.debug(data)
    return Configuration(data)


def resolveImports(loader: yaml.SafeLoader, node: MappingNode, deep: bool = False):
    mappings = Configuration()

    for key_node, value_node in node.value:
        key = loader.construct_object(key_node, deep=deep)
        value = loader.construct_object(value_node, deep=deep)

        mappings[key] = value
        logger.debug("Key :: " + key)

        if key == "import":
            import_path = mappings.pop(key)
            mappings.update(load(import_path))
        elif key == "imports":
            import_paths = mappings.pop(key)
            for imp_path in import_paths:
                mappings.update(load(import_path))

    # return loader.construct_mapping(node, deep)
    return mappings

