#!/usr/bin/env python3
# -*- coding: utf-8 -*-
# Copyright © 2019 Taylor C. Richberger
# This code is released under the license described in the LICENSE file

import sys
from pygments import highlight, lexers, formatters

color_options = (
    'auto',
    'yes',
    'no',
    '256color',
    'truecolor',
)

lexers = {
    'json': lexers.JsonLexer,
    'yaml': lexers.YamlLexer,
    'xml': lexers.XmlLexer,
    'python': lexers.PythonLexer,
}

# From django, see license
def supports_color(output):
    """
    Return True if the running system's terminal supports color,
    and False otherwise.
    """
    plat = sys.platform
    supported_platform = plat != 'Pocket PC' and (plat != 'win32' or 'ANSICON' in os.environ)

    # isatty is not always implemented, #6223.
    is_a_tty = hasattr(output, 'isatty') and output.isatty()
    return supported_platform and is_a_tty

def get_colorizer(format, color, output):
    '''Get a colorizer function for a format if possible'''
    try:
        if color in {'yes', '256color', 'truecolor'} or color == 'auto' and supports_color(output):
            lexer = lexers[format]()
            if color == '256color':
                formatter = formatters.Terminal256Formatter()
            elif color == 'truecolor':
                formatter = formatters.TerminalTrueColorFormatter()
            else:
                formatter = formatters.TerminalFormatter()

            def colorize(code):
                return highlight(code, lexer, formatter)

            return colorize
    except KeyError:
        pass

    return lambda value: value
