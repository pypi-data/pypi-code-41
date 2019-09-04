import time
import traceback
from sys import stderr
from functools import wraps


def try_to(f, *args, **kwargs):
    try:
        return f(*args, **kwargs)
    except Exception as e:
        return e


def try_or_none(f, *args, **kwargs):
    try:
        return f(*args, **kwargs)
    except:
        return


def retry(retries=3, delay=0, backoff=2, exceptions=Exception):
    """Retry function decorator.
    you can also put in delay and backoff to wait between retries
    and define to which exception you want to retry.
    :param retries: number of times to try (not retry) before giving up
    :param delay: initial delay between retries in seconds
    :param backoff: backoff multiplier e.g. value of 2 will double the delay each retry
    :param exceptions: the exception to check. may be a tuple of exceptions to check
    :type retries: int
    :type delay: int
    :type backoff: int
    :type exceptions: Exception or tuple
    """
    def decorator(f):
        @wraps(f)
        def wrapper(*args, **kwargs):
            wait = delay
            for i in range(retries):
                try:
                    return f(*args, **kwargs)
                except exceptions:
                    stderr.write("\nERROR running {}\n{}\nRetries left {}\n".format(f.__name__, traceback.format_exc(), retries-i))
                    time.sleep(wait)
                    wait *= backoff
            return f(*args, **kwargs)
        return wrapper
    return decorator
