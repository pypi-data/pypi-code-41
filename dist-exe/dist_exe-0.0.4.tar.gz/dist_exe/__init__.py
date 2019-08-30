# This program is free software: you can redistribute it and/or modify it under the
# terms of the Apache License (v2.0) as published by the Apache Software Foundation.
#
# This program is distributed in the hope that it will be useful, but WITHOUT ANY
# WARRANTY; without even the implied warranty of MERCHANTABILITY or FITNESS FOR A
# PARTICULAR PURPOSE. See the Apache License for more details.
#
# You should have received a copy of the Apache License along with this program.
# If not, see <https://www.apache.org/licenses/LICENSE-2.0>.

"""Entry-point for dist_exe."""

# standard libs
import sys

# internal libs
from .logging import get_logger
from . import server, client
from .__meta__ import (__appname__, __version__, __authors__, __contact__,
                       __copyright__, __website__, __description__)

# application logger
log = get_logger(__appname__)

USAGE = f"""\
usage: dist_exe [-h] {{server|client}} ...
{__description__}\
"""

EPILOG = f"""\
Documentation and issue tracking at:
{__website__}

Copyright (c) {__copyright__}
{__authors__} {__contact__}.\
"""

HELP = f"""\
{USAGE}

commands:
server                Start the server.
client                Start a client.

options:
-h, --help            Show this message and exit.
-v, --version         Show the version and exit.

{EPILOG}\
"""


ENTRY_POINTS = {
    'server': server.main,
    'client': client.main
}


def main() -> int:
    """Entry point for dist_exe."""

    if len(sys.argv) < 2:
        print(USAGE)
        return 1

    if sys.argv[1] in ('-h', '--help'):
        print(HELP)
        return 1

    if sys.argv[1] in ('-v', '--version'):
        print(__version__)
        return 1

    if sys.argv[1] not in ENTRY_POINTS:
        print(f'{__appname__}: error: "{sys.argv[1]}" is not a valid command.')
        return 2

    return ENTRY_POINTS[sys.argv[1]](sys.argv[2:])
