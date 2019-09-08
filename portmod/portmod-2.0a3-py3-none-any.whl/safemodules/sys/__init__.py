# Copyright 2019 Portmod Authors
# Distributed under the terms of the GNU General Public License v3

from sys import (  # noqa  # pylint: disable=unused-import
    byteorder,
    exc_info,
    executable,
    getfilesystemencoding,
    getsizeof,
    implementation,
    int_info,
    maxsize,
    maxunicode,
    platform,
    version,
    version_info,
)

if platform == "win32":
    from sys import getwindowsversion, winver  # noqa  # pylint: disable=unused-import
