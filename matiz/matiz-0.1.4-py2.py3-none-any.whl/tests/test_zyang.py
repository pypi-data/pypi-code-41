import dataclasses
import typing

import pytest

import matiz as iz


@dataclasses.dataclass
class T1(iz.Able):
    a_required: int = iz.fields.TInt32()
    b_has_default: int = iz.fields.TInt16(default=1222)
    c_has_minimum: int = iz.fields.TUInt16(default=1333, minimum=12)


@dataclasses.dataclass
class T2(iz.Able):
    index: int = iz.fields.TInt32(minimum=30)
    info: str = iz.fields.TString(min_len=30)
    one: T1 = iz.fields.TObject(T1)
    two: T1 = iz.fields.TObject(T1)


def test_creation():
    object_a = T1(a_required=12, b_has_default=1222, c_has_minimum=1333)
    object_b = T1(a_required=12, b_has_default=1222, c_has_minimum=1333)
    assert object_a == object_b

    t2 = T2(
        731,
        'That descritption',
        object_a,
        T1(a_required=-3, b_has_default=-2, c_has_minimum=-1),
    )
    assert t2.one.c_has_minimum == 1333
    assert t2.two.c_has_minimum == -1
    assert [str(v) for v in t2.violations()] == ['T2.info | Value: 17 exceeds minimum: 30.']

    assert iz.dump_y(t2) == """\
!iz/T2
index: 731
info: That descritption
one: !iz/T1
  a_required: 12
  b_has_default: 1222
  c_has_minimum: 1333
two: !iz/T1
  a_required: -3
  b_has_default: -2
  c_has_minimum: -1
"""


def test_create_from_arbitrary_dict():
    proper = T1(a_required=300, b_has_default=1222, c_has_minimum=400)
    arbitrary = T1.from_dict(dict(one=1, two=2, three=3, a_required=300, c_has_minimum=400))

    assert arbitrary == proper  # note that some fields are not being compared

    assert not hasattr(proper, 'aux_call_kwargs')
    assert hasattr(arbitrary, 'aux_call_kwargs')
    assert arbitrary.aux_call_kwargs == {'one': 1, 'three': 3, 'two': 2}

    assert arbitrary.a_required == 300
    assert arbitrary.b_has_default == 1222
    assert arbitrary.c_has_minimum == 400

    assert proper.a_required == 300
    assert proper.b_has_default == 1222
    assert proper.c_has_minimum == 400


@dataclasses.dataclass
class IndexableType(iz.Able):
    a_index: int = iz.fields.TInt8(-2, 8)


@dataclasses.dataclass
class TypeWithInts(IndexableType):
    b_ok: int = iz.fields.TInt8(-2, 8)
    c_none_init: int = iz.fields.TInt8(-2, 8)
    d_not_given: int = iz.fields.TInt8(default=34)
    e_info: str = iz.fields.TString(3, 7, default=7013)


class TestNewPOC:

    @pytest.fixture
    def thing_instance(self):
        """Happy scenario object case."""
        return TypeWithInts(
            a_index=-100,
            b_ok=5,
            c_none_init=None,  # noqa
            e_info="will have to test it by parametrization",
        )

    def test_does_not_require_all_args(self):
        t = TypeWithInts(1, 2, 3, 4)
        assert t == TypeWithInts(a_index=1, b_ok=2, c_none_init=3, d_not_given=4, e_info=7013)

    def test_validation(self, thing_instance):
        assert not thing_instance.is_valid()
        assert [str(v) for v in thing_instance.violations()] == [
            'TypeWithInts.a_index | Value: -100 exceeds minimum: -2.',
            'TypeWithInts.c_none_init | Value cannot be None.',
            'TypeWithInts.e_info | Value: 39 exceeds maximum: 7.',
        ]

    def test_yaml_dumping(self, thing_instance):
        assert iz.dump_y(thing_instance) == """\
            !iz/TypeWithInts
            a_index: -100
            b_ok: 5
            c_none_init: null
            d_not_given: 34
            e_info: will have to test it by parametrization
            """.replace(' ' * 4, '')


@dataclasses.dataclass
class l2tpv3CtrlInstance(iz.Able):
    """There could be multiple control instances, each of them is mapping to a tunnel instance."""
    keys_ = ["ctrlName"]
    ctrlName: str = iz.fields.TString()
    hostName: str = iz.fields.TString(1, 19)
    routerID: int = iz.fields.TInt8(0, 2 ** 16 - 1)
    rcvWinSize: int = iz.fields.TInt8(0, 2 ** 16 - 1)
    another: typing.List[int] = iz.fields.TInt8()
    # TString(valid_len=(1, 19), description="The name of the control instance.")
    # hostName: str = TString(mandatory=True, description="The name of the host.")
    #
    # routerID: int = Integer(c_type_name="uint16", mandatory=True, description="Router ID.")
    # rcvWinSize = Integer(c_type_name="uint16", description="Receiving window size.")
    # helloInterval = Integer(c_type_name="uint16", description="Hello interval time.")


def ntest_l2tpv3CtrlInstance():
    l2 = l2tpv3CtrlInstance(
        'controler name',
        'host name',
        3412,
        12314,
        another=[("one", 3), ("twos", 1231.3)],
    )

    assert l2 == l2tpv3CtrlInstance(
        ctrlName='controler name',
        hostName='host name',
        routerID=3412,
        rcvWinSize=12314,
        another=[("one", 3), ("twos", 1231.3)],
    )

    assert iz.dump_y(l2) == """\
!iz/l2tpv3CtrlInstance
another:
- !iz/Lighter
  l_amount: 3
  l_name: one
- !iz/Lighter
  l_amount: 1231.3
  l_name: twos
ctrlName: controler name
hostName: host name
rcvWinSize: 12314
routerID: 3412
"""


@dataclasses.dataclass
class TWListScalars(iz.Able):
    info: str = iz.fields.TString(min_len=30)
    scalars: list = iz.fields.TList(iz.fields.TInt8(45, 49))


class TestListUsage:

    def test_creation_no_items(self):
        t = TWListScalars(info="does it work?", scalars=[])

        assert repr(t) == "TWListScalars(info='does it work?', scalars=[])"
        assert str(t) == repr(t)
        assert iz.dump_y(t) == """\
!iz/TWListScalars
info: does it work?
scalars: []
"""
        assert list(t.violations()) == [
            iz.Violation(path_='TWListScalars.info', message='Value: 13 exceeds minimum: 30.'),
        ]

    def test_creation_with_some_list(self):
        t = TWListScalars("does it work?", [12, 23, 34, 45, 56])

        assert repr(t) == "TWListScalars(info='does it work?', scalars=[12, 23, 34, 45, 56])"
        assert str(t) == "TWListScalars(info='does it work?', scalars=[12, 23, 34, 45, 56])"
        assert iz.dump_y(t) == """\
!iz/TWListScalars
info: does it work?
scalars:
- 12
- 23
- 34
- 45
- 56
"""
        assert list(t.violations()) == [
            iz.Violation(path_='TWListScalars.info', message='Value: 13 exceeds minimum: 30.'),
            iz.Violation(path_='TWListScalars.scalars[0]', message='Value: 12 exceeds minimum: 45.'),
            iz.Violation(path_='TWListScalars.scalars[1]', message='Value: 23 exceeds minimum: 45.'),
            iz.Violation(path_='TWListScalars.scalars[2]', message='Value: 34 exceeds minimum: 45.'),
            iz.Violation(path_='TWListScalars.scalars[4]', message='Value: 56 exceeds maximum: 49.'),
        ]
