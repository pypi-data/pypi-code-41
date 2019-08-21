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
        """pass"""

    @classmethod
    @abc.abstractmethod
    def from_yaml_to_py(cls, loader, yaml_node):
        """pass"""


def nest(type_):
    # not working yet
    class Wrap(GeneralField):

        def __init__(self, *, init=True, repr_=True, hash_=None, compare=True, metadata=None):
            super().__init__(init=init, repr_=repr_, hash_=hash_, compare=compare, metadata=metadata)

        @classmethod
        def from_py_to_yaml(cls, dumper, py_node_object):
            return type_.to_yaml(dumper, py_node_object)

        @classmethod
        def from_yaml_to_py(cls, loader, yaml_node):
            """pass"""

    return Wrap()


class Scalar(GeneralField):
    _yaml_encode_pattern = None
    _yaml_decode_pattern = None
    _py_constructor = None

    @classmethod
    def from_yaml_to_py(cls, loader, yaml_node):
        if not cls._py_constructor:
            raise UnPythonizable(f"Unable to create a python value because {cls.__name__!r} "
                                 f"class does not define _py_constructor.")

        if isinstance(yaml_node, str):
            if cls._yaml_decode_pattern is not None:
                matches = re.match(cls._yaml_decode_pattern, yaml_node)
                if matches:
                    return cls._py_constructor(matches.group(1))
            else:
                return cls._py_constructor(yaml_node.strip())
        else:
            return cls._py_constructor(yaml_node)

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
    _py_constructor = int


class _HexUInt(Scalar):
    _yaml_decode_pattern = r'(?:0x|)([0-9a-fA-F]+)'
    _py_constructor = partial(int, base=16)


class HexUInt8(_HexUInt):
    _yaml_encode_pattern = '0x{node:02x}'


class HexUInt16(_HexUInt):
    _yaml_encode_pattern = '0x{node:04x}'


class HexUInt32(_HexUInt):
    _yaml_encode_pattern = '0x{node:08x}'


class HexUInt64(_HexUInt):
    _yaml_encode_pattern = '0x{node:016x}'


GENERAL_FLOAT_RE_PATTERN = r'([\+\-]?\d+\.?\d+)'


class _FloatDecimal(Scalar):
    _yaml_encode_pattern = '{node:.f}'
    _yaml_decode_pattern = GENERAL_FLOAT_RE_PATTERN
    _py_constructor = float


class Float(_FloatDecimal):
    unit_suffix = ''
    _yaml_encode_pattern = f'{{node:0.6f}}{unit_suffix}'
    _yaml_decode_pattern = GENERAL_FLOAT_RE_PATTERN + rf'(:?\s?{unit_suffix}|)?'


class FloatSeconds(Float):
    unit_suffix = 's'
    _yaml_encode_pattern = f'{{node:0.6f}}{unit_suffix}'
    _yaml_decode_pattern = GENERAL_FLOAT_RE_PATTERN + rf'(:?\s?{unit_suffix}|)?'


class FloatMeters(Float):
    unit_suffix = ' m'
    _yaml_encode_pattern = f'{{node:0.8g}}{unit_suffix}'
    _yaml_decode_pattern = GENERAL_FLOAT_RE_PATTERN + rf'(:?\s*{unit_suffix}|)?'


class StringField(GeneralField):
    _normalization_pattern = None

    @classmethod
    @abc.abstractmethod
    def normalize_value(cls, re_matches):
        """to be overridden if regex normalization/validation is needed"""

    @classmethod
    def catch_normalizing(cls, _, string_value):
        """
        it's bidirectional 'normalization'
        it's assumed that such kind of type is stored in same form in each codec
        """
        if cls._normalization_pattern is None:
            return string_value

        matches = re.match(cls._normalization_pattern, str(string_value), re.I)
        if matches:
            return cls.normalize_value(matches)
        raise UnYamlizable(f"Cannot create {cls.__name__} out of string: {string_value}.\n"
                           f"The regex pattern does not match: {cls._normalization_pattern}.")

    from_yaml_to_py = from_py_to_yaml = catch_normalizing


class MacAddress(StringField):
    _normalization_pattern = (r'(MAC:\s*)?' + r'([0-9a-fA-F]{2})[\:\-]' * 5 + r'([0-9a-fA-F]{2})')

    @classmethod
    def normalize_value(cls, re_matches):
        assert len(re_matches.groups()) == 7, "bad mac address format or its regex pattern"
        return ":".join(re_matches.groups()[1:])


class IPv4(StringField):
    _normalization_pattern = r'\b((?:\d{1,3}\.){3}\d{1,3})\b'

    @classmethod
    def normalize_value(cls, re_matches):
        return re_matches.group(0)


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
