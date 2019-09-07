import pytest

from typing import *
from uuid import UUID
from dataclasses import dataclass as stdlib_dataclass, field as stdlib_field
from rx import operators as rx
from rxdata import field, dataclass, typeguard
from pprint import pprint

def test_assigners_overriden_to_specific_rx_functions():
    @dataclass
    class Data0:
        v0: Union[int, None] = field(default=None)

    @dataclass
    class Data1(Data0):
        v1: Union[int, None] = field(default=None)

    data0 = Data0()
    data1 = Data1()

    assert data0.__setattr__.__func__ is not data1.__setattr__.__func__

    assert data0.__delattr__.__func__ is not data1.__delattr__.__func__

def test_partial_dataclass_call_results_in_specific_rx_functions():
    rxdc = dataclass(repr=False)

    @rxdc
    class Data0:
        v: int = field(default=None)

    @rxdc
    class Data1:
        v: int = field(default=None)


    data0 = Data0()
    data1 = Data1()

    assert data0.__setattr__.__func__ is not data1.__setattr__.__func__
    assert data0.__delattr__.__func__ is not data1.__delattr__.__func__


def test_rxdataclass_call_reverts_original_field_assign_for_subcalls_to_stdlib_dataclass():
    @dataclass
    class Data0:
        def create_stdlib_dataclass():
            @stdlib_dataclass
            class Stdlib:
                y: int = stdlib_field(default=10)
            return Stdlib
        stdlib: Any = field(default_factory=create_stdlib_dataclass)

    data0 = Data0()

    assert data0.stdlib.__setattr__ == object.__setattr__

def test_partial_rxdataclass_call_reverts_original_field_assign_for_subcalls_to_stdlib_dataclass():
    rxdc = dataclass(repr=False)
    @rxdc
    class Data0:
        def create_stdlib_dataclass():
            @stdlib_dataclass
            class Stdlib:
                y: int = stdlib_field(default=10)
            return Stdlib
        stdlib: Any = field(default_factory=create_stdlib_dataclass)

    data0 = Data0()


    assert data0.stdlib.__setattr__ == object.__setattr__


def test_rxdataclass_reverts_to_original_field_assign_after_call():
    @dataclass
    class Data0:
        stdlib: Any = field(default=None)

    @stdlib_dataclass
    class Stdlib:
        y: int = stdlib_field(default=10)

    data0 = Data0()
    data1 = Stdlib()


    assert data1.__class__.__setattr__ == object.__setattr__

def test_partial_rxdataclass_reverts_to_original_field_assign_after_call():
    rxdc = dataclass(repr=False)
    @rxdc
    class Data0:
        stdlib: Any = field(default=None)

    @stdlib_dataclass
    class Stdlib:
        y: int = stdlib_field(default=10)

    data0 = Data0()
    data1 = Stdlib()


    assert data1.__class__.__setattr__ == object.__setattr__