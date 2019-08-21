# pylint: disable=no-member,bad-mcs-classmethod-argument

import dataclasses
from itertools import zip_longest

from . import _exceptions
from ._common import dump_y, load_y, yaml


class _RegisteringMeta(type):

    def __new__(mcs, name, bases, attrs):
        tag = attrs.get('yaml_tag', None) or f"!iz/{name}"
        attrs['yaml_tag'] = f"!{tag.replace('!', '')}"
        return super().__new__(mcs, name, bases, attrs)

    def __init__(cls, name, bases, attrs):
        yaml.add_representer(cls, cls.to_yaml)
        yaml.add_constructor(cls.yaml_tag, cls.from_yaml)
        super(_RegisteringMeta, cls).__init__(name, bases, attrs)


@dataclasses.dataclass
class Able(metaclass=_RegisteringMeta):
    # if yaml_tag is not set, class name is used instead
    yaml_tag = None

    # if _yaml_as_mapping is set, yaml uses a dictionary
    # to represent the data, list otherwise
    _yaml_as_mapping = True

    @classmethod
    def to_yaml(cls, dumper, node):
        fields = dataclasses.fields(cls)
        values = dataclasses.astuple(node)
        if cls._yaml_as_mapping:
            values = {f.name: v for f, v in zip(fields, values)}
            nodes = {f.name: f.from_py_to_yaml(dumper, v) for f, v in cls._fv(values)}
            return dumper.represent_mapping(cls.yaml_tag, nodes)
        else:
            nodes = [f.from_py_to_yaml(dumper, v) for f, v in cls._fv(values)]
            return dumper.represent_sequence(cls.yaml_tag, nodes)

    @classmethod
    def from_yaml_str(cls, yaml_string):
        return load_y(yaml_string)

    @classmethod
    def from_yaml(cls, loader, node):
        if cls._yaml_as_mapping:
            values = loader.construct_mapping(node)
        else:
            values = loader.construct_sequence(node)
        g = (f.from_yaml_to_py(loader, v) for f, v in cls._fv(values))
        return cls(*g)

    @classmethod
    def _fv(cls, values):
        if cls._yaml_as_mapping:
            for f in dataclasses.fields(cls):
                if f.name in values:
                    yield f, values[f.name]
                else:
                    raise _exceptions.UnYamlizable('The yaml node has not {f.name} value.')
        else:
            yield from zip_longest(dataclasses.fields(cls), values)

    def __str__(self):
        return dump_y(self)
