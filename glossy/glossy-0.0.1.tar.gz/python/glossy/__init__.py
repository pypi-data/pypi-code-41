from __future__ import absolute_import

from . import inspect
from .inspect import (
    get_decorator,
    get_decorators,
    has_decorator,
    has_decorators,
    is_decorated,
)


# PREFIX = "@"


# def glitz():
#     """
#     """

#     def outer(func):

#         frame = inspect.currentframe()
#         decorator = inspect.getframeinfo(frame).function

#         @functools.wraps(func)
#         def inner(*args, **kwargs):
#             return func(*args, **kwargs)

#         return inner

#     return outer


# def _add_decorator(func, decorator):
#     """
#     """
#     _add_decorators_attribute(func)
#     func.__decorators__.append(decorator)


# def _add_decorators_attribute(func):
#     """
#     """
#     attr = "__decorators__"
#     if not hasattr(func, attr):
#         setattr(func, attr, [])


# def one():
#     def outer(func):
#         @functools.wraps(func)
#         def inner(*args, **kwargs):
#             return func(*args, **kwargs)

#         return inner

#     return outer


# def two(func):
#     @functools.wraps(func)
#     def inner(*args, **kwargs):
#         return func(*args, **kwargs)

#     return inner


# @one()
# @two
# def foo():
#     return "bar"


# def get_current_module():
#     """
#     Get current module

#     Returns:
#         module: Current module.
#     """
#     return sys.modules[__name__]


# def is_decorated(func):
#     """
#     """
#     pass


# import ast

# source = inspect.getsource(foo)
# print(source)
# tree = ast.parse(source)
# print(tree)
# print(ast.dump(tree))
# print("---")

# for node in ast.walk(tree):
#     if isinstance(node, ast.FunctionDef):
#         decorators = [d for d in node.decorator_list]
#         print(node.name, decorators)

# for d in decorators:
#     print(">", d, d.__dict__)

# print(get_decorators(foo))
