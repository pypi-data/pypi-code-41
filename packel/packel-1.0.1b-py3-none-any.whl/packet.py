import pprint
from typing import Dict, List

from packel.types import PacketType


class Packet(object):
    def __init__(self, *args, **kwargs):
        """Initialize packel fields from the constructor."""
        self.serializable_fields: List[str] = []
        for field_name in dir(type(self)):
            if isinstance(getattr(type(self), field_name), PacketType):
                self.serializable_fields.append(field_name)
        self.serializable_fields.sort()

        for name, val in kwargs.items():
            if name in self.serializable_fields:
                setattr(self, name, val)

    def __iter__(self):
        for field in self.serializable_fields:
            yield (field, getattr(self, field))

    def __str__(self) -> str:
        return self.__class__.__name__ + pprint.pformat(self.as_dict(), indent=4)

    def as_dict(self) -> Dict:
        return {k:v for k, v in self}

    def serialized(self) -> bytes:
        """Serializes a packet to bytes."""
        data: bytes = b''
        for name in self.serializable_fields:
            field = getattr(type(self), name)
            field_data = field.serialize(getattr(self, name))
            if field.is_dynamic_length:
                data = data + len(field_data).to_bytes(4, 'big')
            data = data + field_data

        return data

    @classmethod
    def deserialize(cls, b: bytes):
        """Deserializes bytes to a packet.""" 
        packet = cls()

        pos = 0
        for name in packet.serializable_fields:
            field = getattr(type(packet), name)
            if field.is_dynamic_length:
                bslice = b[pos:pos+4]
                pos = pos + 4
                field_len = int.from_bytes(bslice, 'big')
            else:
                field_len = len(field.serialize(getattr(packet, name)))

            bslice = b[pos:pos+field_len]
            pos = pos + field_len
            setattr(packet, name, field.deserialize(bslice))

        return packet
