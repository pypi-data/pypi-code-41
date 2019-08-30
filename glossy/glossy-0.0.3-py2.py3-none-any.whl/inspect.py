import inspect

PREFIX = "@"


class Inspection:
    """
    Glossy Inspection

    This class represents an inspected item. If the inspected
    item is a glossy item, then it can be used to discover
    information about the associated decorators (if there are any).
    """

    def __init__(self, obj):
        """
        """
        self._obj = obj
        self._decorators = []

    @property
    def glossy(self):
        """
        Get glossy status.

        bool: True if the inspected object is glossy, false otherwise.
        """
        return is_glossy(self._obj)

    @property
    def decorators(self):
        """
        Get decorators

        list of Decorator: Decorators
        """
        if not self._decorators and self.glossy:
            for meta in getattr(self._obj, "__wrappers__", []):
                decorator = Decorator(meta)
                self._decorators.append(decorator)

        return self._decorators

    def is_decorated(self):
        """
        Check for decorators

        bool: True if decorated, false otherwise.
        """
        return bool(self.decorators)

    def is_decorated_by(self, decorator, *args, **kwargs):
        """
        Check for the given decorator

        Check if the inspected item has the given
        decorator. If additional arguments and/or keyword
        arguments were given, check if the decorator was
        created with these values.
        """
        for decorator_ in self.decorators:
            if decorator.__name__ == decorator.__name__:
                match_args = not args or args == decorator_.args
                match_kwargs = not kwargs or kwargs == dict(decorator_.kwargs)
                if match_args and match_kwargs:
                    return True

        return False


class Decorator:
    """
    Decorator Specification

    This class represents a glossy decorator.
    """

    def __init__(self, meta):
        self._meta = meta

    @property
    def parameters(self):
        """
        Get parameters (args and kwargs)

        tuple or None: Parameters
        """
        return self._meta.get("parameters")

    @property
    def args(self):
        """
        Get position arguments.

        list or None: Positional arguments
        """
        return self.parameters[0] if self.parameters else None

    @property
    def kwargs(self):
        """
        Get keyword arguments.

        collections.OrderedDict or None: Keyword arguments
        """
        return self.parameters[1] if self.parameters else None


def inspect(obj):
    """
    Inspect the given object.

    Args:
        obj (callable): Some decorated function or class.
    """
    return Inspection(obj)


def is_glossy(obj):
    """
    Check if the given callable is glossy.

    Args:
        obj (callable): A function or class.

    Returns:
        bool: True if the object is glossy, false otherwise
    """
    return hasattr(obj, "__wrappers__") or hasattr(obj, "__glossy__")


def get_decorators(func):
    """
    Get function decorators.

    Args:
        func (function): Function object.

    Returns:
        list of callable: Function decorators.
    """
    decorators = []
    module = inspect.getmodule(func)
    lines = inspect.getsourcelines(func)[0]
    matches = (line for line in lines if line.startswith(PREFIX))
    for match in matches:
        name = match.split("(")[0].replace(PREFIX, "").strip()
        decorator = getattr(module, name, None)
        if decorator:
            decorators.append(decorator)

    return decorators


def get_decorator(func, name):
    """
    Get function decorator.

    Args:
        func (function): Function object.
        name (str): Decorator name.

    Returns:
        callable: Function decorator.
    """
    match = None

    clean_name = name.replace(PREFIX, "")

    decorators = get_decorators(func)
    for decorator in decorators:
        if decorator.__name__ == clean_name:
            match = decorator
            break

    return match


def is_decorated(func):
    """
    Check if the given function is decorated.

    Args:
        func (function): Function object.

    Returns:
        bool: True if the function is decorated, false otherwise.
    """
    return bool(get_decorators(func))


def has_decorator(func, decorator):
    """
    Check if the given function has the given decorator.

    Args:
        func (function): Function object.
        decorator (function): Decorator

    Returns:
        bool: True if the function has the decorator, false otherwise.
    """
    match = False
    decorators = get_decorators(func)
    for decorator_ in decorators:
        if decorator == decorator_:
            match = True
            break

    return match


def has_decorators(func, decorators):
    """
    Check if the given function has the given decorators.

    Args:
        func (function): Function
        decorators (list of function): Decorators

    Returns:
        bool: True if the function has the decorators, false otherwise.
    """
    return all([has_decorator(func, d) for d in decorators])
