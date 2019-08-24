from cmt.a_converter import AConverter
from cmt.cmap.v0 import *
from cmt.ecmap.v0 import *
from cmt.ecmap.v1 import *


class Converter(AConverter):
    @staticmethod
    def convert(source: ECMap_0) -> CMap_0:
        return source.cmap

    @staticmethod
    def downgrade(source: ECMap_0) -> None:
        raise ValueError(
            f"Downgrading {source.identifier.name} {source.format_version} to"
            f" {source.identifier.name} {source.format_version - 1} is not possible."
        )

    @staticmethod
    def upgrade(source: ECMap_0) -> ECMap_1:
        res = ECMap_1()
        res.cmap = Converter.upgrade(source.cmap)
        return res
