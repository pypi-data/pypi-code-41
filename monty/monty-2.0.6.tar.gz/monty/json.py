# coding: utf-8
"""
JSON serialization and deserialization utilities.
"""

from __future__ import absolute_import, unicode_literals
import os
import json
import datetime
import six
import inspect

from hashlib import sha1
from collections import OrderedDict, defaultdict

try:
    from importlib import import_module
except ImportError:
    # importlib only available in Python 2.7+, 3.1+
    importlib = lambda x: x

try:
    from inspect import getfullargspec as getargspec
except ImportError:
    from inspect import getargspec

try:
    import numpy as np
except ImportError:
    np = None

try:
    import bson
except ImportError:
    bson = None

try:
    import ruamel.yaml as yaml
    try:  # Default to using CLoader and CDumper for speed.
        from ruamel.yaml import CLoader as Loader
        from ruamel.yaml import CDumper as Dumper
    except ImportError:
        from ruamel.yaml import Loader
        from ruamel.yaml import Dumper
except ImportError:
    try:
        import yaml
        try:  # Default to using CLoader and CDumper for speed.
            from yaml import CLoader as Loader
            from yaml import CDumper as Dumper
        except ImportError:
            from yaml import Loader
            from yaml import Dumper
    except ImportError:
        yaml = None

__author__ = "Shyue Ping Ong"
__copyright__ = "Copyright 2014, The Materials Virtual Lab"
__version__ = "0.1"
__maintainer__ = "Shyue Ping Ong"
__email__ = "ongsp@ucsd.edu"
__date__ = "1/24/14"


def _load_redirect(redirect_file):
    try:
        with open(redirect_file, "rt") as f:
            d = yaml.safe_load(f)
    except IOError:
        # If we can't find the file
        # Just use an empty redirect dict
        return {}

    # Convert the full paths to module/class
    redirect_dict = defaultdict(dict)
    for old_path, new_path in d.items():
        old_class = old_path.split(".")[-1]
        old_module = ".".join(old_path.split(".")[:-1])

        new_class = new_path.split(".")[-1]
        new_module = ".".join(new_path.split(".")[:-1])

        redirect_dict[old_module][old_class] = {
            "@module": new_module,
            "@class": new_class,
        }

    return dict(redirect_dict)


