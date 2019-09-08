# Copyright 2019 Portmod Authors
# Distributed under the terms of the GNU General Public License v3

"""
A wrapper around filecmp that provides safe versions of its functions for use
within pybuilds
"""
import filecmp
from filecmp import clear_cache  # noqa  # pylint: disable=unused-import
from .io_guard import _wrap_path_read_2

cmp = _wrap_path_read_2(filecmp.cmp)
cmpfiles = _wrap_path_read_2(filecmp.cmpfiles)
dircmp = _wrap_path_read_2(filecmp.dircmp)
