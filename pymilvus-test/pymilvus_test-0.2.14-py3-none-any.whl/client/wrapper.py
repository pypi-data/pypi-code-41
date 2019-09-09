from functools import wraps


# @deprecated
def deprecated(func):
    @wraps(func)
    def inner(*args, **kwargs):
        return func(*args, **kwargs)

    return inner
