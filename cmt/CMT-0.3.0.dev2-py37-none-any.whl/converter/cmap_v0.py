from cmt.a_converter import AConverter
from cmt.cmap.v0 import *
from cmt.cmap.v1 import *
from cmt.ecmap.v0 import *


class Converter(AConverter):
    @staticmethod
    def convert(source: CMap_0) -> ECMap_0:
        ecmap = ECMap_0()
        ecmap.cmap = source
        ecmap.cmap.medal_times = None
        return ecmap

    @staticmethod
    def downgrade(source: CMap_0) -> None:
        raise ValueError(
            f"Downgrading {source.identifier.name} {source.format_version} to"
            f" {source.identifier.name} {source.format_version - 1} is not possible."
        )

    @staticmethod
    def upgrade(source: CMap_0) -> CMap_1:
        res = CMap_1()
        res.name = source.name

        for time in source.medal_times:
            new_time = CheckpointTime_1()
            new_time.platin = int(time.platin * 5 / 3)
            new_time.gold = int(time.gold * 5 / 3)
            new_time.silver = int(time.silver * 5 / 3)
            new_time.bronze = int(time.bronze * 5 / 3)
            res.checkpoint_times.append(new_time)

        res.sun_rotation = source.sun_rotation
        res.sun_angle = source.sun_angle
        res.camera_pos = source.camera_pos
        res.camera_look = source.camera_look

        for ent in source.entities:
            new_ent = None
            if type(ent) == Block_0:
                new_ent = Block_1()
                new_ent.block_type = ent.block_type
                new_ent.position = ent.position
                new_ent.scale = ent.scale
                new_ent.rotation_z = ent.rotation_z
                new_ent.checkpoint_nr = ent.checkpoint_nr
                new_ent.byte_size = ent.byte_size
            elif type(ent) == Sphere_0:
                new_ent = Sphere_1()
                new_ent.position = ent.position
            elif type(ent) == PlayerStart_0:
                new_ent = PlayerStart_1()
                new_ent.position = ent.position
                new_ent.rotation_z = ent.rotation_z
            elif type(ent) == Dummy_0:
                new_ent = Dummy_1()
                new_ent.id = ent.id
                new_ent.position = ent.position
                new_ent.scale = ent.scale
                new_ent.rotation_z = ent.rotation_z
            if new_ent is not None:
                res.entities.append(new_ent)
        return res
