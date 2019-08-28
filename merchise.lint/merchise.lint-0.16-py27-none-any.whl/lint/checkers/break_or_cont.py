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


class BreakContinueVisitor(ast.NodeVisitor):
    def __init__(self):
        self.breaks = []
        self.continues = []

    def visit_Break(self, node):
        self.breaks.append((node.lineno, node.col_offset))

    def visit_Continue(self, node):
        self.continues.append((node.lineno, node.col_offset))


class BreakContinueCheck(object):
    name = 'break-or-continue'
    code = 'C990'
    msg = "C990 Using break or continue"
    uses_break = "C990 Using 'break'"
    uses_continue = "C990 Using 'continue'"
    version = "1.0"
    off_by_default = False

    def __init__(self, tree, filename=None):
        self.tree = tree
        self.filename = filename

    def run(self):
        fname = os.path.basename(self.filename) if self.filename else None
        if fname and not fname.startswith('__'):
            visitor = BreakContinueVisitor()
            visitor.visit(self.tree)
            for line, col in visitor.breaks:
                yield line, col, self.uses_break, type(self)
            for line, col in visitor.continues:
                yield line, col, self.uses_continue, type(self)
