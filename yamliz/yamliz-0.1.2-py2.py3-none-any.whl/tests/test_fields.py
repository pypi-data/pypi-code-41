import dataclasses
import itertools

import pytest

import yamliz
from yamliz import UnPythonizable, dump_y, fields, load_y
from .some_test_defs import Request


def test_dataclass_stuff():
    with pytest.raises(ValueError, match="cannot specify both default and default_factory"):
        fields.GeneralField(default="some", default_factory=str)


def test_forgot_to_():
    class ForgotToSpecify(fields.Scalar):
        pass

    msg = "Unable to create a python value because 'ForgotToSpecify' class does not define _py_constructor."
    with pytest.raises(UnPythonizable, match=msg):
        ForgotToSpecify.from_yaml_to_py(None, 'anything')

    forgot = ForgotToSpecify()
    assert ForgotToSpecify.from_py_to_yaml(None, forgot) == forgot


def test_integer_yaml_creation():
    assert fields.Integer.from_py_to_yaml(None, 345) == 345


def test_mac_address_conversion():
    some_mac = '12:ab:34:cd:56:ef'
    some_mac_other_format = '12-ab-34-cd-56-ef'
    assert fields.MacAddress.from_py_to_yaml(None, some_mac) == some_mac
    assert fields.MacAddress.from_yaml_to_py(None, some_mac_other_format) == some_mac
    assert fields.MacAddress.from_py_to_yaml(None, some_mac_other_format) == some_mac


INVALID_OBJECT_REPRS = list(zip(itertools.repeat(False), ['', ' ', None, 1234, {}, 3.14159]))


@pytest.mark.parametrize('method', ['to_py', 'to_yaml'])
@pytest.mark.parametrize('type_, successful, str_constructor', [
    (fields.IPv4, False, ''),
    (fields.IPv4, False, ' '),
    (fields.IPv4, False, None),
    (fields.IPv4, False, 1234),
    (fields.IPv4, False, {}),
    (fields.IPv4, False, 3.14159),
    (fields.IPv4, False, '12344'),
    (fields.IPv4, False, '12.13.14'),
    (fields.IPv4, False, '..12.13'),
    (fields.IPv4, False, '12.13.14 15'),
    (fields.IPv4, True, '12.13.14.15'),
    (fields.IPv4, True, '0.0.0.0'),
    (fields.MacAddress, False, ''),
    (fields.MacAddress, False, ' '),
    (fields.MacAddress, False, None),
    (fields.MacAddress, False, 1234),
    (fields.MacAddress, False, {}),
    (fields.MacAddress, False, 3.14159),
    (fields.MacAddress, False, 'aabbccddeef'),
    (fields.MacAddress, False, 'aabbccddeef'),
    (fields.MacAddress, False, 'a word'),
    (fields.MacAddress, False, 'aabbccddeeff'),
    (fields.MacAddress, False, 'aa bb cc dd ee ff'),
    (fields.MacAddress, False, 'aa:bb:cc:dd:ee ff'),
    (fields.MacAddress, True, 'aa:bb:cc:dd:ee:ff'),
])
def test_fail_to_decode_ipv4(method, type_, successful, str_constructor):
    if successful:
        assert type_.from_py_to_yaml(None, str_constructor) == str_constructor
        assert type_.from_yaml_to_py(None, str_constructor) == str_constructor
    else:
        msg = rf"Cannot create {type_.__name__} out of string: {str_constructor}\."
        with pytest.raises(yamliz.UnYamlizable, match=msg):
            if method == 'to_yaml':
                type_.from_py_to_yaml(None, str_constructor)
            else:
                type_.from_yaml_to_py(None, str_constructor)


