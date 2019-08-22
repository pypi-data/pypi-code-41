import os
import sys
import jsonschema
from functools import wraps

from requests.auth import HTTPBasicAuth


def graceful_error(func):
    @wraps(func)
    def wrapper(*args, **kwargs):
        try:
            return func(*args, **kwargs)

        except jsonschema.exceptions.ValidationError as e:
            if hasattr(e, 'context'):
                print('{}:{}Context: {}'.format(repr(e), os.linesep, e.context), file=sys.stderr)
                exit(1)

            print(repr(e), file=sys.stderr)
            exit(2)

        except Exception as e:
            print('{}:{}{}'.format(repr(e), os.linesep, e), file=sys.stderr)
            exit(3)

    return wrapper


def auth_method_obj(access):
    if not access.get('auth'):
        return None

    auth = access['auth']

    return HTTPBasicAuth(
        auth['username'],
        auth['password']
    )
