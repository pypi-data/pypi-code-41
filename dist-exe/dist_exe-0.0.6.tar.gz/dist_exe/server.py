# This program is free software: you can redistribute it and/or modify it under the
# terms of the Apache License (v2.0) as published by the Apache Software Foundation.
#
# This program is distributed in the hope that it will be useful, but WITHOUT ANY
# WARRANTY; without even the implied warranty of MERCHANTABILITY or FITNESS FOR A
# PARTICULAR PURPOSE. See the Apache License for more details.
#
# You should have received a copy of the Apache License along with this program.
# If not, see <https://www.apache.org/licenses/LICENSE-2.0>.

"""Server side queue manager."""

# standard libs
import sys
import argparse
from typing import List

# internal libs
from .__meta__ import __appname__
from .logging import get_logger
from .queue import QueueServer, ADDRESS, AUTHKEY, MAXSIZE


# server side logger
log = get_logger(f'{__appname__} server:')

# command line interface
interface = argparse.ArgumentParser()
interface.add_argument('-H', '--host', default=ADDRESS[0])
interface.add_argument('-p', '--port', default=ADDRESS[1], type=int)
interface.add_argument('-k', '--authkey', default=AUTHKEY, type=str)
interface.add_argument('-d', '--debug', action='store_true')
interface.add_argument('-s', '--maxsize', default=MAXSIZE, type=int)


USAGE = f"""\
usage: dist_exe server [-h] [-d] [-H ADDR] [-p PORT] [-k KEY] [-s SIZE]
Start task server.\
"""

HELP = f"""\
{USAGE}

options:
-h, --help           Show this message and exit.
-d, --debug          Show debugging messages.
-H, --host     ADDR  Hostname of server (default: {ADDRESS[0]}).
-p, --port     PORT  Port number for clients (default: {ADDRESS[1]}).
-k, --authkey  KEY   Cryptographic authkey for connection (default: {AUTHKEY}).
-s, --maxsize  SIZE  Maximum items allowed in the queue (default: {MAXSIZE}).
"""


def main(cmdline: List[str] = None) -> int:
    """Entry-point for `dist_exe server`."""
    try:
        if not cmdline:
            print(USAGE)
            return 1

        if '-h' in cmdline or '--help' in cmdline:
            print(HELP)
            return 1

        if len(cmdline) == 1 and cmdline[0] == '-':
            # no arguments, read from stdin
            opt = interface.parse_args([])
        else:
            opt = interface.parse_args(cmdline)
            if opt.debug is True:
                log.setLevel('DEBUG')
            if isinstance(opt.authkey, str):
                opt.authkey = opt.authkey.encode()

        log.info(f'starting server on port {opt.port}')
        with QueueServer(address=(opt.host, opt.port), authkey=opt.authkey,
                         maxsize=opt.maxsize) as server:
            for line in sys.stdin:
                log.info(f'queueing {line.strip()}')
                server.queue.put(line.strip())

        return 0

    except KeyboardInterrupt:
        log.warning('keyboard interrupt - going down now!')
        return 3
