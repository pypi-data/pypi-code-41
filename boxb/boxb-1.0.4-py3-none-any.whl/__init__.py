import json

from .bbox import *
from .multibbox import *


def dumps(obj, *args, **kwargs):
    if not isinstance(obj, BBox) and not isinstance(obj, MultiBBox):
        raise TypeError("Object should be either of type BBox or MultiBBox")
    return json.dumps(obj.to_json(), *args, **kwargs)


def dump(obj, *args, **kwargs):
    if not isinstance(obj, BBox) and not isinstance(obj, MultiBBox):
        raise TypeError("Object should be either of type BBox or MultiBBox")
    return json.dump(obj.to_json(), *args, **kwargs)


def loads(*args, **kwargs):
    obj = json.loads(*args, **kwargs)
    if not isinstance(obj, dict) and obj.get("type") not in ["BBox", "MultiBBox"]:
        raise TypeError("Object should be either of type BBox or MultiBBox")
    if obj["type"] == "BBox":
        return BBox.from_json(obj)
    return MultiBBox.from_json(obj)


def load(*args, **kwargs):
    obj = json.load(*args, **kwargs)
    if not isinstance(obj, dict) and obj.get("type") not in ["BBox", "MultiBBox"]:
        raise TypeError("Object should be either of type BBox or MultiBBox")
    if obj["type"] == "BBox":
        return BBox.from_json(obj)
    return MultiBBox.from_json(obj)
