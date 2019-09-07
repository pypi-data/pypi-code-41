import pytest

from typing import *
from uuid import UUID
from dataclasses import dataclass as stdlib_dataclass, field as stdlib_field, asdict, FrozenInstanceError
from rx import operators as rx
from rxdata import field, rxsubject, dataclass, typeguard
from pprint import pprint

def test_class_observed_single_field_of_external_dataobject_():
    @dataclass
    class Parent:
        value0: Union[int, None] = field(default=None, invoke=typeguard.ensure)
        derived: Union[str, None] = field(default=None,
                                          observe=value0,
                                          pipeline=rx.map(lambda v: f'stringified: {v}'),
                                          invoke=typeguard.ensure)
    parent = Parent(value0=123)

    @dataclass
    class Child:
        derived: Union[str, None] = field(default=None,
                                          observe=rxsubject(Parent, 'derived')(parent),
                                          pipeline=rx.map(lambda v: f'child stringified: {v}'),
                                          invoke=typeguard.ensure)

        x: Union[str, None] = field(default=None, invoke=typeguard.ensure)
        y: Union[int, None] = field(default=0,
                                    observe=x,
                                    pipeline=rx.map(lambda v: v[0]), invoke=[rx.map(int), typeguard.ensure])


    child = Child(x='2')
    assert asdict(child) == {'derived': "child stringified: ('stringified: (123,)',)", 'x': '2', 'y': 2}

    child.x = '3'
    assert asdict(child) == {'derived': "child stringified: ('stringified: (123,)',)", 'x': '3', 'y': 3}

    parent.value0 = 321
    assert asdict(child) == {'derived': "child stringified: ('stringified: (321,)',)", 'x': '3', 'y': 3}


def test_object_observed_single_field_of_external_dataobject():

    @dataclass
    class Parent:
        value0: Union[int] = field(default=0, invoke=typeguard.ensure)
        derived: Union[str] = field(default='parentnull',
                                    observe=value0,
                                    pipeline=rx.map(lambda v: f'stringified: {v}'),
                                    invoke=typeguard.ensure
                                    )
    @dataclass
    class Child:
        x: Union[str]       = field(default='2',
                                    invoke=typeguard.ensure)
        y: Union[int]       = field(default=3,
                                    observe=x,
                                    pipeline=rx.map(lambda v: v[0]),
                                    invoke=[rx.map(int),
                                            typeguard.ensure]
                                    )

        derived: Union[str] = field(default='childnull',
                                    pipeline=rx.map(lambda v: f'child stringified: {v}'),
                                    invoke=typeguard.ensure
                                    )


    parent = Parent()
    child = Child(x='1')

    assert asdict(child) == {'derived': 'childnull', 'x': '1', 'y': 1}

    rxsubject(Child, 'derived')(child).observes(rxsubject(Parent, 'derived')(parent))
    parent.value0 = 321
    assert asdict(child) == {'derived': "child stringified: ('stringified: (321,)',)", 'x': '1', 'y': 1}

    child.x = '4'
    assert asdict(child) == {'derived': "child stringified: ('stringified: (321,)',)", 'x': '4', 'y': 4}
