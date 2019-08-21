import dataclasses

import yamliz
from yamliz import fields


@dataclasses.dataclass
class TransitionTime(yamliz.Able):
    t_start: float = fields.FloatSeconds()
    t_stop: float = fields.FloatSeconds()

    def time_span(self):
        return self.t_stop - self.t_start


@dataclasses.dataclass
class Point(yamliz.Able):
    _yaml_as_mapping = False

    x: float = fields.FloatMeters()
    y: float = fields.FloatMeters()
    z: float = fields.FloatMeters()


@dataclasses.dataclass
class Nested(yamliz.Able):
    nest_name: str = fields.StringField()
    p_start: Point = yamliz.nest(Point)
    p_stop: Point = yamliz.nest(Point)


@dataclasses.dataclass
class SomeMeta(yamliz.Able):
    event_time: float = fields.FloatSeconds()
    ip_pot: str = fields.IPv4()
    mac_address: str = fields.MacAddress()
    metadata: bytes = fields.BinaryHexdump()


@dataclasses.dataclass
class Request(yamliz.Able):
    id: int = fields.Integer()
    mac1: str = fields.MacAddress()
    mac2: str = fields.MacAddress()


def sample_data_structure_obj():
    """No need to copy.deepcopy() the test data, since it's recreated by this function at each time."""
    return [
        {
            'transitions': [
                TransitionTime(0.01, 0.234),
                TransitionTime(0.01234, 3.141591),
            ],
            'metadata': SomeMeta(
                event_time=12,
                ip_pot="131.23.12.1",
                mac_address="00:00:11:11:22:22",
                metadata=b"\xc9\x0d\xf2\xa9\x66\x6a\xb7\xbf\x6a\xd4\x3d\x87\xa1\xb1\x67\x49"
                         b"\x08\x4f\x1e\xcc\xfb\xc7\xad\x3e\xee\xc9\x27\xc7\xbf\x9c\x0c\x07"
                         b"\x6d\x6f\x08\x0d\xf7\x22\x9b\xfa\xf6\x69\x26\x1a\x1b\x64\x93\xaf"
                         b"\x98\xe0\x78\x41\x1e\xbf\x08\xd9\x29\xf0\x53\xf1\xe3\xf6\xa3\x41"
                         b"\x89\x26\x84\x2f\x61\x0e\x91\xa9\xc8\x1b\xd5\xb6\x4b\x86\x23\x4e"
                         b"\x9c\x0d\x2b\xac",
            ),
        },
        {
            'transitions': [
                TransitionTime(0.0, 1.3),
            ],
            'metadata': SomeMeta(
                event_time=31,
                ip_pot="131.24.48.1",
                mac_address="aa:bb:cc:dd:ee:ff",
                metadata=b"\x29\xe2\x21\x1b\x2c\x74\x1c\xfa\x6e\x78\xc8\x6b\x9c\xfd\xeb\xf6"
                         b"\x4c\x70\x3c\xd1\x86\x04\x39\x18\x19\xae\xba\x07\x69\x86\xba\x2f"
                         b"\xc1\x3b\xbc\x38\xd7\xb6\x2d\xbe\x9f\x01\x9c\x0d\x2b\xac",
            ),
        },
    ]


def sample_data_structure_yaml():
    return """\
- metadata: !iz/SomeMeta
    event_time: 12.000000s
    ip_pot: 131.23.12.1
    mac_address: 00:00:11:11:22:22
    metadata: c9 0d f2 a9 66 6a b7 bf 6a d4 3d 87 a1 b1 67 49 08 4f 1e cc fb c7 ad
      3e ee c9 27 c7 bf 9c 0c 07 6d 6f 08 0d f7 22 9b fa f6 69 26 1a 1b 64 93 af 98
      e0 78 41 1e bf 08 d9 29 f0 53 f1 e3 f6 a3 41 89 26 84 2f 61 0e 91 a9 c8 1b d5
      b6 4b 86 23 4e 9c 0d 2b ac
  transitions:
  - !iz/TransitionTime
    t_start: 0.010000s
    t_stop: 0.234000s
  - !iz/TransitionTime
    t_start: 0.012340s
    t_stop: 3.141591s
- metadata: !iz/SomeMeta
    event_time: 31.000000s
    ip_pot: 131.24.48.1
    mac_address: aa:bb:cc:dd:ee:ff
    metadata: 29 e2 21 1b 2c 74 1c fa 6e 78 c8 6b 9c fd eb f6 4c 70 3c d1 86 04 39
      18 19 ae ba 07 69 86 ba 2f c1 3b bc 38 d7 b6 2d be 9f 01 9c 0d 2b ac
  transitions:
  - !iz/TransitionTime
    t_start: 0.000000s
    t_stop: 1.300000s
"""
