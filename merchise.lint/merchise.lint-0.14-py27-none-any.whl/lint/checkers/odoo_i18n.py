#!/usr/bin/env python
# -*- coding: utf-8 -*-
# ---------------------------------------------------------------------
# Copyright (c) Merchise Autrement [~º/~] and Contributors
# All rights reserved.
#
# This is free software; you can do what the LICENCE file allows you to.
#
from __future__ import absolute_import

import os
import ast
import sys

try:
    from ast import JoinedStr
except ImportError:

    class JoinedStr:
        pass


class OdooI18NVisitor(ast.NodeVisitor):
    # I assume you import _ at the top level
    def __init__(self):
        self.import_odoo_gettext = False
        self.mangled_i18n = []

    def visit_ImportFrom(self, node):
        if self.import_odoo_gettext:
            return
        if node.module not in ("odoo", "xoeuf.odoo"):
            return
        self.import_odoo_gettext = any(name == "_" for name in node.names)

    def visit_Call(self, node):
        func = node.func
        if not self.import_odoo_gettext:
            self.generic_visit(node)
            return

        if isinstance(func, ast.Name) and func.id == "_":
            args = node.args
            if len(args) == 1:  # More than one args indicate a non-Odoo _
                arg = args[0]
                if isinstance(arg, JoinedStr):
                    self.mangled_i18n.append((node.lineno, node.col_offset))
        else:
            self.generic_visit(node)


class MangledI18NWithFStringsCheck(object):
    name = "fstring-in-i18n"
    code = "O001"
    msg = "O001 Using a f-string inside a call to Odoo's gettext"
    version = "1.0"
    off_by_default = True

    def __init__(self, tree, filename=None):
        self.tree = tree
        self.filename = filename

    def run(self):
        if sys.version_info < (3, 6):
            # f-strings were introduced in Python 3.6
            return
        fname = os.path.basename(self.filename) if self.filename else None
        if fname and not fname.startswith("__"):
            visitor = OdooI18NVisitor()
            visitor.visit(self.tree)
            for line, col in visitor.mangled_i18n:
                yield line, col, self.msg, type(self)
