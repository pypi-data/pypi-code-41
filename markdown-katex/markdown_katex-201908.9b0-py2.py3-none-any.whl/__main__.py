#!/usr/bin/env python
# -*- coding: utf-8 -*-
# This file is part of the markdown-katex project
# https://gitlab.com/mbarkhau/markdown-katex
#
# Copyright (c) 2019 Manuel Barkhau (mbarkhau@gmail.com) - MIT License
# SPDX-License-Identifier: MIT
from __future__ import absolute_import
from __future__ import division
from __future__ import print_function
from __future__ import unicode_literals
import os
import sys
import json
import typing as typ
import subprocess as sp
try:
    import builtins
except ImportError:
    import __builtin__ as builtins
import markdown_katex
str = getattr(builtins, 'unicode', str)
if os.environ.get('ENABLE_BACKTRACE') == '1':
    import backtrace
    backtrace.hook(align=True, strip_path=True, enable_on_envvar_only=True)
HTML_TEMPLATE = """
<!DOCTYPE html>
<html>
<head>
  <title>Test Katex</title>
  <link rel="stylesheet"
    href="https://cdn.jsdelivr.net/npm/katex@0.10.2/dist/katex.css"
    integrity="sha256-SSjvSe9BDSZMUczwnbB1ywCyIk2XaNly9nn6yRm6WJo="
    crossorigin="anonymous">
  <style type="text/css">
    body{background: white; }
  </style>
</head>
<body>
Generated with markdown-katex
<hr/>
{{content}}
</body>
</html>
"""
ExitCode = int


def _selftest():
    import markdown_katex.wrapper as wrp
    print('Command options:')
    print(json.dumps(wrp.parse_options(), indent=4))
    print()
    html_parts = []
    test_formulas = markdown_katex.TEST_FORMULAS
    for tex_formula in test_formulas:
        html_part = wrp.tex2html(tex_formula)
        if not html_part:
            return 1
        html_parts.append(html_part)
    formula_html = '\n<hr/>\n'.join(html_parts)
    html_text = HTML_TEMPLATE.replace('{{content}}', formula_html)
    with open('test.html', mode='wb') as fh:
        fh.write(html_text.encode('utf-8'))
    print("Created 'test.html'")
    return 0


def main(args=sys.argv[1:]):
    """Basic wrapper around the svgbob command.

    This is mostly just used for self testing.
    """
    if '--markdown-katex-selftest' in args:
        return _selftest()
    if '--version' in args or '-V' in args:
        version = markdown_katex.__version__
        print('markdown-katex version: ', version)
    binpath = markdown_katex.get_bin_path()
    return sp.call([str(binpath)] + args)


if __name__ == '__main__':
    sys.exit(main())
