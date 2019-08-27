__version__ = "1"

import logging
import platform
from pathlib import Path

log = logging.Logger(__name__)

if platform.system() != "Windows":
    log.warning("This module is intended for windows only.")

_data_path = Path(__file__).parent / "data"
_lib_path = _data_path / "lib" / "x64"

dll_path = _lib_path / "pthreadVC2.dll"
import_lib_path = _lib_path / "pthreadVC2.lib"
include_path = _data_path / "include"
