from pathlib import Path

from cmt import utils
from cmt.a_map import AMap, MapType
from cmt.cmap.v0 import *
from cmt.cmap.v1 import *
from cmt.ecmap.v0 import *
from cmt.ecmap.v1 import *
from cmt.ecmap.v2 import *


def decode(file: Path, debug: bool = False) -> AMap:
    """
    :raises ValueError: something failed
    """
    with file.open("rb") as reader:
        data = reader.read()

    identifier = data[0:11].decode("utf-8")
    if debug:
        utils.debug_print(data[0:11], "identifier", identifier, 0)
    offset = 11

    if identifier == MapType.CMAP.value:
        version = utils.unpack_from('<B', data, offset, ("version",), debug)[0]
        offset += 1
        if version == 0:
            return CMap_0.decode(data, offset, debug)
        elif version == 1:
            return CMap_1.decode(data, offset, debug)
        else:
            raise ValueError(f"reading .cmap version {version} is not supported")
    elif identifier == MapType.ECMAP.value:
        version = utils.unpack_from('<B', data, offset, ("version",), debug)[0]
        offset += 1
        if version == 0:
            return ECMap_0.decode(data, offset, debug)
        elif version == 1:
            return ECMap_1.decode(data, offset, debug)
        elif version == 2:
            return ECMap_2.decode(data, offset, debug)
        else:
            raise ValueError(f"reading .ecmap version {version} is not supported")
    else:
        raise ValueError("given data is not a .cmap or .ecmap")
