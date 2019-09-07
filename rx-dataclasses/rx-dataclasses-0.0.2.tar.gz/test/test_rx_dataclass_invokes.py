import pytest

from typing import *
from rx import operators as rx
from rxdata import field, dataclass, typeguard
from pprint import pprint


def test_invokes_single_typeguard():
    @dataclass
    class Data:
        v: Union[int, None] = field(default=None,
                                    invoke=typeguard.ensure)

    data = Data(v=12345)
    assert data.v == 12345
    data.v = None
    assert data.v is None
    data.v = 67891
    assert data.v is 67891
    with pytest.raises(TypeError):
        data.v = 1.0


def test_invokes_single_typeguard_with_overriden_type():
    @dataclass
    class Data:
        v: str = field(default=None,
                       invoke=typeguard.ensure(Union[int, None]))

    data = Data(v=12345)
    assert data.v == 12345
    data.v = None
    assert data.v is None
    data.v = 67891
    assert data.v is 67891
    with pytest.raises(TypeError):
        data.v = 1.0


def test_invokes_casting_with_typeguard():
    @dataclass
    class Data:
        v: Union[int, None] = field(default=None,
                                     invoke=(rx.map(lambda v: int(v) if v is not None else None),
                                             typeguard.ensure))

    data = Data(v='12345')
    assert data.v == 12345
    data.v = None
    assert data.v is None
    data.v = 67891
    assert data.v is 67891
    data.v = 1.0
    assert data.v == 1
    assert isinstance(data.v, int)

def test_invokes_casting_with_typeguard_overriden_type():
    @dataclass
    class Data:
        v: str = field(default=None,
                       invoke=(rx.map(lambda v: int(v) if v is not None else None),
                       typeguard.ensure(Union[int, None])))

    data = Data(v='12345')
    assert data.v == 12345
    data.v = None
    assert data.v is None
    data.v = 67891
    assert data.v is 67891
    data.v = 1.0
    assert data.v == 1
    assert isinstance(data.v, int)