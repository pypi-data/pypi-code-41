from decimal import Decimal
import json

from .types import ResourceSlot


def custom_decode(obj):
    type_tag = obj.get('__type')
    if type_tag is None:
        return obj
    elif type_tag == 'ResourceSlot':
        return ResourceSlot.from_json(obj)
    else:
        raise TypeError('Cannot deserialize the given JSON object.', obj)


class CustomEncoder(json.JSONEncoder):

    def default(self, obj):
        if isinstance(obj, ResourceSlot):
            data = obj.as_json_numeric()
            data['__type'] = 'ResourceSlot'
            return data
        raise TypeError('Cannot serialize the given object into JSON.', obj)


_encoder = CustomEncoder(allow_nan=False)


def dumps(o):
    return _encoder.encode(o)


def loads(s):
    return json.loads(s, object_hook=custom_decode, parse_float=Decimal)
