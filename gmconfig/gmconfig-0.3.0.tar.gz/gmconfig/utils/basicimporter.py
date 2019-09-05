from gmconfig.configuration import Configuration
from gmconfig.loaders.load import loadFile
from gmconfig.utils.litemerge import liteMerge


def basicImporter(obj: dict) -> dict:
    """ This is a slow but effective way of importing content
    """
    return _import(obj)


def _import(obj: dict) -> dict:

    new_obj = Configuration()
    import_value = None

    for key, value in obj.items():
        new_obj[key] = value

        if key == "import":
            import_value = value
            new_obj.pop(key)
        if isinstance(value, dict):
            new_obj[key] = _import(value)

    if import_value is not None:
        if isinstance(import_value, str):
            new_obj.merge(loadFile(import_value))

        elif isinstance(import_value, list):
            for imp_path in import_value:
                new_obj.merge(loadFile(imp_path))

    return new_obj
