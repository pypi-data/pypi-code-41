# Copyright 2019 Portmod Authors
# Distributed under the terms of the GNU General Public License v3

import shutil
from shutil import which, get_archive_formats  # noqa  # pylint: disable=unused-import
from ..io_guard import (
    _wrap_path_read,
    _wrap_path_write_2,
    _wrap_path_write,
    _wrap_path_read_write,
)

copyfile = _wrap_path_read_write(shutil.copyfile)
copymode = _wrap_path_read_write(shutil.copymode)
copystat = _wrap_path_read_write(shutil.copystat)
copy = _wrap_path_read_write(shutil.copy)
copy2 = _wrap_path_read_write(shutil.copy2)
copytree = _wrap_path_read_write(shutil.copytree)
rmtree = _wrap_path_write(shutil.rmtree)
move = _wrap_path_write_2(shutil.move)
disk_usage = _wrap_path_read(shutil.disk_usage)
chown = _wrap_path_write(shutil.chown)

# FIXME: Archiving operations have been omitted
