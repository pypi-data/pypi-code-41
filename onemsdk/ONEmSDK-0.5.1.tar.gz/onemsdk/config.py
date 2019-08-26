import os
from pathlib import Path

from onemsdk.exceptions import ONEmSDKException

_static_dir = None


def get_static_dir() -> str:
    global _static_dir
    return _static_dir


def set_static_dir(static_dir: str) -> None:
    global _static_dir
    path = Path(static_dir)
    if not path.exists() or not path.is_dir():
        raise ONEmSDKException(f'{path.absolute()} is not a dir')
    _static_dir = str(path.absolute())
