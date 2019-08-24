from cmt.a_converter import AConverter
from cmt.ecmap.v1 import *
from cmt.ecmap.v2 import *


class Converter(AConverter):
    @staticmethod
    def convert(source: ECMap_2) -> 'CMap_2':
        raise ValueError(
            f"Converting {source.identifier.name} {source.format_version} to CMap {source.format_version} is not supported.")

    @staticmethod
    def downgrade(source: ECMap_2) -> ECMap_1:
        res = ECMap_1()
        res.cmap = source.cmap
        return res

    @staticmethod
    def upgrade(source: ECMap_2) -> 'ECMap_3':
        raise ValueError(
            f"Upgrading {source.identifier.name} {source.format_version} to"
            f" {source.identifier.name} {source.format_version + 1} is not supported."
        )
