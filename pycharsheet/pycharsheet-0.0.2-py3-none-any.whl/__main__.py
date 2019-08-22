#!/usr/bin/env python3
# -*- coding: utf-8 -*-
# Copyright © 2019 Taylor C. Richberger <taywee@gmx.com>
# This code is released under the license described in the LICENSE file

from . import _meta
from .charsheet import Charsheet
from .error import ExitError
from pathlib import Path
import argparse
import atexit
import code
import locale
import readline
import shlex

histfile = Path.home() / '.pycharsheet_history'

def main():
    parser = argparse.ArgumentParser(description='Run a character sheet command line')
    parser.add_argument('-V', '--version', action='version', version=_meta.data['version'])
    args = parser.parse_args()

    try:
        readline.read_history_file(histfile)
    except FileNotFoundError:
        pass
    readline.set_history_length(1000)

    atexit.register(readline.write_history_file, histfile)

    console = code.InteractiveConsole()
    charsheet = Charsheet()

    try:
        while True:
            lexer = shlex.shlex(console.raw_input(prompt='> '), punctuation_chars=True)
            tokens = list(lexer)
            try:
                retval = getattr(charsheet, tokens[0])(*tokens[1:])
            except AttributeError:
                print(f'ERROR: No known command: {tokens[0]}')
    except (EOFError, ExitError):
        pass

if __name__ == '__main__':
    locale.setlocale(locale.LC_ALL, '')
    main()

