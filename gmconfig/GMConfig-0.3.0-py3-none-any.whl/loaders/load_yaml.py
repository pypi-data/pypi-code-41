import yaml
from yaml.nodes import MappingNode
from yaml.parser import ParserError as YamlParserError

from gmconfig.configuration import Configuration
from gmconfig.utils import createLogger
from gmconfig.loaders.load import loadFile

try:
    from yaml import CLoader as Loader
except ImportError:
    from yaml import Loader  # type: ignore

logger = createLogger("gmconfig.loader.yaml")


def loadYaml(path: str):
    """ Helper function that helps loads YAML based configuration files
    """
    yaml.add_constructor(
        yaml.resolver.BaseResolver.DEFAULT_MAPPING_TAG, resolveImports, yaml.SafeLoader
    )

    with open(path, "r") as handle:
        data = yaml.safe_load(handle)
    return Configuration(data)


def resolveImports(loader: yaml.SafeLoader, node: MappingNode, deep: bool = True):
    mappings = Configuration()

    for key_node, value_node in node.value:
        key = loader.construct_object(key_node, deep=deep)
        value = loader.construct_object(value_node, deep=deep)

        mappings[key] = value
        logger.debug("Key :: " + key)

        if key == "import":
            import_path = mappings.pop(key)

            if isinstance(import_path, str):
                logger.debug("Import path :: " + import_path)
                # light merge the two dicts
                mappings.merge(loadFile(import_path))
                # mappings = liteMerge(mappings, load(import_path))

            elif isinstance(import_path, list):
                logger.debug("Import paths :: " + str(import_path))
                for imp_path in import_path:
                    # light merge the two dicts
                    mappings.merge(loadFile(imp_path))
                    # mappings = liteMerge(mappings, load(imp_path))

    # return loader.construct_mapping(node, deep)
    return mappings
