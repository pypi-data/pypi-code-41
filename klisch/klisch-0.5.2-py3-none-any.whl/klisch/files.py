import os
import pathlib
import shutil
from typing import Union

Path = Union[str, pathlib.Path]


def ensure_parent_folder_exists(dst_path: Path):
    dst_parent = pathlib.Path(dst_path).parent
    return dst_parent.mkdir(exist_ok=True, parents=True)


def copy_folder(src_path: Path, dst_path: Path):
    """Copy folder to specific destination.

    Args:
        src_path (str or :class:`pathlib.Path`): source file path.
        dst_path (str or :class:`pathlib.Path`): destination file path.
    """
    src_path = str(src_path)
    dst_path = str(dst_path)
    try:
        shutil.copytree(src_path, dst_path)
    except (shutil.Error, OSError) as e:
        print('Directory not copied. Error: %s' % e)


def copy(src_path: Path, dst_path: Path):
    """Copy file to specific destination or folder.

    Args:
        src_path (str or :class:`pathlib.Path`): source file path.
        dst_path (str or :class:`pathlib.Path`): destination file path or folder.
    """
    src_path = str(src_path)
    dst_path = str(dst_path)
    ensure_parent_folder_exists(dst_path)

    return shutil.copy(src_path, dst_path)


def remove(path: Path):
    """Delete the file.
    Args:
        path (str or :class:`pathlib.Path`).
    """
    path = str(path)
    return os.remove(path)


def remove_folder(path: Path):
    """Delete entire folder.
    Args:
        path (str or :class:`pathlib.Path`).
    """
    path = str(path)
    return shutil.rmtree(path)
