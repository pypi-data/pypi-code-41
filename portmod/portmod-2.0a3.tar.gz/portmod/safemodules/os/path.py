# Copyright 2019 Portmod Authors
# Distributed under the terms of the GNU General Public License v3

"""
A wrapper around os.path that provides safe versions of its functions for use
within pybuilds
"""
import os.path
from os.path import (  # noqa  # pylint: disable=unused-import
    abspath,
    basename,
    commonpath,
    commonprefix,
    dirname,
    expanduser,
    expandvars,
    isabs,
    join,
    normcase,
    normpath,
    relpath,
    split,
    splitdrive,
    splitext,
    supports_unicode_filenames,
)
from ..io_guard import _wrap_path_read, _wrap_path_read_2


exists = _wrap_path_read(os.path.exists)
getatime = _wrap_path_read(os.path.getatime)
getmtime = _wrap_path_read(os.path.getmtime)
getctime = _wrap_path_read(os.path.getctime)
getsize = _wrap_path_read(os.path.getsize)
isfile = _wrap_path_read(os.path.isfile)
isdir = _wrap_path_read(os.path.isdir)
islink = _wrap_path_read(os.path.islink)
ismount = _wrap_path_read(os.path.ismount)
realpath = _wrap_path_read(os.path.realpath)
samefile = _wrap_path_read_2(os.path.samefile)