class MSONable(object):
    """
    This is a mix-in base class specifying an API for msonable objects. MSON
    is Monty JSON. Essentially, MSONable objects must implement an as_dict
    method, which must return a json serializable dict and must also support
    no arguments (though optional arguments to finetune the output is ok),
    and a from_dict class method that regenerates the object from the dict
    generated by the as_dict method. The as_dict method should contain the
    "@module" and "@class" keys which will allow the MontyEncoder to
    dynamically deserialize the class. E.g.::

        d["@module"] = self.__class__.__module__
        d["@module"] = self.__class__.__name__

    A default implementation is provided in MSONable, which automatically
    determines if the class already contains self.argname or self._argname
    attributes for every arg. If so, these will be used for serialization in
    the dict format. Similarly, the default from_dict will deserialization
    classes of such form. An example is given below::

        class MSONClass(MSONable):

        def __init__(self, a, b, c, d=1, **kwargs):
            self.a = a
            self.b = b
            self._c = c
            self._d = d
            self.kwargs = kwargs

    For such classes, you merely need to inherit from MSONable and you do not
    need to implement your own as_dict or from_dict protocol.

    New to Monty V2.0.6....
    Classes can be redirected to moved implementations by putting in the old
    fully qualified path and new fully qualified path into .monty.yaml in the 
    home folder

    Example:
    old_module.old_class: new_module.new_class
    """

    REDIRECT = _load_redirect(os.path.join(os.path.expanduser("~"), ".monty.yaml"))

    def as_dict(self):
        """
        A JSON serializable dict representation of an object.
        """
        d = {"@module": self.__class__.__module__,
             "@class": self.__class__.__name__}

        try:
            parent_module = self.__class__.__module__.split('.')[0]
            module_version = import_module(parent_module).__version__
            d["@version"] = u"{}".format(module_version)
        except AttributeError:
            d["@version"] = None

        args = getargspec(self.__class__.__init__).args

        def recursive_as_dict(obj):
            if isinstance(obj, (list, tuple)):
                return [recursive_as_dict(it) for it in obj]
            elif isinstance(obj, dict):
                return {kk: recursive_as_dict(vv) for kk, vv in obj.items()}
            elif hasattr(obj, "as_dict"):
                return obj.as_dict()
            return obj

        for c in args:
            if c != "self":
                try:
                    a = self.__getattribute__(c)
                except AttributeError:
                    try:
                        a = self.__getattribute__("_" + c)
                    except AttributeError:
                        raise NotImplementedError(
                            "Unable to automatically determine as_dict "
                            "format from class. MSONAble requires all "
                            "args to be present as either self.argname or "
                            "self._argname, and kwargs to be present under"
                            "a self.kwargs variable to automatically "
                            "determine the dict format. Alternatively, "
                            "you can implement both as_dict and from_dict.")
                d[c] = recursive_as_dict(a)
        if hasattr(self, "kwargs"):
            d.update(**self.kwargs)
        if hasattr(self, "_kwargs"):
            d.update(**self._kwargs)
        return d

    @classmethod
    def from_dict(cls, d):
        decoded = {k: MontyDecoder().process_decoded(v) for k, v in d.items()
                   if not k.startswith("@")}
        return cls(**decoded)

    def to_json(self):
        """
        Returns a json string representation of the MSONable object.
        """
        return json.dumps(self, cls=MontyEncoder)

    def unsafe_hash(self):
        """
        Returns an hash of the current object. This uses a generic but low
        performance method of converting the object to a dictionary, flattening
        any nested keys, and then performing a hash on the resulting object
        """

        def flatten(obj, seperator="."):
            # Flattens a dictionary

            flat_dict = {}
            for key, value in obj.items():
                if isinstance(value, dict):
                    flat_dict.update(
                        {
                            seperator.join([key, _key]): _value
                            for _key, _value in flatten(value).items()
                        }
                    )
                elif isinstance(value, list):
                    list_dict = {
                        "{}{}{}".format(key,seperator,num): item for num, item in enumerate(value)
                    }
                    flat_dict.update(flatten(list_dict))
                else:
                    flat_dict[key] = value

            return flat_dict

        ordered_keys = sorted(flatten(jsanitize(self.as_dict())).items(), key=lambda x: x[0])
        ordered_keys = [item for item in ordered_keys if "@" not in item[0]]
        return sha1(json.dumps(OrderedDict(ordered_keys)).encode("utf-8"))


class MontyEncoder(json.JSONEncoder):
    """
    A Json Encoder which supports the MSONable API, plus adds support for
    numpy arrays, datetime objects, bson ObjectIds (requires bson).

    Usage::

        # Add it as a *cls* keyword when using json.dump
        json.dumps(object, cls=MontyEncoder)
    """

    def default(self, o):
        """
        Overriding default method for JSON encoding. This method does two
        things: (a) If an object has a to_dict property, return the to_dict
        output. (b) If the @module and @class keys are not in the to_dict,
        add them to the output automatically. If the object has no to_dict
        property, the default Python json encoder default method is called.

        Args:
            o: Python object.

        Return:
            Python dict representation.
        """
        if isinstance(o, datetime.datetime):
            return {"@module": "datetime", "@class": "datetime",
                    "string": o.__str__()}
        if np is not None:
            if isinstance(o, np.ndarray):
                return {"@module": "numpy",
                        "@class": "array",
                        "dtype": o.dtype.__str__(),
                        "data": o.tolist()}
            elif isinstance(o, np.generic):
                return o.item()
        if bson is not None:
            if isinstance(o, bson.objectid.ObjectId):
                return {"@module": "bson.objectid",
                        "@class": "ObjectId",
                        "oid": str(o)}

        try:
            d = o.as_dict()
            if "@module" not in d:
                d["@module"] = u"{}".format(o.__class__.__module__)
            if "@class" not in d:
                d["@class"] = u"{}".format(o.__class__.__name__)
            if "@version" not in d:
                try:
                    parent_module = o.__class__.__module__.split('.')[0]
                    module_version = import_module(parent_module).__version__
                    d["@version"] = u"{}".format(module_version)
                except AttributeError:
                    d["@version"] = None
            return d
        except AttributeError:
            return json.JSONEncoder.default(self, o)


