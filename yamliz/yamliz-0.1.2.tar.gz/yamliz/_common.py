import yaml


def log(message):
    """Dummy logger, meets mvp."""
    print(message)


def load_y(yaml_string):
    return yaml.load(yaml_string, Loader=yaml.Loader)


def dump_y(object_):
    return yaml.dump(object_, Dumper=yaml.Dumper)
