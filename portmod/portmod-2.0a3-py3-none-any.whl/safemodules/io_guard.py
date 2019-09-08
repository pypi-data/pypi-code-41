# Copyright 2019 Portmod Authors
# Distributed under the terms of the GNU General Public License v3

"""
Module that provides a function to aid construction of safe
wrapper libraries around unsafe system libraries
"""
import inspect
from enum import Enum
from pathlib import Path
from ..globals import env


class IOType(Enum):
    """Enumerated type indicating type of file IO operation"""

    Read = 1
    Write = 2
    Exec = 3  # Note that in general we allow execution when we allow reads


def _check_call(path: str, operation: IOType):
    """
    Determines if the given IO operation is valid given the context of the function call
    """
    realpath = Path(path).resolve()
    tmp_path = Path(env.TMP_DIR).resolve()
    pyclass_path = Path("pyclass")
    network = False
    global_scope = False
    valid_call = False
    for index, frame in enumerate(inspect.stack(0)):
        stack_path = Path(frame.filename)
        if stack_path.match("*/portmod/mod.py") or stack_path.match(
            "*/test/test_loader.py"
        ):
            try:
                # Path must not be relative to the pyclass directory
                stack_path.relative_to(pyclass_path)
            except ValueError:
                pass
            else:
                continue
            valid_call = frame.function in {
                "install_mod",
                "remove_mod",
            } or frame.function.startswith("test")

            # Determine the function called and set network and global scope flags
            # accordingly
            # Network access is only allowed in src_unpack and can_update_live
            network = inspect.stack(0)[index - 1].function in {
                "src_unpack",
                "can_update_live",
            }

            if valid_call:
                break
        elif (
            stack_path.match("*/portmod/repo/loader.py")
            and frame.function == "restricted_load"
        ):
            global_scope = True
            break

    if global_scope:
        raise PermissionError(
            f"Illegal access to file {realpath}\n"
            "File IO from the global scope is not allowed!"
        )

    if not valid_call:
        raise Exception("Wrapped function called from invalid context!")
    try:
        realpath.relative_to(tmp_path)
    except ValueError:
        # path is not within TMP_DIR. We must not give write permissions.
        # If network is available or this was called from the global scope,
        # we must not give read permissions either.
        if network:
            raise PermissionError(
                f"Illegal access to file {realpath}"
                "File IO from functions with network access is restricted "
                "to the build directory!"
            )
        if operation == IOType.Write:
            raise PermissionError(
                f"Illegal access to file {realpath}\n"
                "Files may not be written to outside the build directory"
            )

    # Otherwise, path is within TMP_DIR. Both read and write permissions are allowed


def _wrap_path_read(func, default=None):
    if default is None:

        def wrapper(path, *args, **kwargs):
            _check_call(path, IOType.Read)
            return func(path, *args, **kwargs)

    else:

        def wrapper(path=default, *args, **kwargs):
            _check_call(path, IOType.Read)
            return func(path, *args, **kwargs)

    return wrapper


def _wrap_path_read_2(func):
    def wrapper(path1, path2, *args, **kwargs):
        _check_call(path1, IOType.Read)
        _check_call(path2, IOType.Read)
        return func(path1, path2, *args, **kwargs)

    return wrapper


def _wrap_path_write(func):
    def wrapper(path, *args, **kwargs):
        _check_call(path, IOType.Write)
        return func(path, *args, **kwargs)

    return wrapper


def _wrap_path_write_2(func):
    def wrapper(path1, path2, *args, **kwargs):
        _check_call(path1, IOType.Write)
        _check_call(path2, IOType.Write)
        return func(path1, path2, *args, **kwargs)

    return wrapper


def _wrap_path_read_write(func):
    def wrapper(src, dst, *args, **kwargs):
        _check_call(src, IOType.Read)
        _check_call(dst, IOType.Write)
        return func(src, dst, *args, **kwargs)

    return wrapper
