import pytest

from typing import *
from uuid import UUID
from dataclasses import dataclass as stdlib_dataclass, field as stdlib_field, asdict, FrozenInstanceError
from rx import operators as rx
from rxdata import field, dataclass, typeguard
from pprint import pprint

def test_observed_single_field_internal():

    @dataclass
    class Data:
        value0: Union[int, None] = field(default=None,
                                         invoke=typeguard.ensure)
        derived: Union[str, None] = field(default=None,
                                          observe=value0,
                                          pipeline=rx.map(lambda v: f'stringified: {v}'),
                                          invoke=typeguard.ensure)


    data = Data(value0=33)
    assert data.derived == 'stringified: (33,)'
    data.value0= 1
    assert data.derived == 'stringified: (1,)'


def test_observed_multiple_fields():

    @dataclass
    class Data:
        value0: Union[int, None] = field(default=None, invoke=typeguard.ensure)
        value1: Union[int, None] = field(default=None, invoke=typeguard.ensure)
        derived: Union[str, None] = field(default=None,
                                          observe=(value0, value1),
                                          pipeline=rx.map(lambda v: f'stringified: {v}'),
                                          invoke=typeguard.ensure)


    data = Data(value0=33)
    assert data.derived == 'stringified: (33, None)'
    data.value0= 1
    assert data.derived == 'stringified: (1, None)'
    data.value1 = 2
    assert data.derived == 'stringified: (1, 2)'


def test_observed_multiple_fields_on_init():
    @dataclass
    class Data:
        value0: Union[int, None] = field(default=None,
                                        invoke=typeguard.ensure)
        value1: Union[int, None] = field(default=None,
                                        invoke=typeguard.ensure)
        derived: Union[str, None] = field(default=None,
                                          observe=(value0, value1),
                                          pipeline=rx.map(lambda v: f'stringified: {v}'),
                                          invoke=typeguard.ensure)


    data = Data(value0=33, value1=22)

    assert data.derived == 'stringified: (33, 22)'
    # print(RX.ASSIGNER.ITEM)

def test_observed_multiple_fields_on_init_of_frozen_cls():
    @dataclass(frozen=True)
    class Data:
        value0: Union[int, None] = field(default=None,
                                        invoke=typeguard.ensure)
        value1: Union[int, None] = field(default=None,
                                        invoke=typeguard.ensure)
        derived: Union[str, None] = field(default=None,
                                          observe=(value0, value1),
                                          pipeline=rx.map(lambda v: f'stringified: {v}'),
                                          invoke=typeguard.ensure)


    data = Data(value0=33, value1=22)

    assert data.derived == 'stringified: (33, 22)'

    with pytest.raises(FrozenInstanceError):
        data.value0 = 44
