# pylint: disable=not-callable

import abc
import binascii
import dataclasses
import re
from functools import partial

from ._exceptions import UnPythonizable, UnYamlizable

MISSING = dataclasses.MISSING


class GeneralField(dataclasses.Field):
    _py_default = MISSING
    _py_default_constructor = MISSING

    def __init__(self, *, default=MISSING, default_factory=MISSING, init=True, repr_=True, hash_=None, compare=True,
                 metadata=None):
        default = default if default is not MISSING else self._py_default
        default_factory = default_factory if default_factory is not MISSING else self._py_default_constructor

        if default is not MISSING and default_factory is not MISSING:
            raise ValueError('cannot specify both default and default_factory')
        super().__init__(default, default_factory, init, repr_, hash_, compare, metadata)

    @classmethod
    @abc.abstractmethod
    def from_py_to_yaml(cls, dumper, py_node_object):
        pass

    @classmethod
    @abc.abstractmethod
    def from_yaml_to_py(cls, loader, yaml_node):
        pass


class Scalar(GeneralField):
    _yaml_encode_pattern = None
    _yaml_decode_pattern = None
    _py_default_factory = None

    @classmethod
    def from_yaml_to_py(cls, loader, yaml_node):
        if not cls._py_default_factory:
            raise UnPythonizable(f"Unable to create a python value because {cls.__name__!r} "
                                 f"class does not define _py_default_factory.")

        if isinstance(yaml_node, str):
            if cls._yaml_decode_pattern is not None:
                matches = re.match(cls._yaml_decode_pattern, yaml_node)
                if matches:
                    return cls._py_default_factory(matches.group(1))
            else:
                return cls._py_default_factory(yaml_node.strip())
        else:
            return cls._py_default_factory(yaml_node)

        raise UnPythonizable(f"Given yaml node: {yaml_node!r} does not fit to pattern "
                             f"{cls._yaml_decode_pattern} defined by {cls.__name__!r} class.")

    @classmethod
    def from_py_to_yaml(cls, dumper, py_node_object):
        if cls._yaml_encode_pattern is None:
            # use native 'yaml' dumper
            return py_node_object
        return cls._yaml_encode_pattern.format(node=py_node_object)


class Integer(Scalar):
    _yaml_decode_pattern = r'([\-\+]?\d+)'
    _py_default_factory = int


class _HexUInt(Scalar):
    _yaml_decode_pattern = r'(?:0x|)([0-9a-fA-F]+)'
    _py_default_factory = partial(int, base=16)


class HexUInt8(_HexUInt):
    _yaml_encode_pattern = '0x{node:02x}'


class HexUInt16(_HexUInt):
    _yaml_encode_pattern = '0x{node:04x}'


class HexUInt32(_HexUInt):
    _yaml_encode_pattern = '0x{node:08x}'


class HexUInt64(_HexUInt):
    _yaml_encode_pattern = '0x{node:016x}'


class _FloatDecimal(Scalar):
    _yaml_encode_pattern = '{node:.f}'
    _yaml_decode_pattern = r'([\+\-]?\d+\.?\d+)'
    _py_default_factory = float


class FloatSeconds(_FloatDecimal):
    _yaml_encode_pattern = '{node:0.6f}s'
    _yaml_decode_pattern = _FloatDecimal._yaml_decode_pattern + r'(:?\s?s|)?'


class StringField(GeneralField):

    @classmethod
    def normalize_value(cls, string_value):
        return string_value

    @classmethod
    def from_yaml_to_py(cls, loader, yaml_node):
        return cls.normalize_value(yaml_node)

    @classmethod
    def from_py_to_yaml(cls, dumper, py_node_object):
        return cls.normalize_value(py_node_object)


class MacAddress(StringField):
    _normalization_pattern = (r'(MAC:\s*)?' + r'([0-9a-fA-F]{2})[\:\-]' * 5 + r'([0-9a-fA-F]{2})')

    @classmethod
    def normalize_value(cls, string_value):
        matches = re.match(cls._normalization_pattern, str(string_value), re.I)
        if matches:
            assert len(matches.groups()) == 7, "bad mac address format"
            return ":".join(matches.groups()[1:])
        raise UnYamlizable(f"Cannot create MAC addres out of {string_value}.")


class IPv4(StringField):
    _normalization_pattern = r'\b((?:\d{1,3}\.){3}\d{1,3})\b'

    @classmethod
    def normalize_value(cls, string_value):
        matches = re.match(cls._normalization_pattern, str(string_value))
        if matches:
            return matches.group(0)
        raise UnYamlizable(f"Cannot create {cls.__name__!r} address out of {string_value!r}.")


class BinaryHexdump(GeneralField):
    bytes_in_group = 1
    _py_default = b''

    @classmethod
    def from_py_to_yaml(cls, dumper, py_node_object):
        assert isinstance(py_node_object, bytes), f"Bad type: {type(py_node_object)}"

        def g():
            for i, b in enumerate(py_node_object):
                if cls.bytes_in_group and i and not i % cls.bytes_in_group:
                    yield ' '
                yield '{:02x}'.format(b)

        return ''.join(g())

    @classmethod
    def from_yaml_to_py(cls, loader, yaml_node):
        yaml_node = re.sub(r"[\s\n]", "", yaml_node)
        return binascii.unhexlify(yaml_node)
