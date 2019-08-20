
def _validate_iterable(iterable):
    """Return the argument if it is iterable, ``TypeError`` otherwise"""
    try:
        iter(iterable)
    except TypeError as e:
        raise TypeError("Argument is not iterable : %s" % repr(e))
    return iterable


def _build_iterable(iterable):
    iterable = [] if iterable is None else iterable
    if isinstance(iterable, float) or isinstance(iterable, int):
        iterable = range(int(iterable))
    return _validate_iterable(iterable)
