from cmt.a_converter import AConverter
from cmt.a_map import AMap, MapType
from cmt.converter import *


def _get_converter(map_type: MapType, version: int) -> AConverter:
    """
    :raises ValueError: something failed
    """
    if map_type == MapType.CMAP and version == 0:
        return Converter_cmap_0()
    elif map_type == MapType.CMAP and version == 1:
        return Converter_cmap_1()
    elif map_type == MapType.ECMAP and version == 0:
        return Converter_ecmap_0()
    elif map_type == MapType.ECMAP and version == 1:
        return Converter_ecmap_1()
    elif map_type == MapType.ECMAP and version == 2:
        return Converter_ecmap_2()
    raise ValueError(f"Converter for {map_type.name} {version} does not exist.")


def convert(source: AMap, version: int, target: MapType) -> AMap:
    """
    :raises ValueError: something failed
    """
    res = source
    while res.format_version != version:
        if res.format_version > version:
            res = _get_converter(res.identifier, res.format_version).downgrade(res)
        else:
            res = _get_converter(res.identifier, res.format_version).upgrade(res)

    if res.identifier != target:
        res = _get_converter(res.identifier, res.format_version).convert(res)
    return res
