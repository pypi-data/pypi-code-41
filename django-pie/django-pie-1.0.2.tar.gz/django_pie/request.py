# coding: utf-8
import json


class RequestException(Exception):
    pass


def request_get(request, key, key_type=None, required=True, choices=None, min_value=None, max_value=None):
    value = request.GET.get(key)
    return _request(value, key_type, required, choices, min_value, max_value)


def request_post(request, key, key_type=None, required=True, choices=None, min_value=None, max_value=None):
    value = request.POST.get(key)
    return _request(value, key_type, required, choices, min_value, max_value)


def request_headers(request, key, key_type=None, required=True, choices=None, min_value=None, max_value=None):
    value = request.headers.get(key)
    return _request(value, key_type, required, choices, min_value, max_value)


def request_data(request, key, key_type=None, required=True, choices=None, min_value=None, max_value=None):
    if not hasattr(request, 'data'):
        try:
            data = json.loads(request.body)
            setattr(request, 'data', data)
        except Exception:
            raise RequestException
    value = request.data.get(key)
    return _request(value, key_type, required, choices, min_value, max_value)


def _request(value, key_type, required, choices, min_value, max_value):
    if required and value is None:
        raise RequestException
    if key_type is not None:
        try:
            value = key_type(value)
        except Exception:
            raise RequestException
    if choices is not None and value not in choices:
        raise RequestException
    if min_value is not None and value < min_value:
        raise RequestException
    if max_value is not None and value > max_value:
        raise RequestException

    return value
