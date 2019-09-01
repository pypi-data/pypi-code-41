from typing import List, Type

from packel.packet import Packet


class Protocol(object):
    def __init__(self, packet_classes: List[Type[Packet]]):
        self.packet_classes = packet_classes

    def serialize(self, packet: Packet) -> bytes:
        """Serializes a packet to bytes."""
        if not isinstance(packet, Packet):
            raise ValueError(f"'{type(packet)}' is not a packet type.")

        try:
            index: int = self.packet_classes.index(type(packet))
        except ValueError:
            raise ValueError(f"'{type(packet)}' packet type is not registered in the protocol.")

        return index.to_bytes(4, 'big') + packet.serialized()

    def deserialize(self, b: bytes) -> Packet:
        """Deserializes bytes to a packet.""" 
        index = int.from_bytes(b[:4], 'big')
        if index > len(self.packet_classes):
            raise ValueError(f"Packet type '{index}' exceeds number of registered protocol packet types.")

        return self.packet_classes[index].deserialize(b[4:])
