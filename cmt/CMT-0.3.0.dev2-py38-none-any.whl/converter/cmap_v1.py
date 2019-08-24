from typing import Union

from cmt.a_converter import AConverter
from cmt.cmap.v0 import *
from cmt.cmap.v1 import *
from cmt.ecmap.v1 import *


class Converter(AConverter):
    @staticmethod
    def convert(source: CMap_1) -> ECMap_1:
        ecmap = ECMap_1()
        ecmap.cmap = source
        ecmap.cmap.checkpoint_times = None
        return ecmap

    @staticmethod
    def downgrade(source: CMap_1) -> CMap_0:
        res = CMap_0()
        res.name = source.name

        for time in source.checkpoint_times:
            new_time = MedalTime_0()
            new_time.platin = int(time.platin * 0.6)
            new_time.gold = int(time.gold * 0.6)
            new_time.silver = int(time.silver * 0.6)
            new_time.bronze = int(time.bronze * 0.6)
            res.medal_times.append(new_time)

        res.sun_rotation = source.sun_rotation
        res.sun_angle = source.sun_angle
        res.camera_pos = source.camera_pos
        res.camera_look = source.camera_look

        for ent in source.entities:
            new_ent = None
            if type(ent) == Block_1:
                new_ent = Block_0()
                new_ent.block_type = ent.block_type
                new_ent.position = ent.position
                new_ent.scale = ent.scale
                new_ent.rotation_z = ent.rotation_z
                new_ent.checkpoint_nr = ent.checkpoint_nr
                new_ent.byte_size = ent.byte_size
            elif type(ent) == Sphere_1:
                new_ent = Sphere_0()
                new_ent.position = ent.position
            elif type(ent) == PlayerStart_1:
                new_ent = PlayerStart_0()
                new_ent.position = ent.position
                new_ent.rotation_z = ent.rotation_z
            elif type(ent) == Dummy_1:
                new_ent = Dummy_0()
                new_ent.id = ent.id
                new_ent.position = ent.position
                new_ent.scale = ent.scale
                new_ent.rotation_z = ent.rotation_z
            if new_ent is not None:
                res.entities.append(new_ent)
        return res

    @staticmethod
    def upgrade(source: CMap_1) -> 'CMap_2':
        raise ValueError(
            f"Upgrading {source.identifier.name} {source.format_version} to"
            f" {source.identifier.name} {source.format_version + 1} is not supported."
        )
