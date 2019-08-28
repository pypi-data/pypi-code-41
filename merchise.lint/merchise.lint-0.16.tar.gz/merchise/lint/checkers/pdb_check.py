#!/usr/bin/env python
# -*- coding: utf-8 -*-
# ---------------------------------------------------------------------
# Copyright (c) Merchise Autrement [~º/~] and Contributors
# All rights reserved.
#
# This is free software; you can do what the LICENCE file allows you to.
#

from __future__ import (division as _py3_division,
                        print_function as _py3_print,
                        absolute_import as _py3_abs_import)

import ast


class ImportVisitor(ast.NodeVisitor):
    def __init__(self):
        self.pdb = False
        self.pdb_node = None

    def visit_Import(self, node):
        if not self.pdb:
            self.pdb = any(alias.name in ('pdb', 'ipdb') for alias in node.names)
            if self.pdb:
                self.pdb_node = (node.lineno, node.col_offset)

    def visit_ImportFrom(self, node):
        if not self.pdb:
            self.pdb = node.module in ('pdb', 'ipdb')
            if self.pdb:
                self.pdb_node = (node.lineno, node.col_offset)


class AvoidPdb(object):
    name = 'avoid-pdb'
    code = 'C980'
    msg = "C980 Importing pdb or ipdb"
    version = "1.0"
    off_by_default = False

    def __init__(self, tree, filename=None):
        self.tree = tree

    def run(self):
        visitor = ImportVisitor()
        visitor.visit(self.tree)
        if visitor.pdb:
            yield visitor.pdb_node[0], visitor.pdb_node[1], self.msg, type(self)
