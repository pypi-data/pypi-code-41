#!/usr/bin/env python3
# -*- coding: utf-8 -*-
# -*- coding: utf-8 -*-
# Copyright © 2019 Taylor C. Richberger and Brandon Phillips
# This code is released under the license described in the LICENSE file

from . import _meta
from .cli import Commands
from .cli.error import ExitError
from .gui import Frame
from pathlib import Path
import argparse
import atexit
import code
import locale
import readline
import shlex
import wx

histfile = Path.home() / '.pycharsheet_history'

def main():
    parser = argparse.ArgumentParser(description='Run a character sheet command line')
    parser.add_argument('-V', '--version', action='version', version=str(_meta.version))
    parser.add_argument('-w', '--wxwidgets', help='Run a GUI instead of a CLI', action='store_true')
    args = parser.parse_args()
    if args.wxwidgets:
        gui()
    else:
        cli()

def cli():
    try:
        readline.read_history_file(histfile)
    except FileNotFoundError:
        pass
    readline.set_history_length(1000)

    atexit.register(readline.write_history_file, histfile)

    console = code.InteractiveConsole()
    commands = Commands()

    try:
        while True:
            lexer = shlex.shlex(console.raw_input(prompt='> '), punctuation_chars=True)
            tokens = list(lexer)
            try:
                retval = getattr(commands, tokens[0])(*tokens[1:])
            except AttributeError:
                print(f'ERROR: No known command: {tokens[0]}')
    except (EOFError, ExitError):
        pass

def gui():
    app = wx.App()
    frame = Frame(None, title=f'pycharsheet version {_meta.version}')
    frame.Show()
    app.MainLoop()

if __name__ == '__main__':
    locale.setlocale(locale.LC_ALL, '')
    main()
