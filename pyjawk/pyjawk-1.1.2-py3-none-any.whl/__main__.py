#!/usr/bin/env python3
# -*- coding: utf-8 -*-
# Copyright © 2019 Taylor C. Richberger
# This code is released under the license described in the LICENSE file

from operator import itemgetter
from pathlib import Path
from pprint import pprint
from ptpython.repl import embed
from xml.dom import minidom
import appdirs
from io import StringIO, BytesIO
import argparse
import json
import locale
import msgpack
import sys
import xml.etree.ElementTree as ET
import yaml

from . import _meta
from .license import License
from .color import color_options, get_colorizer

def trim_whitespace_text(element):
    '''Trim whitespace text children unless they are the only child of an element'''

    children = list(element)
    if len(children) > 0:
        if not element.text or element.text.isspace():
            element.text = None
        for child in children:
            if not child.tail or child.tail.isspace():
                child.tail = None
            trim_whitespace_text(child)

class NullContext:
    '''Simple context manager that does nothing but pass out its value'''

    def __init__(self, value):
        self.value = value

    def __enter__(self):
        return self.value

    def __exit__(self, *args, **kwargs):
        pass

formats = [
    'json',
    'yaml',
    'xml',
    'msgpack',
    'python',
    'string',
    'bytes',
]

binary = {
    'msgpack',
    'bytes',
}

