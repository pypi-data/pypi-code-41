import types

from .inspect import get_decorator

_mocks = {}


def mock(func, decorator, *args, **kwargs):
    """
    Mock decorator

    Args:
        func (function): Function with decorator(s) on it.
        name (str): The name of a decorator on the function.
        *args: Position arguments for the decorator.
        **kwargs: Keyword argeuments for the decorator.
    """
    global _mocks

    if isinstance(decorator, str):
        decorator = get_decorator(func, decorator)

    name = decorator.__name__
    if not decorator:
        msg = f"Object {func.__name__} has no decorator: {name}"
        raise ValueError(msg)

    key = id(func)
    _mocks.setdefault(key, [])
    _mocks[func].append((decorator, args or None, kwargs or None))


def is_mocked(func, decorator, *args, **kwargs):
    """
    Check if a decorator has been mocked.

    Args:
        func (function): Function with decorator(s) on it.
        name (str): The name of a decorator on the function.
        *args: Position arguments for the decorator.
        **kwargs: Keyword argeuments for the decorator.
    """
    key = id(func)
    mocks = _mocks.get(key, [])
    for mocked in mocks:
        if mocked == (decorator, args or None, kwargs or None):
            return True

    return False


def unmock(func, decorator, *args, **kwargs):
    """
    Unmock decorator on function.

    Args:
        func (function): Function with decorator(s) on it.
        name (str): The name of a decorator on the function.
    """
    global _mocks

    if is_mocked(func, decorator, *args, **kwargs):
        _mocks[id(func)].remove((decorator, args or None, kwargs or None))
