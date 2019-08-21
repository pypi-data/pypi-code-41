import functools


def register(cli, func, *args, **kwargs):
    """Register a function for a command line interface.

    Args:
        cli: Command line interface for which we register the function.
        func: Function that we register.
        args, kwargs: Optional positional and keyword arguments that will be
            passed to the function when invoked.
    """
    name = func.__name__
    if len(args) > 0 or len(kwargs) > 0:
        callback = functools.wraps(func)(
            functools.partial(func, *args, **kwargs)
        )
    else:
        callback = func
    return cli.command(name)(callback)
