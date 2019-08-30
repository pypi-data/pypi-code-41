from __future__ import absolute_import

import collections
import functools
import inspect
import time
import types

from .decorated import Decorated


def decorator(func):
    """
    Glossy Decorator

    This decorator can be used to make your decorators glossy.
    It simplifies the creation of decorators by flattening their
    structure and reducing the number of wrapper functions required.
    It also adds some additional attributes to both the wrapped and
    the wrapper objects. This makes the code more discoverable and
    makes it possible for glossy to provide mocking capabilities.
    """

    # Create glossy metadata.
    stack = inspect.stack()
    meta = _get_meta(func, stack)

    # Add glossy attribute so we can determine if a decorator is "glossy".
    _add_attr(meta["decorator"], "__glossy__", True)

    @functools.wraps(func)
    def outer(*args, **kwargs):

        wrapped = args[0]
        wrapped = getattr(wrapped, "__wrapped__", wrapped)

        # Add glossy attributes
        _add_attr(wrapped, "__wrappers__", [])
        wrapped.__wrappers__.append(meta)

        caller = functools.partial(func, *args, **kwargs)
        caller = functools.update_wrapper(caller, args[0])

        decorated = Decorated(caller)
        decorated = functools.update_wrapper(decorated, args[0])
        decorated.__wrapped__ = wrapped
        decorated.__wrappers__ = wrapped.__wrappers__

        return decorated

    return outer


def _add_attr(wrapped, attr, default=None):
    if not hasattr(wrapped, attr):
        setattr(wrapped, attr, default)


def _get_meta(func, stack):
    """
    Get metadata

    Inspect the outer frame to see if the decorator accepts
    arguments. If so, the decorator has an outer layer and this
    is the one we want to use as a reference.
    """
    # Use the call stack to inspect the outer frame. If the outer
    # frame is scoped at a function level, assume the decorator has
    # an outer layer which accepts arguments.

    # NOTE: There is an important assumption here - we expect all
    # decorators to be defined at the module level.

    scope = stack[1]
    frame = scope.frame
    outer = frame.f_globals.get(scope.function)
    func.__decorator__ = outer

    if outer:
        variables = stack[1].frame.f_locals
        parameters = _get_decorator_parameters(outer, variables)
        meta = {"decorator": outer, "parameters": parameters}
    else:
        meta = {"decorator": func, "parameters": None}

    return meta


def _get_decorator_parameters(obj, locals_):
    """
    Get the parameters used during function decoration.

    Args:
        obj (callable): Decorator object
        locals (dict): The local variables from the decorator frame.
    """
    # Get the function siganture and parameters.
    signature = inspect.signature(obj)
    parameters = signature.parameters.values()

    # Determine the arguments passed to the decorator.
    keys = [p.name for p in parameters if p.default == inspect._empty]
    args = [locals_[key] for key in keys]

    # Determine keyword arguments passed to the decorator.
    keys = [p.name for p in parameters if p.default != inspect._empty]
    kwargs = collections.OrderedDict()
    for key in keys:
        kwargs[key] = locals_[key]

    return args, kwargs