class MontyDecoder(json.JSONDecoder):
    """
    A Json Decoder which supports the MSONable API. By default, the
    decoder attempts to find a module and name associated with a dict. If
    found, the decoder will generate a Pymatgen as a priority.  If that fails,
    the original decoded dictionary from the string is returned. Note that
    nested lists and dicts containing pymatgen object will be decoded correctly
    as well.

    Usage:

        # Add it as a *cls* keyword when using json.load
        json.loads(json_string, cls=MontyDecoder)
    """

    def process_decoded(self, d):
        """
        Recursive method to support decoding dicts and lists containing
        pymatgen objects.
        """
        if isinstance(d, dict):
            if "@module" in d and "@class" in d:
                modname = d["@module"]
                classname = d["@class"]
                if classname in MSONable.REDIRECT.get(modname, {}):
                    modname = MSONable.REDIRECT[modname][classname]["@module"]
                    classname = MSONable.REDIRECT[modname][classname]["@class"]
            else:
                modname = None
                classname = None
            if modname and modname not in ["bson.objectid", "numpy"]:
                if modname == "datetime" and classname == "datetime":
                    try:
                        dt = datetime.datetime.strptime(d["string"],
                                                        "%Y-%m-%d %H:%M:%S.%f")
                    except ValueError:
                        dt = datetime.datetime.strptime(d["string"],
                                                        "%Y-%m-%d %H:%M:%S")
                    return dt

                mod = __import__(modname, globals(), locals(), [classname], 0)
                if hasattr(mod, classname):
                    cls_ = getattr(mod, classname)
                    data = {k: v for k, v in d.items()
                           if not k.startswith("@")}
                    if hasattr(cls_, "from_dict"):
                        return cls_.from_dict(data)
            elif np is not None and modname == "numpy" and classname == \
                    "array":
                return np.array(d["data"], dtype=d["dtype"])

            elif (bson is not None) and modname == "bson.objectid" and \
                    classname == "ObjectId":
                return bson.objectid.ObjectId(d["oid"])

            return {self.process_decoded(k): self.process_decoded(v)
                    for k, v in d.items()}
        elif isinstance(d, list):
            return [self.process_decoded(x) for x in d]

        return d

    def decode(self, s):
        d = json.JSONDecoder.decode(self, s)
        return self.process_decoded(d)


class MSONError(Exception):
    """
    Exception class for serialization errors.
    """
    pass


def jsanitize(obj, strict=False, allow_bson=False):
    """
    This method cleans an input json-like object, either a list or a dict or
    some sequence, nested or otherwise, by converting all non-string
    dictionary keys (such as int and float) to strings, and also recursively
    encodes all objects using Monty's as_dict() protocol.

    Args:
        obj: input json-like object.
        strict (bool): This parameters sets the behavior when jsanitize
            encounters an object it does not understand. If strict is True,
            jsanitize will try to get the as_dict() attribute of the object. If
            no such attribute is found, an attribute error will be thrown. If
            strict is False, jsanitize will simply call str(object) to convert
            the object to a string representation.
        allow_bson (bool): This parameters sets the behavior when jsanitize
            encounters an bson supported type such as objectid and datetime. If
            True, such bson types will be ignored, allowing for proper
            insertion into MongoDb databases.

    Returns:
        Sanitized dict that can be json serialized.
    """
    if allow_bson and (isinstance(obj, (datetime.datetime, bytes)) or \
                       (bson is not None and isinstance(obj,
                                                        bson.objectid.ObjectId))):
        return obj
    if isinstance(obj, (list, tuple)):
        return [jsanitize(i, strict=strict, allow_bson=allow_bson) for i in obj]
    elif np is not None and isinstance(obj, np.ndarray):
        return [jsanitize(i, strict=strict, allow_bson=allow_bson) for i in
                obj.tolist()]
    elif isinstance(obj, dict):
        return {k.__str__(): jsanitize(v, strict=strict, allow_bson=allow_bson)
                for k, v in obj.items()}
    elif isinstance(obj, six.integer_types + tuple([float])):
        return obj
    elif obj is None:
        return None

    else:
        if not strict:
            return obj.__str__()
        else:
            if isinstance(obj, six.string_types):
                return obj.__str__()
            else:
                return jsanitize(obj.as_dict(), strict=strict,
                                 allow_bson=allow_bson)
