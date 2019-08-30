import inspect
import types
from unittest.mock import ANY

# This variable is used in testing mode only. It acts as a
# registry for all mocked decorators.
_mocks = {}


def clear_mocks():
    global _mocks
    _mocks = {}


class Decorated:
    """
    Decorated

    This class represents a wrapped (or decorated) function/class.
    To the user it should appear like the wrapped object. It simply
    adds some additional logic when called.
    """

    def __init__(self, func, *args, **kwargs):
        self._func = func
        self._args = args
        self._kwargs = kwargs

        # Functools attributes
        self.__wrapped__ = None

        # Glossy attributes
        self.__wrappers__ = []

    def __repr__(self):
        return f"<glossy.Decorated({self._func.__name__}) at {hex(id(self))}>"

    def __getattr__(self, attr):
        """
        Get attribute

        This method overrides the base class method. It is called
        whenever python can't find an attribute on an object. In this
        case, we'll look for the attribute on the function we're
        wrapping. From a user perspective, this make the class appear
        like the wrapped function which is what we want.
        """
        return getattr(self._func, attr)

    @property
    def wrapped(self):
        """
        Get wrapped object

        callable: Wrapped function/class.
        """
        wrapped = self._func
        while hasattr(wrapped, "__wrapped__"):
            wrapped = wrapped.__wrapped__

        return wrapped

    @property
    def decorators(self):
        """
        Get decorators

        list or callable: Decorators
        """
        return [item["decorator"] for item in self.__wrappers__]

    def is_decorated_by(self, decorator, *args, **kwargs):
        """
        Check if the given decorator exists
        """
        status = False

        # Check if the given decorator matches any of the
        # current decorations.
        info = self.get_decorator_info(decorator)

        if info:
            status = True

            # If arguments and/or keyword arguments were given,
            # check if they match the information  we found.
            if args != () and args != info["args"]:
                status = False

            if kwargs != {} and kwargs != dict(info["kwargs"]):
                status = False

        return status

    def get_decorator_info(self, decorator):
        """
        Get information about the given decorator
        """
        for item in self.__wrappers__:
            current_decorator = item["decorator"]
            if match_decorators(decorator, current_decorator):
                args, kwargs = item.get("parameters") or (None, None)
                return {
                    "obj": current_decorator,
                    "name": current_decorator.__name__,
                    "args": args,
                    "kwargs": kwargs,
                }

    @property
    def _decorator(self):
        """
        Get decorator

        callable: Decorator
        """
        obj = getattr(self._func.func, "__decorator__", None) or self._func.func
        return obj

    @property
    def _mocked_decorators(self):
        """
        Get mocked decorators
        """
        global _mocks

        key = id(self.wrapped)
        return _mocks.get(key, [])

    def mock_decorator(self, decorator, *args, **kwargs):
        """
        Mock the given decorator

        If no arguments or keyword arguments are given, the
        decorator will be mocked for ANY arguments and/or
        keyword arguments.
        """
        global _mocks

        # Throw error when the decorated object doesn't have the
        # given decorator.
        if not self.is_decorated_by(decorator, *args, **kwargs):
            info = self.get_decorator_info(decorator)
            if not info:
                name = decorator.__name__
                wrapped_name = self.wrapped.__name__
                msg = f"Object {wrapped_name} has no decorator: {name}"
                raise ValueError(msg)
            else:
                return

        key = id(self.wrapped)
        _mocks.setdefault(key, [])
        _mocks[key].append((decorator, args or ANY, kwargs or ANY))

    def is_decorator_mocked(self, decorator, *args, **kwargs):
        """
        Check if the given decorator has been mocked.
        """
        for mocked_decorator, mocked_args, mocked_kwargs in self._mocked_decorators:
            if match_decorators(decorator, mocked_decorator):
                matched_args = mocked_args in (args, ANY)
                matched_kwargs = mocked_kwargs in (kwargs, ANY)
                if matched_args and matched_kwargs:
                    return True

        return False

    def __call__(self, *args, **kwargs):
        """
        Call the decorated function with the given parameters.
        """
        if self.is_decorator_mocked(self._decorator, *args, **kwargs):
            result = self._func.__wrapped__(*args, **kwargs)
            return result

        result = self._func(*args, **kwargs)
        return result


def match_decorators(decorator1, decorator2):
    """
    Match decorators

    This function checks if the import paths for the
    decorators are the same.
    """
    path1 = get_decorator_path(decorator1)
    path2 = get_decorator_path(decorator2)
    return path1 == path2


def get_decorator_path(decorator):
    """
    Get the import path for the given decorator
    """
    mod = inspect.getmodule(decorator)
    return f"{mod.__name__}.{decorator.__name__}"
