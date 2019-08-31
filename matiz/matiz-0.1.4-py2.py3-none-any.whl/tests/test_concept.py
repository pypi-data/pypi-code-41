import abc
import dataclasses

import yaml

from matiz import dump_y, load_y


class _AbleMeta(type):

    def __new__(mcs, name, bases, attrs):
        tag = attrs.get('yaml_tag', None) or f"!iz/{name}"
        attrs['yaml_tag'] = f"!{tag.replace('!', '')}"
        return super().__new__(mcs, name, bases, attrs)

    def __init__(cls, name, bases, attrs):
        if '__dataclass_params__' not in attrs:
            """decorating becomes optional"""
            dataclasses.dataclass(cls)
        """Almost the same is done by yaml.YAMLObjectMetaclass"""
        cls.yaml_loader.add_constructor(cls.yaml_tag, cls.from_yaml)
        cls.yaml_dumper.add_representer(cls, cls.to_yaml)
        super(_AbleMeta, cls).__init__(name, bases, attrs)


class AbleBase(metaclass=_AbleMeta):
    yaml_loader = yaml.Loader
    yaml_dumper = yaml.Dumper
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
    def from_py_to_yaml(cls, dumper, py_node_object):
        """pass"""

    @classmethod
    @abc.abstractmethod
    def from_yaml_to_py(cls, loader, yaml_node):
        """pass"""


@dataclasses.dataclass
class Pstryk(AbleBase):
    value: int = 12


@dataclasses.dataclass
class Dupa(AbleBase):
    one: int
    two: str
    p: Pstryk


@dataclasses.dataclass
class DupaBlada(AbleBase):
    three: Dupa
    four: Dupa
    five: list


def test_dupa():
    d = Dupa(12, "napis", Pstryk(522))

    assert dump_y(d) == """\
!iz/Dupa
one: 12
p: !iz/Pstryk
  value: 522
two: napis
"""


def test_dupa_blada():
    db = DupaBlada(
        three=Dupa(12, "czarna", Pstryk(123)),
        four=Dupa(24, "blada", Pstryk(124)),
        five=[3.14159265359] * 10,
    )

    assert db.three.one == 12
    assert db.four.two == "blada"

    obj = ["swietny string", dict(raz=db, dwa=Dupa(0, "", Pstryk(1e10))), 144]
    expected_string = """\
- swietny string
- dwa: !iz/Dupa
    one: 0
    p: !iz/Pstryk
      value: 10000000000.0
    two: ''
  raz: !iz/DupaBlada
    five:
    - 3.14159265359
    - 3.14159265359
    - 3.14159265359
    - 3.14159265359
    - 3.14159265359
    - 3.14159265359
    - 3.14159265359
    - 3.14159265359
    - 3.14159265359
    - 3.14159265359
    four: !iz/Dupa
      one: 24
      p: !iz/Pstryk
        value: 124
      two: blada
    three: !iz/Dupa
      one: 12
      p: !iz/Pstryk
        value: 123
      two: czarna
- 144
"""
    assert dump_y(obj) == expected_string

    assert load_y(expected_string) == obj
