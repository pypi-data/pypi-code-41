#
# Copyright (c) 2018-present, wobe-systems GmbH
#
# This source code is licensed under the MIT license found in the
# LICENSE file in the root directory of this source tree.
#

""" Ujo Types submodule variants
"""

from typing import Union

from .base import UjoBase  # noqa: F401
from .none import UjoNone  # noqa: F401
from .none import UJO_VARIANT_NONE  # noqa: F401
from .boolean import UjoBool  # noqa: F401
from .integer import UjoUInt8  # noqa: F401
from .integer import UjoInt8  # noqa: F401
from .integer import UjoUInt16  # noqa: F401
from .integer import UjoInt16  # noqa: F401
from .integer import UjoUInt32  # noqa: F401
from .integer import UjoInt32  # noqa: F401
from .integer import UjoUInt64  # noqa: F401
from .integer import UjoInt64  # noqa: F401
from .float import UjoFloat64  # noqa: F401
from .float import UjoFloat32  # noqa: F401
from .float import UjoFloat16  # noqa: F401
from .string import UjoStringC  # noqa: F401
from .string import UjoStringUTF8  # noqa: F401
from .timestamp import UjoTimestamp  # noqa: F401
from .container import UjoList  # noqa: F401
from .container import UjoMap  # noqa: F401
from .container import UjoContainer  # noqa: F401
from .container import variant_factory  # noqa: F401
from .container import read_file  # noqa: F401
from .container import write_file  # noqa: F401
from .container import read_buffer  # noqa: F401
from .container import write_buffer  # noqa: F401

# for type hinting purposes
UjoVariant = Union[
    UjoNone,
    UjoBool,
    UjoUInt8,
    UjoInt8,
    UjoUInt16,
    UjoInt16,
    UjoUInt32,
    UjoInt32,
    UjoUInt64,
    UjoInt64,
    UjoFloat64,
    UjoFloat32,
    UjoFloat16,
    UjoStringC,
    UjoStringUTF8,
    UjoTimestamp,
]
