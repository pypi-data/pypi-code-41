import random

import yamliz
from yamliz import dump_y, load_y
from . import some_test_defs as sdf
from .some_test_defs import sample_data_structure_obj, sample_data_structure_yaml


def test_inheriting_yaml_tag():
    """Check if missing yaml_tag is automatically assigned."""

    class SomeClass(yamliz.Able):
        pass

    class TaggedClass(yamliz.Able):
        yaml_tag = 'custom_tag'

    class AnotherClass(SomeClass):
        pass

    class MissedTag(TaggedClass):
        pass

    class E(TaggedClass):
        yaml_tag = '!that_E'

    assert SomeClass.yaml_tag == "!iz/SomeClass"
    assert AnotherClass.yaml_tag == "!iz/AnotherClass"
    assert TaggedClass.yaml_tag == "!custom_tag"
    assert MissedTag.yaml_tag == "!iz/MissedTag"
    assert E.yaml_tag == "!that_E"


def test_creation_basic_object():
    one = sdf.TransitionTime(0.01234, 0.234)
    assert one.t_start == 0.01234
    assert one.t_stop == 0.234
    assert one == sdf.TransitionTime(0.01234, 0.234)
    assert repr(one) == "TransitionTime(t_start=0.01234, t_stop=0.234)"
    expectancies = """\
!iz/TransitionTime
t_start: 0.012340s
t_stop: 0.234000s
"""
    assert str(one) == expectancies


def generate_reprable_bytes(count):
    return ''.join(f"\\x{random.randint(0, 255):02x}" for _ in range(count))


def test_yamlization_dump_foo():
    result = dump_y(sample_data_structure_obj())
    assert result == sample_data_structure_yaml()
    reloaded = load_y(result)
    assert reloaded == sample_data_structure_obj()


def test_attributes_access():
    s = load_y(dump_y(sample_data_structure_obj()))
    assert s[0]['transitions'][0].t_start == 0.01
    assert s[0]['transitions'][0].t_stop == 0.234
    assert s[0]['transitions'][0].time_span() == 0.224

    s[0]['transitions'][0].t_start = 1000
    s[0]['transitions'][0].t_stop = 1065.5

    # attributes updated
    assert s[0]['transitions'][0].time_span() == 65.5

    assert s[0]['metadata'].ip_pot == '131.23.12.1'
    assert s[0]['metadata'].mac_address == '00:00:11:11:22:22'
    assert s[1]['metadata'].ip_pot == '131.24.48.1'
    assert s[1]['metadata'].mac_address == 'aa:bb:cc:dd:ee:ff'


def test_nesting():
    obj = sdf.Nested(
        "nesting",
        sdf.Point(0, 0, 0),
        sdf.Point(1, 1, 1),
    )
    assert obj.p_start.x == 0
    assert obj.p_start.y == 0
    assert obj.p_start.z == 0
    assert obj.p_stop.x == 1
