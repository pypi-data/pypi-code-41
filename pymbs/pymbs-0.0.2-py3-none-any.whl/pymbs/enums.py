"""
PyMBS is a Python library for use in modeling Mortgage-Backed Securities.
Copyright (C) 2019  Brian Farrell

This program is free software: you can redistribute it and/or modify
it under the terms of the GNU Affero General Public License as published
by the Free Software Foundation, either version 3 of the License, or
(at your option) any later version.

This program is distributed in the hope that it will be useful,
but WITHOUT ANY WARRANTY; without even the implied warranty of
MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
GNU Affero General Public License for more details.

You should have received a copy of the GNU Affero General Public License
along with this program.  If not, see <https://www.gnu.org/licenses/>.

Contact: brian.farrell@me.com
"""

from enum import Enum, IntEnum


class ExitCode(IntEnum):
    """Enumeration of exit codes.

    This class implements POSIX error codes, as found in
    /usr/include/sysexits.h on the Linux platform and
    described in the manual page for sysexit on BSD systems,
    including Darwin (macOS).

    Additional information is availble from The Linux Documnetation Project
    at http://tldp.org/LDP/abs/html/exitcodes.html
    """
    EX_SUCCESS = 0  # command exits successfully
    EX_GENERAL = 1  # catchall for general errors
    EX_USAGE = 64  # command line usage error
    EX_DATAERR = 65  # data format error
    EX_NOINPUT = 66  # cannot open input
    EX_NOUSER = 67  # addressee unknown
    EX_NOHOST = 68  # host name unknown
    EX_UNAVAILABLE = 69  # service unavailable
    EX_SOFTWARE = 70  # internal software error
    EX_OSERR = 71  # system error (e.g., can't fork)
    EX_OSFILE = 72  # critical OS file missing
    EX_CANTCREAT = 73  # can't create (user) output file
    EX_IOERR = 74  # input/output error
    EX_TEMPFAIL = 75  # temp failure; user is invited to retry
    EX_PROTOCOL = 76  # remote error in protocol
    EX_NOPERM = 77  # permission denied
    EX_CONFIG = 78  # configuration error
    EX_SIGINT = 130  # keyboard interrupt


class PrepayBenchmark(Enum):
    """docstring for PrepayBenchmark"""
    CPR = 'CPR'
    PSA = 'PSA'