def main(default_format='json'):
    parser = argparse.ArgumentParser(description='Transform json input and output.')
    parser.add_argument('-V', '--version', help='prints license information', action='version', version=str(_meta.version))
    parser.add_argument('--license', help='prints license information', action=License, license=_meta.license)
    parser.add_argument('--color', help="Whether or not to output with color.  auto will try to detect if the output is a terminal and colorize in that case only.  If you know you have a better terminal, you can turn on 256color or truecolor for better output.", default='auto', choices=color_options)
    parser.add_argument('-c', '--compact', help="Compact output.  By default, output is prettified.  Specify twice to pack output as much as possible.  In the REPL, this may be set to 0, 1, or 2 to modify compactness.  This does not apply to all formats", action='count', default=0)
    parser.add_argument('-o', '--output', help="Output file. If not specified, uses stdout (may be explicitly specified with -).", default='-')
    parser.add_argument('-i', '--input', help="Input file. If not specified, uses stdin (may be explicitly specified with -).", default='-')
    parser.add_argument('-n', '--no-input', help="Do not take any input.  data object will be initialized to None", action='store_true')
    parser.add_argument('-N', '--no-output', help="Do not dump any output.", action='store_true')
    parser.add_argument('-f', '--file', dest='files', help="Script file(s) to be executed.  These are always run before the exec blocks regardless of order.  May be - for stdin", action='append', default=[])
    parser.add_argument('-r', '--repl', help="Open a ptpython REPL after running all script blocks and files.  Will not write to output by default, will only do so when write() is called.  Also gives you direct access to the argparse object, so you can customize output and change the destination.", action='store_true')
    parser.add_argument('-I', '--input-format', help="Input file format (default: %(default)s).", default=default_format, choices=formats)
    parser.add_argument('-O', '--output-format', help="Output file format (default: %(default)s).", default=default_format, choices=formats)
    parser.add_argument('-e', '--exec', dest='execs', help="Full script blocks to be exec'd.", action='append', default=[])
    parser.add_argument('--keep-whitespace', help="For XML dumping, whitespace children with node siblings are normally trimmed before any formatting.  This option suppresses that.", action='store_true')
    parser.add_argument('expression', help="An expression to be evaluated, assigning the result to data.  This is always run after all file and exec arguments.", nargs='?')
    args = parser.parse_args()

    binary_in = args.input_format in binary
    binary_out = args.output_format in binary

    if binary_in:
        stdin = sys.stdin.buffer
        read_mode = 'rb'
    else:
        stdin = sys.stdin
        read_mode = 'r'

    if binary_out:
        stdout = sys.stdout.buffer
        write_mode = 'wb'
    else:
        stdout = sys.stdout
        write_mode = 'w'

    def input(path):
        '''Evaluate an input option for use with a context manager, to
        determine if it should actually open a file or just use stdin.

        This is done because we don't want to close stdin.
        '''
        if path == '-':
            return NullContext(stdin)
        else:
            return open(path, read_mode)

    def output(path):
        '''Evaluate an output option to determine whether it is represented by
        a file or pass-closing stdout.
        
        This is done because we don't want to close stdout.
        '''
        if path == '-':
            return NullContext(stdout)
        else:
            return open(path, write_mode)

    if args.no_input:
        data = None
    else:
        with input(args.input) as file:
            if args.input_format == 'json':
                data = json.load(file)
            elif args.input_format == 'yaml':
                data = yaml.load(file)
            elif args.input_format == 'xml':
                data = ET.parse(file).getroot()
            elif args.input_format == 'msgpack':
                data = msgpack.load(file, raw=False)
            elif args.input_format == 'python':
                data = eval(file.read())
            elif args.input_format in {'string', 'bytes'}:
                data = file.read()
            else:
                raise f'Format {args.input_format!r} not supported'

    scripts = []

    for path in args.files:
        with input(path) as file:
            scripts.append(file.read())

    scripts += args.execs

    environment = {'data': data}

    for script in scripts:
        exec(script, environment)

    if args.expression:
        environment['data'] = eval(args.expression, environment)

    def write():
        '''A function for writing, so that it can be embedded into the REPL'''

        if not args.no_output:
            data = environment['data']

            if binary_out:
                file = BytesIO()
            else:
                file = StringIO()

            if args.output_format == 'json':
                if args.compact == 0:
                    json.dump(data, file, indent=2)
                    file.write('\n')
                elif args.compact == 1:
                    json.dump(data, file)
                    file.write('\n')
                else:
                    json.dump(data, file, separators=(',', ':'))

            elif args.output_format == 'yaml':
                if args.compact == 0:
                    yaml.dump(data, file, default_flow_style=False)
                elif args.compact == 1:
                    yaml.dump(data, file)
                else:
                    yaml.dump(data, file, default_flow_style=True)

            elif args.output_format == 'xml':
                if not args.keep_whitespace:
                    trim_whitespace_text(data)

                xml_string = ET.tostring(data, encoding='utf8').decode('utf-8') + '\n'

                if args.compact == 0:
                    xml_string = minidom.parseString(xml_string).toprettyxml(indent='  ')

                file.write(xml_string)

            elif args.output_format == 'msgpack':
                data = msgpack.dump(data, file, use_bin_type=True)

            elif args.output_format == 'python':
                if args.compact == 0:
                    pprint(data, file, indent=2)
                elif args.compact == 1:
                    pprint(data, file, indent=2, compact=True)
                else:
                    file.write(repr(data))
                    file.write('\n')

            elif args.output_format == 'string':
                file.write(str(data))
                if args.compact == 0:
                    file.write('\n')

            elif args.output_format == 'bytes':
                file.write(data)

            else:
                raise f'Format {args.output_format!r} not supported'

            with output(args.output) as outFile:
                colorizer = get_colorizer(args.output_format, args.color, outFile)
                outFile.write(colorizer(file.getvalue()))

    if args.repl:
        histfile = Path(appdirs.user_cache_dir('pyjawk')) / 'history'
        histfile.parent.mkdir(mode=0o700, parents=True, exist_ok=True)
        environment['write'] = write
        environment['args'] = args
        embed(environment, environment, history_filename=str(histfile), title='pyjawk')
    else:
        write()

def pyyawk():
    main('yaml')
def pyxawk():
    main('xml')
def pymawk():
    main('msgpack')
def pypawk():
    main('python')
def pysawk():
    main('string')
def pybawk():
    main('bytes')

if __name__ == '__main__':
    locale.setlocale(locale.LC_ALL, '')
    main()
