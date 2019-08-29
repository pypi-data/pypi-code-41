import sys
import click
from aos.util import get_host_os, ProcessException
from serial.tools import miniterm

# Make command
@click.command("monitor", short_help="Serial port monitor")
@click.argument("port", required=True, nargs=1)
@click.argument("baud", required=True, nargs=1)
def cli(port, baud):
    """ Open a simple serial monitor. """
    args = ['miniterm', port, baud]
    host_os = get_host_os()
    if host_os == 'Win32':
        args += ['--eol', 'CRLF']
    elif host_os == 'OSX':
        args += ['--eol', 'CR']
    else:
        args += ['--eol', 'LF']

    sys.argv = args
    try:
        miniterm.main()
    except ProcessException as e:
        raise e
