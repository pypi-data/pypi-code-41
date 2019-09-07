# This program is free software: you can redistribute it and/or modify it under the
# terms of the Apache License (v2.0) as published by the Apache Software Foundation.
#
# This program is distributed in the hope that it will be useful, but WITHOUT ANY
# WARRANTY; without even the implied warranty of MERCHANTABILITY or FITNESS FOR A
# PARTICULAR PURPOSE. See the Apache License for more details.
#
# You should have received a copy of the Apache License along with this program.
# If not, see <https://www.apache.org/licenses/LICENSE-2.0>.

"""Client side queue manager."""

# standard libs
import argparse
import subprocess
from typing import List

# internal libs
from .__meta__ import __appname__
from .logging import get_logger
from .queue import QueueClient, ADDRESS, AUTHKEY


# client side logger
log = get_logger(f'{__appname__} client:')

# default command template
TEMPLATE = '{}'

# command line interface
interface = argparse.ArgumentParser()
interface.add_argument('-H', '--host', default=ADDRESS[0])
interface.add_argument('-p', '--port', default=ADDRESS[1], type=int)
interface.add_argument('-k', '--authkey', default=AUTHKEY, type=str)
interface.add_argument('-t', '--template', default=TEMPLATE)
interface.add_argument('-d', '--debug', action='store_true')


USAGE = f"""\
usage: dist_exe client [-h] [-d] [-H ADDR] [-p PORT] [-k KEY] [-t CMD]
Execute tasks from queue server.\
"""

HELP = f"""\
{USAGE}

options:
-h, --help           Show this message and exit.
-d, --debug          Show debugging messages.
-H, --host     ADDR  Hostname of server (default: {ADDRESS[0]}).
-p, --port     SIZE  Port number for clients (default: {ADDRESS[1]}).
-k, --authkey  KEY   Cryptographic authkey for connection (default: {AUTHKEY}).
-t, --template CMD   Template command (default: "{TEMPLATE}").\
"""


def main(cmdline: List[str] = None) -> int:
    """Entry-point for `dist_exe client`."""
    try:
        if not cmdline:
            print(USAGE)
            return 1

        if '-h' in cmdline or '--help' in cmdline:
            print(HELP)
            return 1

        if len(cmdline) == 1 and cmdline[0] == '-':
            opt = interface.parse_args([])
        else:
            opt = interface.parse_args(cmdline)
            if opt.debug is True:
                log.setLevel('DEBUG')
            if isinstance(opt.authkey, str):
                opt.authkey = opt.authkey.encode()

        log.info(f'subscribing to {opt.host}:{opt.port}')
        with QueueClient(address=(opt.host, opt.port), authkey=opt.authkey) as client:
            for item in iter(client.queue.get, None):
                log.info(f'running {item}')
                process = subprocess.run(opt.template.format(item), shell=True,
                                         stdout=subprocess.PIPE, stderr=subprocess.STDOUT)
                for line in process.stdout.decode('utf-8').strip().split('\n'):
                    log.debug(f'STDOUT: {line}')
                client.queue.task_done()

        return 0

    except KeyboardInterrupt:
        log.warning('keyboard interrupt - going down now!')
        return 3
