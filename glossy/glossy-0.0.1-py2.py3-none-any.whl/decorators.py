from __future__ import absolute_import

import collections
import functools
import inspect
import time
import types


Meta = collections.namedtuple("Meta", ["layers"])
Layer = collections.namedtuple("Layer", ["obj", "parameters"])


class Target:
    """
    """

    def __init__(self, func, *args, **kwargs):
        self._func = func
        self._args = args
        self._kwargs = kwargs

        # Functools attributes
        self.__wrapped__ = None

        # Glossy attributes
        self.__wrappers__ = []

    @property
    def func(self):
        return self._func

    # @property
    # def args(self):
    #     return self._args

    # @property
    # def kwargs(self):
    #     return self._kwargs

    @property
    def mocked(self):
        return self._mocked

    def mock(self, decorator):
        for meta in self.__wrappers__:
            decorator_ = meta["decorator"]
            if decorator_.__name__ == decorator.__name__:
                print(">>> match: ", decorator_, decorator)
                self._mocked.append(decorator_)

    def __getattr__(self, attr):
        return getattr(self.func, attr)

    def __call__(self, *args, **kwargs):
        decorator = getattr(self.func.func, "__decorator__", None) or self.func.func
        print(">", decorator, self._mocked)

        # If we're in testing mode, check if the decorator has been
        # mocked. If it has, then bypass the decorator logic by
        # calling the wrapped function directly.
        if mode == Modes.Testing:
            if self._is_mocked(decorator):
                result = self.func.__wrapped__(*args, **kwargs)
                return result

        result = self.func(*args, **kwargs)
        return result


        for wrapper in self.__wrappers__:
            decorator_ = wrapper["decorator"]
            if decorator_.__name__ == decorator.__name__:
                parameters = decorator["parameters"]

                if is_mocked(, wrapper[])

        if decorator in self._mocked:
            print("> Running decorator (mocked)", decorator)
            result = self.func.__wrapped__(*args, **kwargs)
            return result
        else:
            print(
                f"> Running {self.func} (name={self.func.__name__}, decorator={decorator.__name__})"
            )
            result = self.func(*args, **kwargs)
            return result


def decorator(func):
    """
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
        target = Target(caller)

        target.__wrapped__ = wrapped
        target.__wrappers__ = wrapped.__wrappers__

        return target

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
        parameters = _get_parameters(wrapper, variables)
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


@decorator
def timer(func, *args, **kwargs):
    """
    Timer

    This decorator function is used to time the given
    function execution.
    """
    start = time.time()
    result = func(*args, **kwargs)
    duration = time.time() - start
    print(f"Function {func.__name__} took {duration} seconds")
    return result


def timeout(limit=5):
    """
    Timeout

    This decorator is used to raise a timeout error when the
    given function exceeds the given timeout limit.
    """

    @decorator
    def _timeout(func, *args, **kwargs):
        start = time.time()
        result = func(*args, **kwargs)
        duration = time.time() - start
        if duration > limit:
            msg = f"Function {func.__name__} exceeded timeout limit ({limit} seconds)"
            raise TimeoutError(msg)

        print("> duration:", duration)
        return result

    return _timeout


def test(func):
    @functools.wraps(func)
    def wrapper(*args, **kwargs):
        return func(*args, **kwargs)

    return wrapper


@test
def wibble(seconds):
    time.sleep(seconds)


# @timeout(limit=1)
@timer
@timeout(limit=1)
def foo(seconds):
    time.sleep(seconds)


# gloss.mock(foo, "@timer")
foo.mock(timeout)
foo(0.9)
print(foo)
print("> Name", foo.__name__)
print("> Wrapped: ", foo.__wrapped__)
print("> Wrappers: ", foo.__wrappers__)

print("----")

# - timer
#   - timeout._timeout
#     foo


# @timeout(1)
# def bar(seconds):
#     time.sleep(seconds)


# bar(1.1)
