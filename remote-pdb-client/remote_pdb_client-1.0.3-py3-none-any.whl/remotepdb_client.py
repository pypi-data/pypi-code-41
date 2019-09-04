#!/usr/bin/env python3

import argparse
from os.path import expanduser
import re
import signal
import sys
import telnetlib
import time

from prompt_toolkit import print_formatted_text
from prompt_toolkit import prompt

from prompt_toolkit.formatted_text import FormattedText
from prompt_toolkit.history import FileHistory
from prompt_toolkit.styles import Style

try:
    from remotepdb_client.__config__ import PACKAGE_DATA
except ModuleNotFoundError:
    from __config__ import PACKAGE_DATA

TITLE = '{} v{}'.format(PACKAGE_DATA['friendly_name'], PACKAGE_DATA['version'])


def exit_handler():
    print()
    print('Exiting...')
    sys.exit(0)


def signal_handler(signal, frame):
    print()
    exit_handler()


def pad_line(padding=0):
    for _ in range(padding):
        print()


def setup(params):
    signal.signal(signal.SIGINT, signal_handler)

    default_host = 'localhost'
    default_port = 4544
    default_delay = 0.5  # Time between retries (s)
    minimum_delay = 0.1  # Lower bounds on delay (s)
    default_theme = 'none'
    default_prompt = '(Pdb) '  # trailing spaces are important
    default_pad_before = 0
    default_pad_after = 1

    def port_value(string):
        value = int(string)
        if not (0 <= value <= 65535):
            msg = 'Port {} is invalid'.format(string)
            raise argparse.ArgumentTypeError(msg)
        return value

    def delay_value(string):
        value = float(string)
        if value and value < minimum_delay:
            msg = '{} is less than minimum delay {}'.format(string, minimum_delay)
            raise argparse.ArgumentTypeError(msg)
        return value

    parser = argparse.ArgumentParser(
        description='{} - {}'.format(TITLE, PACKAGE_DATA['description']),
        formatter_class=argparse.ArgumentDefaultsHelpFormatter,
    )
    parser.add_argument('--host', metavar='HOST_NAME', required=False,
                        type=str, default=default_host,
                        help='hostname to connect to')
    parser.add_argument('--port', metavar='PORT', required=False,
                        type=port_value, default=default_port,
                        help='port to connect to')
    parser.add_argument('--delay', metavar='DELAY_SECS', required=False,
                        type=delay_value, default=default_delay,
                        help='connection retry delay')
    parser.add_argument('--theme', metavar='THEME_NAME', required=False,
                        type=str, default=default_theme,
                        help='display theme (dark, light, none)')
    parser.add_argument('--padbefore', required=False,
                        type=int, metavar='LINES', default=default_pad_before,
                        help='pad before remote lines')
    parser.add_argument('--padafter', metavar='LINES', required=False,
                        type=int, default=default_pad_after,
                        help='pad after remote lines')
    parser.add_argument('--prompt', metavar='STRING', required=False,
                        type=str, default=default_prompt,
                        help='remote prompt incl. trailing spaces')
    parser.add_argument('--debug', action='store_true',
                        help='Enable debugging output')
    args = parser.parse_args()

    params['host'] = args.host if args.host else default_host
    params['port'] = args.port
    params['delay'] = args.delay
    params['prompt'] = args.prompt if args.prompt else default_prompt
    params['prompt_local'] = [('class:prompt', params['prompt'].strip()), ('', ' ')]
    params['pad_before'] = args.padbefore
    params['pad_after'] = args.padafter
    params['delay_timeout'] = time.time()
    params['debug'] = args.debug

    styles = {
        'none': {
            '': '',  # User input (default text)
            'prompt': '',
            'output': '',
            'wait': '',
            'alert': '',
            'title': '',
        },
        'light': {
            '': 'fg:ansigreen',  # User input (default text)
            'prompt': 'fg:ansicyan',
            'output': 'fg:ansibrightblack',
            'wait': 'fg:ansiblue',
            'alert': 'fg:ansired',
            'title': 'fg:ansiblack bold',
        },
        'dark': {
            '': 'fg:ansiyellow',  # User input (default text)
            'prompt': 'fg:ansigreen',
            'output': 'fg:ansiwhite',
            'wait': 'fg:ansicyan',
            'alert': 'fg:ansibrightred',
            'title': 'fg:ansiwhite bold',
        },
    }

    params['theme'] = args.theme.lower() if args.theme else default_theme
    params['style'] = Style.from_dict(styles[params['theme']])
    params['history'] = FileHistory(expanduser('~/.remotepdb_history'))

    return params


