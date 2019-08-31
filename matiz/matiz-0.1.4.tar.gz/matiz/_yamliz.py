# pylint: disable=no-member,bad-mcs-classmethod-argument

import dataclasses
import logging
from itertools import zip_longest

from . import _common, _contain, _exceptions, _fields

_logger = logging.getLogger(__name__)


class YamlizMeta(_contain.DataclassFieldMeta):

    def __new__(mcs, name, bases, attrs):
        """Purpose: ensure yaml_tag value."""
        tag = attrs.get('yaml_tag', None) or f"!iz/{name}"
        attrs['yaml_tag'] = f"!{tag.replace('!', '')}"
        return super(YamlizMeta, mcs).__new__(mcs, name, bases, attrs)

    def __init__(cls, name, bases, attrs):
        """Almost the same is done by yaml.YAMLObjectMetaclass"""
        if '__dataclass_params__' not in attrs:
            _logger.warning(f"Matiz class {name!r} must be a dataclass.")

        cls.yaml_loader.add_constructor(cls.yaml_tag, cls.from_yaml)
        cls.yaml_dumper.add_representer(cls, cls.to_yaml)
        super(YamlizMeta, cls).__init__(name, bases, attrs)


class Yamlizable(metaclass=YamlizMeta):
    # We reference yaml package by own module `_common` to make sure
    # that it is exactly the same `yaml` package
    # where yaml handler registration happen
    yaml_loader = _common.yaml.Loader
    yaml_dumper = _common.yaml.Dumper
    yaml_tag = None
    yaml_flow_style = None  # yaml_flow_style set to False disables auto-magical inline'ing

    @classmethod
    def to_yaml(cls, dumper, data):
        """Convert a Python object to a representation node."""
        return dumper.represent_yaml_object(cls.yaml_tag, data, cls, flow_style=cls.yaml_flow_style)

    @classmethod
    def from_yaml(cls, loader, node):
        """Convert a representation node to a Python object."""
        return loader.construct_yaml_object(node, cls)

    @classmethod
    def from_yaml_str(cls, yaml_string: str):
        return _common.load_y(yaml_string)

    def to_yaml_str(self) -> str:
        return _common.dump_y(self)


@dataclasses.dataclass
class ObsoleteAble(Yamlizable):
    # if `represent_as_mapping` is set, yaml uses a arbitrary_kwargs to represent the data
    # Values are bound by field name then, the dump requires keywords.
    # Document is more readable but weights more though.
    # Otherwise (false equivalent) - it uses a sequence. Values are bound by its order.
    represent_as_mapping = True

    @classmethod
    def unused_to_yaml(cls, dumper, py_node):
        if cls.represent_as_mapping:
            mapping = py_node.__dict__.copy()
            return dumper.represent_mapping(cls.yaml_tag, mapping, flow_style=cls.yaml_flow_style)
        else:
            sequence = [getattr(py_node, f.name) for f in cls.fields]
            return dumper.represent_sequence(cls.yaml_tag, sequence, flow_style=cls.yaml_flow_style)

    @classmethod
    def to_yaml(cls, dumper, py_node):
        def represent_yaml(node_):
            if isinstance(node_, ObsoleteAble):
                pass
            elif isinstance(node_, _fields.GeneralFieldObsolete):
                return node_.from_py_to_yaml(dumper, node_)
            else:
                return dumper.represent(node_)

        if isinstance(py_node, ObsoleteAble):
            values = dataclasses.astuple(py_node)
        else:
            values = py_node

        fields = dataclasses.fields(cls)
        if cls.represent_as_mapping:
            values = dataclasses.astuple(py_node)

            def g():
                for f, v in zip(fields, values):
                    yield f.name, f.from_py_to_yaml(dumper, v)

            return dumper.represent_mapping(cls.yaml_tag, dict(g()))

        else:
            values = dataclasses.astuple(py_node)

            def g():
                for f, v in zip_longest(fields, values):
                    yield f.from_py_to_yaml(dumper, v)

            return dumper.represent_sequence(cls.yaml_tag, list(g()))

    @classmethod
    def from_yaml(cls, loader, node):
        if cls.represent_as_mapping:
            values = loader.construct_mapping(node)
        else:
            values = loader.construct_sequence(node)
        g = (f.from_yaml_to_py(loader, v) for f, v in cls._fv(values))
        return cls(*g)

    @classmethod
    def _fv(cls, values):
        if cls.represent_as_mapping:
            for f in dataclasses.fields(cls):
                if f.name in values:
                    yield f, values[f.name]
                else:
                    raise _exceptions.UnYamlizable(f'The yaml node has not {f.name} value.')
        else:
            yield from zip_longest(dataclasses.fields(cls), values)
