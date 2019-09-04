import inspect

import pymq.typing

deep_from_dict = pymq.typing.deep_from_dict
deep_to_dict = pymq.typing.deep_to_dict
fullname = pymq.typing.fullname
isgeneric = pymq.typing.is_generic


def isderived(obj, parent):
    cls = obj if inspect.isclass(obj) else type(obj)
    return inspect.isclass(cls) and issubclass(cls, parent) and cls != parent


_json_type_map = {
    int: 'integer',
    float: 'number',
    str: 'string',
    bool: 'boolean',
    list: 'array',
    tuple: 'array',
    dict: 'object'
}


def json_schema(cls):
    if cls in (int, float, str, bool, list, tuple, dict):
        return {'type': _json_type_map[cls]}

    if isgeneric(cls):
        container_class = cls.__origin__

        if issubclass(container_class, list):
            return {'type': 'array', 'items': json_schema(cls.__args__[0])}

        if issubclass(container_class, set):
            return {'type': 'array', 'items': json_schema(cls.__args__[0]), 'uniqueItems': True}

        if issubclass(container_class, tuple):
            return {'type': 'array', 'items': [json_schema(arg) for arg in cls.__args__]}

        if issubclass(container_class, dict):
            key_type = cls.__args__[0]  # there are only string keys in JSON
            value_type = cls.__args__[1]
            return {
                'type': 'object',
                'additionalProperties': json_schema(value_type)
            }

        raise TypeError('Unknown generic class %s' % cls)

    if hasattr(cls, '__annotations__'):
        return {
            'type': 'object',
            'properties': {
                var: json_schema(vartype) for var, vartype in cls.__annotations__.items()
            }
        }

    raise TypeError('Unhandled class %s' % cls)
