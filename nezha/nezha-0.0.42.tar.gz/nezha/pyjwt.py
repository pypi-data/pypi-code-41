import operator as op
from collections.abc import Mapping
from datetime import datetime, timedelta
from functools import wraps
from typing import Callable, Optional, List, Dict

from jwt.api_jwt import PyJWT
from jwt.exceptions import ExpiredSignatureError
from nezha.ustring import to_str

# todo
def _encode(func: Callable):
    """
    :param func:
    :param lifetime: the period of validity for token. the unit of lifetime is second.
    :return:
    """

    @wraps(func)
    def wrap(self, *args, **kwargs):
        if len(args) < 0 or not isinstance(args[0], Mapping):
            raise TypeError('Expecting a mapping object, as JWT only supports JSON objects as payloads.')
        lifetime = kwargs.pop('lifetime', None)
        payload = args[0]
        if lifetime and isinstance(lifetime, int):
            payload['exp'] = op.add(datetime.utcnow(), timedelta(seconds=lifetime))
        return to_str(func(self, *args, **kwargs))

    return wrap

def is_expired(self, jwt: str, key: str, verify: bool = True, algorithms: Optional[List[str]] = None,
             options: Optional[Dict] = None, **kwargs):
    try:
        PyJWT().decode(jwt, key=key, verify=verify, algorithms=algorithms, options=options, **kwargs)
        return False
    except ExpiredSignatureError as e:
        return True


def is_valid(self, jwt: str, key: str, verify: bool = True, algorithms: Optional[List[str]] = None,
             options: Optional[Dict] = None, **kwargs):
    try:
        PyJWT().decode(jwt, key=key, verify=verify, algorithms=algorithms, options=options, **kwargs)
        return True
    except Exception as e:
        return False


PyJWT.is_valid = is_valid
PyJWT.encode = _encode(PyJWT.encode)
_jwt_global_obj = PyJWT()
encode = _jwt_global_obj.encode
