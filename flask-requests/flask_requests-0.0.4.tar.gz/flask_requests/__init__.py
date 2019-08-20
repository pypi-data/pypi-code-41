from operator import ne
from typing import Tuple, Any, Optional
from urllib.parse import urlparse

from flask import request


def _parse_url_query(url, *keys: str) -> Optional[Tuple]:
    parsed = urlparse(url)
    if parsed.query:
        parameter_iter = map(lambda x: x.split('='), parsed.query.split('&'))
        contained_keys = filter(lambda x: lambda x: len(x) == 2 and x[0] in keys, parameter_iter)
        return tuple(map(lambda x: x[1], contained_keys))
    return ('',)


def get_data(*keys: str, data_source: request = request) -> Tuple[Any, ...]:
    """
    1. if mimetype is 'application/x-www-form-urlencoded', front end html example:
        action: request url
        name: name is necessary, name is ImmutableMultiDict item key
        <form role="form" action="/download-file/"
                  target="_self"
                  accept-charset="UTF-8"
                  method="POST"
                  autocomplete="off"
                  enctype="application/x-www-form-urlencoded">
            <textarea name="comment"></textarea>
            <input ..../>
        </form>

    2. support get data from url, such as http://0.0.0.0:8889/companies&token=xxxx
    get_data('token') -> 'xxxx'
    :return:
    """
    match_mimetype = {
        'application/x-www-form-urlencoded': lambda: tuple(data_source.form.get(key, '') for key in keys),
        'application/json': lambda: tuple(data_source.json.get(i, '') for i in keys),
    }
    implemented_method = {
        'POST': lambda: match_mimetype.get(request.mimetype, lambda x: x),
        'GET': lambda: _parse_url_query(request.full_path, *keys)
    }
    method_func = implemented_method.get(request.method)
    if not method_func:
        raise NotImplementedError(f'method {request.method} not support')
    matched = method_func()
    if not matched or ne(*map(len, (matched, keys))):
        raise ValueError(f'keys {keys} and matched {matched} length not match')
    return matched


if __name__ == '__main__':
    s = _parse_url_query('http://0.0.0.0:8889/companies?token=xxxxxxx', 'token')
    print(s)
