from __future__ import division

import ast
import _ast

try:
    # Python 3+
    NameConstant = _ast.NameConstant
except AttributeError:
    # Python 2.7
    NameConstant = _ast.Name


class NotSafeExpression(Exception):
    pass


class UnsafeNode(Exception):
    pass


class Evaler(object):
    ALLOWED_NODES = {
        _ast.Module,
        # math
        _ast.Add,
        _ast.UAdd,
        _ast.Sub,
        _ast.USub,
        _ast.Mult,
        _ast.Div,
        _ast.FloorDiv,
        _ast.Pow,
        _ast.Mod,
        # binary math
        _ast.LShift,
        _ast.RShift,
        _ast.BitAnd,
        _ast.BitOr,
        _ast.BitXor,
        _ast.Invert,
        # conditions
        _ast.Not,
        _ast.IfExp,
        # base expressions
        _ast.Expr,
        _ast.BinOp,
        _ast.UnaryOp,
        # comparisons
        _ast.Compare,
        _ast.Eq,
        _ast.NotEq,
        _ast.Lt,
        _ast.LtE,
        _ast.Gt,
        _ast.GtE,
        _ast.Is,
        _ast.IsNot,
        _ast.In,
        _ast.NotIn,
        # structures
        _ast.Tuple,
        _ast.List,
        _ast.Dict,
        # system
        _ast.Num,
        _ast.Str,
        _ast.Name,
        NameConstant,  # True, False, None in Python 3+
        _ast.Load,
        _ast.Call,  # visit_Call makes the rest
    }

    def __init__(self, safe_funcs=None):
        if safe_funcs is None:
            safe_funcs = []

        # to preserve ordering. OrderedDict is overkill here, I think
        self.safe_func_names = [func.__name__ for func in safe_funcs]
        self.checker = Evaler.IsExprSafe(self)

        self.safe_funcs = {func.__name__: func for func in safe_funcs}

        self.boolean_builtins = {"True": True, "False": False}

    def eval(self, expr, variables=None):
        unsafe = self.expr_is_unsafe(expr)

        if not unsafe:
            return self.raw_eval(expr, variables)
        else:
            raise NotSafeExpression(expr, unsafe)

    def __str__(self):
        return "Evaler([%s])" % ", ".join(self.safe_func_names)

    def get_allowed_nodes(self):
        return self.ALLOWED_NODES

    def expr_is_unsafe(self, expr):
        ast_tree = ast.parse(expr)

        try:
            self.checker.visit(ast_tree)
            return None
        except UnsafeNode as e:
            return e

    def raw_eval(self, expr, variables=None):
        locals = dict(self.boolean_builtins)
        if variables is not None:
            locals.update(variables)

        return eval(expr, {'__builtins__': self.safe_funcs}, locals)

    class IsExprSafe(ast.NodeVisitor):
        def __init__(self, evaler):
            self.evaler = evaler
            self.safe_func_names = set(evaler.safe_func_names)

            ast.NodeVisitor.__init__(self)

        def visit_Module(self, node):
            self.generic_visit(node)
            return True

        def visit_Call(self, node):
            func = node.func

            if "id" in func.__dict__:
                if func.id not in self.safe_func_names:
                    raise UnsafeNode(ast.dump(node))
            else:
                raise UnsafeNode(ast.dump(node))

            self.generic_visit(node)

        def visit_Compare(self, node):
            operands = node.comparators + [node.left]

            for op in operands:
                self.generic_visit(op)

        def visit_BoolOp(self, node):
            for val in node.values:
                self.generic_visit(val)

        def generic_visit(self, node):
            if type(node) not in self.evaler.get_allowed_nodes():
                raise UnsafeNode(ast.dump(node))
            ast.NodeVisitor.generic_visit(self, node)
