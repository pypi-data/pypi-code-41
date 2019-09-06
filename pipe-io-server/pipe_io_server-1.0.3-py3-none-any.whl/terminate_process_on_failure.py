from functools import wraps
from os import kill, getpid
from signal import SIGTERM
from traceback import print_exc


def terminate_process_on_failure(fun):
    @wraps(fun)
    def wrapper(*args, **kwargs):
        try:
            return fun(*args, **kwargs)
        except:  # pylint: disable=bare-except
            print_exc()
            kill(getpid(), SIGTERM)
    return wrapper
