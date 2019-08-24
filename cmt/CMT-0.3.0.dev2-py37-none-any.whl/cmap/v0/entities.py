import struct
from enum import Enum
from typing import Tuple

from cmt import utils
from cmt.cmap.a_entity import AEntity


class BlockType(Enum):
    NOTHING = 0  # white
    FINISH = 1  # red
    JUMP = 2  # green
    SPEED = 3  # yellow
    ICE = 4  # blue
    CHECKPOINT = 5  # purple


class Block(AEntity):
    def __init__(self):
        super().__init__(0, 30)
        self.block_type: BlockType = None
        self.position: Tuple[float, float, int] = (0.0, 0.0, 0)
        self.scale: Tuple[int, int, int] = (0, 0, 0)
        self.rotation_z: int = 0
        self.checkpoint_nr: int = None

    def __str__(self):
        return f"type: 0 [Block]\n" \
            f"block type: {self.block_type.value} [{self.block_type.name}]\n" \
            f"position: {self.position}\n" \
            f"scale: {self.scale}\n" \
            f"rotation z: {self.rotation_z}" \
            "" if self.block_type != 5 else f"\ncheckpoint nr: {self.checkpoint_nr}"

    @classmethod
    def decode(cls, data: bytes, offset: int, debug: bool = False) -> 'Block':
        ent = Block()

        ent.block_type = BlockType(utils.unpack_from('<B', data, offset, ("block type",), debug)[0])
        offset += 1
        utils.unpack_from('<B', data, offset, ("unused",), debug)
        offset += 1
        ent.position = utils.unpack_from('<iiI', data, offset, ("position x", "position y", "position z"), debug)
        offset += 3 * 4
        ent.scale = utils.unpack_from('<III', data, offset, ("scale x", "scale y", "scale z"), debug)
        offset += 3 * 4
        ent.rotation_z = utils.unpack_from('<f', data, offset, ("rotation z",), debug)[0]
        offset += 4
        ent.checkpoint_nr = -1
        if ent.block_type == BlockType.CHECKPOINT:
            ent.checkpoint_nr = utils.unpack_from('B', data, offset, ("checkpoint nr",), debug)[0]
            ent.byte_size += 1
        return ent

    def encode(self) -> bytearray:
        data = bytearray()
        # entity type
        data.extend(struct.pack('<B', self.type))
        # block type
        data.extend(struct.pack('<B', self.block_type.value))
        # unused byte
        data.extend(b'\x01')
        # position
        data.extend(struct.pack('<iiI', *self.position))
        # scale
        data.extend(struct.pack('<III', *self.scale))
        # rotation z
        data.extend(struct.pack('<f', self.rotation_z))
        if self.block_type == BlockType.CHECKPOINT:
            data.extend(struct.pack('<B', self.checkpoint_nr))
        return data


class Sphere(AEntity):
    def __init__(self):
        super().__init__(1, 12)
        self.position: Tuple[float, float, float] = (0.0, 0.0, 0.0)

    def __str__(self):
        return f"type: 1 [Sphere]\n" \
            f"position: {self.position}"

    @classmethod
    def decode(cls, data: bytes, offset: int, debug: bool = False) -> 'Sphere':
        ent = Sphere()

        ent.position = utils.unpack_from('<iii', data, offset, ("position x", "position y", "position z"), debug)
        return ent

    def encode(self) -> bytearray:
        data = bytearray()
        # entity type
        data.extend(struct.pack('<B', self.type))
        # position
        data.extend(struct.pack('<iii', *self.position))
        return data


class PlayerStart(AEntity):
    def __init__(self):
        super().__init__(2, 17)
        self.position: Tuple[float, float, float] = (0.0, 0.0, 0.0)
        self.rotation_z: float = 0.0

    def __str__(self):
        return f"type: 2 [PlayerStart]\n" \
            f"position: {self.position}\n" \
            f"rotation z: {self.rotation_z}"

    @classmethod
    def decode(cls, data: bytes, offset: int, debug: bool = False) -> 'PlayerStart':
        ent = PlayerStart()

        utils.unpack_from('<B', data, offset, ("unused",), debug)
        offset += 1
        ent.position = utils.unpack_from('<iii', data, offset, ("position x", "position y", "position z"), debug)
        offset += 3 * 4
        ent.rotation_z = utils.unpack_from('<f', data, offset, ("rotation z",), debug)[0]
        return ent

    def encode(self) -> bytearray:
        data = bytearray()
        # entity type
        data.extend(struct.pack('<B', self.type))
        # unused byte
        data.extend(b'\x00')
        # position
        data.extend(struct.pack('<iii', *self.position))
        # rotation z
        data.extend(struct.pack('<f', self.rotation_z))
        return data


class Dummy(AEntity):
    def __init__(self):
        super().__init__(128, 29)
        self.id: int = None
        self.position: Tuple[float, float, int] = (0.0, 0.0, 0)
        self.scale: Tuple[int, int, int] = (0, 0, 0)
        self.rotation_z: float = 0.0

    def __str__(self):
        return f"type: 128 [Dummy]\n" \
            f"id: {self.id}\n" \
            f"position: {self.position}\n" \
            f"scale: {self.scale}\n" \
            f"rotation z: {self.rotation_z}"

    @classmethod
    def decode(cls, data: bytes, offset: int, debug: bool = False) -> 'Dummy':
        ent = Dummy()

        ent.id = utils.unpack_from('<B', data, offset, ("id",), debug)[0]
        offset += 1
        ent.position = utils.unpack_from('<iiI', data, offset, ("position x", "position y", "position z"), debug)
        offset += 3 * 4
        ent.scale = utils.unpack_from('<III', data, offset, ("scale x", "scale y", "scale z"), debug)
        offset += 3 * 4
        ent.rotation_z = utils.unpack_from('<f', data, offset, ("rotation z",), debug)[0]
        return ent

    def encode(self) -> bytearray:
        data = bytearray()
        # entity type
        data.extend(struct.pack('<B', self.type))
        # id
        data.extend(struct.pack('<B', self.id))
        # position
        data.extend(struct.pack('<iiI', *self.position))
        # scale
        data.extend(struct.pack('<III', *self.scale))
        # rotation z
        data.extend(struct.pack('<f', self.rotation_z))
        return data
