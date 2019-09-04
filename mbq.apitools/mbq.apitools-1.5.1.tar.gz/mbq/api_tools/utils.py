def first(iterable, predicate=lambda x: True, default=None):
    return next((item for item in iterable if predicate(item)), default)


class Immutable:
    """Base immutable class for the query params."""

    _frozen = False

    def __init__(self, mutable=False, **kwargs):
        for kwarg_name, kwarg_value in kwargs.items():
            setattr(self, kwarg_name, kwarg_value)

        self._fields = kwargs
        self._frozen = not mutable

    def __setattr__(self, key, value):
        if self._is_immutable():
            raise TypeError(f"The instance of {self.__class__} is immutable.")
        super().__setattr__(key, value)

    def _is_immutable(self):
        return self._frozen

    def _set_immutable(self):
        """Set the instance as immutable."""
        self._frozen = False

    def as_dict(self):
        """Return the dictionary of items."""
        transformed = {}

        for key, value in self._fields.items():
            if isinstance(value, list):
                value = [
                    x.as_dict() if isinstance(x, self.__class__) else x for x in value
                ]
            elif isinstance(value, self.__class__):
                value = value.as_dict()

            transformed[key] = value

        return transformed
