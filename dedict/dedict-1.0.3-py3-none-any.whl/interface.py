from typing import List, get_type_hints, Any, Dict

from dedict.optional_attribute import OptionalAttr


def _dedict(data: dict, cls: Any, strict):
    obj = cls()
    annotations = get_type_hints(cls)

    if strict:
        for k, v in annotations.items():
            if k not in data.keys():
                if not issubclass(v, OptionalAttr):
                    raise AttributeError(f'dictionary was missing mandatory attribute {k} to create an object of type {cls.__name__}')

    for attr, value in data.items():

        try:
            t = annotations[attr]
        except KeyError:
            raise AttributeError(f'object {cls.__name__} has no attribute named {attr}')

        if hasattr(t, '__origin__') and issubclass(t.__origin__, OptionalAttr):
            t = t.__args__[0]

        setattr(obj, attr, _setter(value, t, strict))

    return obj


def _setter(obj, t, strict):
    if t in (str, int, float, bool):
        return obj
    elif t == list:
        return [v for v in obj]
    elif t == tuple:
        return tuple(v for v in obj)
    elif t == dict:
        return {k: v for k, v in obj.items()}
    elif t == set:
        return {v for v in obj}
    elif hasattr(t, '__origin__') and (t.__origin__ == list or issubclass(t.__origin__, List)):
        return [_setter(v, t.__args__[0], strict) for v in obj]
    elif hasattr(t, '__origin__') and (t.__origin__ == dict or issubclass(t.__origin__, Dict)):
        return {k: _setter(v, t.__args__[1], strict) for k, v in obj.items()}
    else:
        if hasattr(t, 'dedict'):
            return t.dedict(obj)
        else:
            return _dedict(obj, t, strict)


class Dedictable:

    @classmethod
    def dedict(cls, d: dict):
        try:
            return _dedict(d, cls, strict=False)

        except AttributeError:
            raise

        except Exception:
            raise Exception(f'error creating object of type {cls.__name__} from dict')


class DedictableStrict:

    @classmethod
    def dedict(cls, d: dict):
        try:
            return _dedict(d, cls, strict=True)

        except AttributeError:
            raise

        except Exception:
            raise Exception(f'error creating object of type {cls.__name__} from dict')
