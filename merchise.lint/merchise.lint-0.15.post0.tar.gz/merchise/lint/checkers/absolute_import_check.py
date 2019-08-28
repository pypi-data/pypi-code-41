from __future__ import absolute_import

import os
import ast
import sys


class ImportVisitor(ast.NodeVisitor):
    def __init__(self):
        self.has_import = False

    def visit_ImportFrom(self, node):
        if self.has_import:
            return
        if node.module != '__future__':
            return
        for nameproxy in node.names:
            if nameproxy.name != 'absolute_import':
                continue
            self.has_import = True
            break


class AbsoluteImportCheck(object):
    name = 'absolute-import'
    code = 'C901'
    msg = "C901 Missing `from __future__ import absolute_import`"
    version = "1.0"
    off_by_default = False

    def __init__(self, tree, filename=None):
        self.tree = tree
        self.filename = filename

    def run(self):
        if sys.version_info >= (3, ):
            return
        fname = os.path.basename(self.filename) if self.filename else None
        if fname and not fname.startswith('__'):
            visitor = ImportVisitor()
            visitor.visit(self.tree)
            if not visitor.has_import:
                yield 0, 0, self.msg, type(self)
