#!/usr/bin/env python3
# -*- coding: utf-8 -*-
# Copyright © 2019 Taylor C. Richberger
# This code is released under the license described in the LICENSE file

from pathlib import Path
from ptpython.repl import embed
import argparse
import json
import locale
import sys
import appdirs

from ._meta import version

class NullContext:
    '''Simple context manager that does nothing but pass out its value'''

    def __init__(self, value):
        self.value = value

    def __enter__(self):
        return self.value

    def __exit__(self, *args, **kwargs):
        pass

def main():
    parser = argparse.ArgumentParser(description='Transform json input and output.')
    parser.add_argument('-V', '--version', action='version', version=str(version))
    parser.add_argument('-c', '--compact', help="Compact output.  By default, output is prettified.  Specify twice to pack output as much as possible.  In the REPL, this may be set to 0, 1, or 2 to modify compactness.", action='count', default=0)
    parser.add_argument('-o', '--output', help="Output file. If not specified, uses stdout (may be explicitly specified with -).", default='-')
    parser.add_argument('-i', '--input', help="Input file. If not specified, uses stdin (may be explicitly specified with -).", default='-')
    parser.add_argument('-n', '--no-input', help="Do not take any input, instead just use a blank dictionary as the input.", action='store_true')
    parser.add_argument('-f', '--file', dest='files', help="Script file(s) to be executed.  These are always run before the literal script blocks.", action='append', type=Path, default=[])
    parser.add_argument('-r', '--repl', help="Open a ptpython REPL after running all script blocks and files.  Will not write to output by default, will only do so when write() is called.  Also gives you direct access to the argparse object, so you can customize output and change the destination.", action='store_true')
    parser.add_argument('scripts', help="Script blocks to be executed.", nargs='*')
    args = parser.parse_args()

    if args.no_input:
        data = {}
    else:
        with NullContext(sys.stdin) if args.input == '-' else open(args.input, 'r') as file:
            data = json.load(file)

    scripts = []

    for path in args.files:
        with path.open() as file:
            scripts.append(file.read())

    scripts += args.scripts

    environment = {'data': data}

    for script in scripts:
        exec(script, environment)

    def write():
        data = environment['data']

        with NullContext(sys.stdout) if args.output == '-' else open(args.output, 'w') as file:
            if args.compact == 0:
                data = json.dump(data, file, indent=2)
            elif args.compact == 1:
                data = json.dump(data, file)
            else:
                data = json.dump(data, file, separators=(',', ':'))
            file.write('\n')

    if args.repl:
        histfile = Path(appdirs.user_cache_dir('pyjawk')) / 'history'
        histfile.parent.mkdir(mode=0o700, parents=True, exist_ok=True)
        environment['write'] = write
        environment['args'] = args
        embed(environment, environment, history_filename=str(histfile), title='pyjawk')
    else:
        write()

if __name__ == '__main__':
    locale.setlocale(locale.LC_ALL, '')
    main()