def test_mac_address_object():
    req = Request(145, '12:34:56:67:78:9a', '78:9a:bc:12:31:03')

    assert req.id == 145
    assert req.mac1 == '12:34:56:67:78:9a'
    assert req.mac2 == '78:9a:bc:12:31:03'

    assert repr(req) == "Request(id=145, mac1='12:34:56:67:78:9a', mac2='78:9a:bc:12:31:03')"
    expected_yaml = """\
!iz/Request
id: 145
mac1: 12:34:56:67:78:9a
mac2: 78:9a:bc:12:31:03
"""
    assert dump_y(req) == expected_yaml
    assert str(req) == expected_yaml
    assert load_y(expected_yaml) == req


def test_bin_hexdump_conversion():
    raw_bytes = b"\xaf\x15\xEC\x17\x18"
    assert fields.BinaryHexdump.from_py_to_yaml(None, raw_bytes) == "af 15 ec 17 18"
    assert fields.BinaryHexdump.from_yaml_to_py(None, "af 15 ec 17 18") == raw_bytes
    assert fields.BinaryHexdump.from_yaml_to_py(None, "af15ec1718") == raw_bytes
    assert fields.BinaryHexdump.from_yaml_to_py(None, "af\n15 ec17 18") == raw_bytes


def test_bin_hexdump_object():
    @dataclasses.dataclass
    class S(yamliz.Able):
        yaml_tag = '!snippets'
        id: int = fields.Integer()
        snip_a: bytes = fields.BinaryHexdump()
        snip_bb: bytes = fields.BinaryHexdump()

    raw_bytes_a = b"\xa7\x18"
    raw_bytes_b = b"\x00\xda\x41\xa7\x18\xda\xed\xa1\xb5\xd7\x7f\x12\x8d\x19\xfa\x12\xc1" * 3
    obj = S(144, raw_bytes_a, raw_bytes_b)

    assert obj.snip_bb == raw_bytes_b

    expected_yaml = """\
!snippets
id: 144
snip_a: a7 18
snip_bb: 00 da 41 a7 18 da ed a1 b5 d7 7f 12 8d 19 fa 12 c1 00 da 41 a7 18 da ed a1
  b5 d7 7f 12 8d 19 fa 12 c1 00 da 41 a7 18 da ed a1 b5 d7 7f 12 8d 19 fa 12 c1
"""
    assert str(obj) == expected_yaml
    assert dump_y(obj) == expected_yaml
    assert load_y(expected_yaml) == obj


def test_ipv4_object():
    @dataclasses.dataclass
    class BindResponse(yamliz.Able):
        id: int = fields.StringField()
        source_address: str = fields.IPv4()
        src_port: int = fields.Integer()
        src_mac: str = fields.MacAddress()
        destination_address: str = fields.IPv4()
        destination_port: int = fields.Integer()
        destination_mac: str = fields.MacAddress()

    obj = BindResponse(2049, "145.12.64.241", 377, "fa:b5:36:29:21:7c", "70.64.24.1", 1235, "50:2b:e4:c8:12:22")

    expected_yaml = """\
!iz/BindResponse
destination_address: 70.64.24.1
destination_mac: 50:2b:e4:c8:12:22
destination_port: 1235
id: 2049
source_address: 145.12.64.241
src_mac: fa:b5:36:29:21:7c
src_port: 377
"""
    assert str(obj) == expected_yaml
    assert dump_y(obj) == expected_yaml
    assert load_y(expected_yaml) == obj


@dataclasses.dataclass
class Ints(yamliz.Able):
    id: int = fields.Integer()
    u8: int = fields.HexUInt8()
    u16: int = fields.HexUInt16()
    u32: int = fields.HexUInt32()


def test_integers():
    integers = Ints(3, 0x32, 0x3002, 0x30002006)
    expected_yaml = """\
!iz/Ints
id: 3
u16: '0x3002'
u32: '0x30002006'
u8: '0x32'
"""
    assert str(integers) == expected_yaml
    assert dump_y(integers) == expected_yaml
    assert load_y(expected_yaml) == integers

    integers.id = 311
    integers.u8 = 0x41
    integers.u16 = 0xffff
    integers.u32 = 0x123

    assert str(integers) == """\
!iz/Ints
id: 311
u16: '0xffff'
u32: '0x00000123'
u8: '0x41'
"""
