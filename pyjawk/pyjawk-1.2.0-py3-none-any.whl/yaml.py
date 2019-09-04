import sys

from .attrdict import AttrDict
from collections.abc import Mapping

from ruamel import yaml
from ruamel.yaml.comments import CommentedMap
from ruamel.yaml.dumper import RoundTripDumper
from ruamel.yaml.loader import RoundTripLoader

def dump_patch(data):
    if isinstance(data, AttrDict):
        return CommentedMap((dump_patch(key), dump_patch(value)) for key, value in data.items())

    elif isinstance(data, list):
        return [dump_patch(item) for item in data]
    else:
        return data

def load_patch(data):
    if isinstance(data, Mapping):
        return AttrDict((load_patch(key), load_patch(value)) for key, value in data.items())

    elif isinstance(data, list):
        return [load_patch(item) for item in data]
    else:
        return data

def load(*args, **kwargs):
    return load_patch(yaml.load(*args, **kwargs, Loader=RoundTripLoader))

def dump(data, *args, **kwargs):
    return yaml.dump(dump_patch(data), *args, **kwargs, Dumper=RoundTripDumper)