p_continue_until = re.compile(r'^c\s*(\d+)$')
auto_continue = False


def check_alive(params, telnet_obj):
    try:
        if telnet_obj.sock:
            # A NOP is usually IAC+NOP but it causes codec errors in remotepdb!
            for attemps in range(4):
                telnet_obj.sock.send(b'\n\n')
                time.sleep(0.1)
            return True
        else:
            if params['debug']:
                print('DEBUG: Socket not connected')
    except Exception as e:
        if params['debug']:
            print('DEBUG: Send failed ({})'.format(e))


def connector(params):
    remote = telnetlib.Telnet(params['host'], params['port'])
    read_remote = True
    if not check_alive(params, remote):
        return False
    while True:
        if time.time() < params['delay_timeout']:
            remote.write('c'.encode('ascii') + b'\n')
            break
        if read_remote:
            try:
                textin = remote.read_until(params['prompt'].encode('ascii'))
            except ConnectionResetError:
                if params['debug']:
                    print('DEBUG: Connection reset by peer')
                break
            text_main = textin.decode('ascii').rsplit(params['prompt'], 1)
            pad_line(params['pad_before'])
            for line in text_main[0].splitlines():
                print_formatted_text(
                    FormattedText(
                        [('class:output', line)],
                    ),
                    style=params['style'],
                )
            pad_line(params['pad_after'])
        try:
            textout = prompt(
                params['prompt_local'],
                style=params['style'],
                history=params['history'],
            ).strip()
        except KeyboardInterrupt:
            if params['debug']:
                print('DEBUG: Keyboad interrupt')
            remote.write('c'.encode('ascii') + b'\n')
            exit_handler()

        if textout in ['e', 'exit', 'q', 'quit']:
            remote.write('c'.encode('ascii') + b'\n')
            exit_handler()

        m = p_continue_until.match(textout)
        if m:
            print_formatted_text(
                FormattedText(
                    [('class:wait', 'Continuing for {} seconds...'.format(m.group(1)))],
                ),
                style=params['style'],
            )
            pad_line(params['pad_after'])
            params['delay_timeout'] = time.time() + float(m.group(1))
            break
        if textout in ['c']:
            remote.write('c'.encode('ascii') + b'\n')
            break
        elif textout in ['cl', 'clear']:
            pad_line(params['pad_before'])
            print_formatted_text(
                FormattedText(
                    [('class:alert', '`{}` is not allowed here (would block on stdin on the server)'.format(textout))],
                ),
                style=params['style'],
            )
            pad_line(params['pad_after'])
            read_remote = False
        else:
            remote.write(textout.encode('ascii') + b'\n')
            read_remote = True
    remote.close()
    return True


def main(params={}):
    setup(params=params)
    print()
    print_formatted_text(
        FormattedText(
            [('class:title', '{} debugging via {}:{}'.format(TITLE, params['host'], params['port']))],
        ),
        style=params['style'],
    )
    print()
    waiting = False
    while True:
        try:
            if params['debug']:
                print('DEBUG: Attempting to connect')
            if connector(params=params):
                waiting = False
        except (ConnectionRefusedError, EOFError):
            if params['debug']:
                print('DEBUG: Connection refused')
        if not waiting:
            pad_line(params['pad_before'])
            print_formatted_text(
                FormattedText(
                    [('class:wait', 'Waiting for breakpoint/trace...')],
                ),
                style=params['style'],
            )
            pad_line(params['pad_after'])
            waiting = True
            time.sleep(params['delay'])


if __name__ == '__main__':
    main()
