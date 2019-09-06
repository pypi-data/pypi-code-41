# Basic Flattening Utility
# Author: Spencer Hanson, for Swimlane


import re
import six
from types import FunctionType, LambdaType, MethodType, CodeType, GeneratorType, TracebackType, FrameType
from types import GetSetDescriptorType, MemberDescriptorType
from dict_plus import SortedDictPlus
import pendulum
from pendulum.exceptions import ParserError, PendulumException


BinaryType = six.binary_type
TextType = six.text_type

if six.PY3:  # Remapping of types from py2 to py3
    import types
    from builtins import str as unicode
    NoneType = type(None)
    TypeType = NoneType
    BooleanType = type(True)
    IntType = six.integer_types
    LongType = float
    FloatType = LongType
    ComplexType = NoneType
    ClassType = type
    InstanceType = getattr(types, "InstanceType", object)
    UnboundMethodType = types.FunctionType
    ModuleType = NoneType
    FileType = NoneType
    XRangeType = NoneType
    BufferType = NoneType
    SliceType = NoneType
    EllipsisType = NoneType
    DictProxyType = NoneType
    NotImplementedType = NoneType
    StringTypes = six.string_types
    TupleType = tuple
    ListType = list
    DictType = dict

else:
    from types import *


"""
Flattener file to provide utilites for dealing with messy JSON
"""


class Flattener(object):
    """
    Flattener class to easily flatten JSON
    """

    BASIC_TYPES = (NoneType, TypeType, BooleanType, IntType, LongType, FloatType, ComplexType, FunctionType, LambdaType,
                   GeneratorType, CodeType, ClassType, InstanceType, MethodType, UnboundMethodType, ModuleType,
                   FileType, XRangeType, SliceType, EllipsisType, TracebackType, FrameType, BufferType, DictProxyType,
                   NotImplementedType, GetSetDescriptorType, MemberDescriptorType, StringTypes, BinaryType, TextType)

    LIST_TYPES = (TupleType, ListType, set, frozenset)

    DICT_TYPES = (DictType, SortedDictPlus)

    def __init__(self, prefix=None, stringify_lists=True, shallow_flatten=False,
                 keep_simple_lists=True, autoparse_dt_strs=True, special_dt_formats=None, oldest_dt_allowed=None):
        """
        Create a new Flattener object with specific options

        :param prefix: Prefix to add to the data after flattening
        :param stringify_lists: Should we turn lists with basic types into CVSs? Defaults to True
        :param shallow_flatten: Should we ignore the first level of nesting, and only flatten each element within it?
         Used for lists of dictionaries
        :param keep_simple_lists: If a list in the resulting flattened dict is only integers or only strings, even if
        stringify_lists is True, keep this list
        :param autoparse_dt_strs: Do we attempt to automatically parse datetime looking strings/ints/floats to ISO8601?
        :param special_dt_formats: List of string formats to attempt parsing on for auto DT parsing. Will be ignored if
        autoparse_dt_strs is False
        :param oldest_dt_allowed: String of the oldest datetime that is allowed to be parsed. Defaults to 2005
        """

        self.prefix = prefix
        self.stringify_lists = stringify_lists
        self.shallow_flatten = shallow_flatten
        self.keep_simple_lists = keep_simple_lists
        self.autoparse_dt_strs = autoparse_dt_strs

        if special_dt_formats:
            self.special_dt_formats = special_dt_formats
        else:
            self.special_dt_formats = []

        if oldest_dt_allowed:
            self.oldest_dt_allowed = pendulum.parse(oldest_dt_allowed)
        else:
            self.oldest_dt_allowed = pendulum.parse("2005")

    def _try_parse_dt(self, value, is_number=False):
        """
        Try to parse a given value into a pendulum object, then return the iso string
        Works with strings and numbers that look like datestamps
        Ignores anything not parsed, returning it without parsing
        Ignores any datetime that is too old (could just be a really big numerical value) (anything past 2005)
        Uses self.special_dt_formats for other formats that could be specific to the data

        :param value: Value to attempt to parse into a datetime
        :param is_number: Is the value a number and should be treated as a timestamp?
        :return:
        """
        return value
        dt = None

        try:
            if is_number:
                dt = pendulum.from_timestamp(value)
            else:
                dt = pendulum.parse(value)
        except Exception:  # Broad exception clause to be picky about dates and parsing errors
            if is_number:  # Can't parse number with format, must be unparsable
                return value

            for fmt in self.special_dt_formats:  # Try special formats
                try:
                    dt = pendulum.from_format(value, fmt)
                except Exception:
                    continue

        if dt:
            diff = self.oldest_dt_allowed.diff(dt)
            signed_diff = diff.years * (1 if diff.invert else -1)
            if signed_diff <= 0:
                # Difference between datetime and oldest_dt is negative, which means it's oldest_dt+
                return dt.to_iso8601_string()
            else:
                # Difference is positive, earlier than oldest_dt, probably not a timestamp
                return value
        else:
            return value

    def combine_list(self, data, key):
        """
        Combine a list or listdict into a dict entry to be flattened.
        combine_list([1,2,3], "a") -> {"a": "1,2,3"}
        combine_list(["A","B"], "test") -> {"test": "A,B"}

        :param data:
        :param key:
        :return:
        """
        if not isinstance(data, ListType):
            raise Exception("Can't combine non-list!")
        if len(data) > 0 and isinstance(data[0], DictType):
            return self.combine_listdict(data)
        else:
            return {key: data}

    @staticmethod
    def flatten_single_lists(data):
        if not isinstance(data, SortedDictPlus):
            data = SortedDictPlus(data)
        for k, v in data.items():
            if isinstance(v, ListType):
                if len(v) == 1:  # Single entry list, can reduce to basic type
                    data[k] = v[0]
        return data

    @staticmethod
    def is_basiclist(data):
        if not len(data) > 0:
            return False  # Not a basic list because it's empty

        is_basic = True

        type_match = data[0]
        if not isinstance(type_match, int) and not isinstance(type_match, StringTypes):
            is_basic = False  # Type of data in list isnt int or str
        else:
            for datai in data:
                if not isinstance(datai, type(type_match)):
                    is_basic = False

        return is_basic


    @staticmethod
    def combine_listdict(data):
        """
        Combine a listdict into a single dictionary, NOT flattening
        Ex:
        [{"e": f_0, "g": h_0, ..}, {"e": f_1, "g": h_1, ..}] ->
                      c["e"] =  [f0, f1, ...]
                      c["g"] =  [h0, h1, ...]

        :param data: Listdict to combine into a single dictionary
        :return: Combined dictionary
        """
        if not isinstance(data, ListType) or (len(data) > 0 and not isinstance(data[0], DictType)):
            return data  # Can't combine non-listdict, so return base list

        result = SortedDictPlus()
        for el in data:
            for k, v in el.items():
                if k in result:
                    if isinstance(v, ListType):
                        """
                        Special case when:
                        {
                        "a_id": val,
                        "a": {
                            "id": val,
                            "other": [list val]
                        }
                        Collision of sub-listdict and and reformatted superkey lead to two keys being mapped to 'a_id'.
                        One option is to combine like [val1, val2] but can lead to [val, []] which isn't flattened
                        Other option is to extend like [val1].extend([val2]) but those "a_id" and "a": "id" might not be
                         related.
                        Current solution is to take the inner key ("a": "id") and turn it into "a_id_" appending '_'
                        until no collision
                        
                        The "other": [] is required, since the flattening treats "a" like as a dict-list, therefore "id"
                        is turned into a list (until flattening of subdict "a" is complete) which causes this error
                        
                        """
                        is_collision = True
                        new_key = k + "_"
                        while is_collision:
                            if new_key in result:
                                new_key += "_"
                            else:
                                result[new_key] = v
                                is_collision = False
                    else:
                        result[k].append(v)
                else:
                    if isinstance(v, ListType):
                        result[k] = v
                    else:
                        result[k] = [v]
        return result

    def flatten(self, data, prefix=None, shallow_flatten=None):
        """
        General flattening function
        Method to flatten a dict like or listdict
        Makes the keys lowercase, removes .'s and replaces spaces with underscores

        a["b C.D"] = {"e": f} -> a["b_cd_e"] = f


        All values are basic types of string or integer
        Lists will be flattened into CSV strings
        Works recursively on list-dicts and inner dicts

        :param data: List of dictionaries or dictionary to flatten
        :param prefix: Prefix to add to the data after flattening
        :param shallow_flatten: Should we ignore the first level of nesting, and only flatten each element within it?
         Used for lists of dictionaries
        :return: Single level dictionary/List of single level dictionaries
        """

        if self.prefix and prefix is None:  # prefix has priority over self.prefix
            prefix = self.prefix

        if shallow_flatten is None:  # Same with shallow flatten
            shallow_flatten = self.shallow_flatten

        if shallow_flatten:
            return [self.flatten(item, prefix=prefix, shallow_flatten=False) for item in data]

        # result = None
        is_basictype = False
        if isinstance(data, Flattener.DICT_TYPES):
            data = SortedDictPlus(data)

            result = self.flatten_dict(data, prefix) # Dict types
            tw = 2
        elif isinstance(data, Flattener.LIST_TYPES):
            # Complex list-like types
            listd = [self.flatten(item, prefix=prefix) for item in list(data)]
            result = self.combine_listdict(listd)

        elif isinstance(data, Flattener.BASIC_TYPES):
            result = data  # Basic types
            is_basictype = True
        else:
            raise Exception("Don't know how to flatten {}".format(data.__class__))  # Unknown type

        # Assumes that the dict has been flattened at least a bit, before attempting to stringify lists
        if self.stringify_lists and not is_basictype:
            if isinstance(result, DictType):  # if there is a list within the dict
                for k, v in result.items():
                    if isinstance(result[k], list):
                        stringify_list = True

                        if self.keep_simple_lists:
                            stringify_list = not self.is_basiclist(v)
                        
                        if stringify_list:
                            result[k] = ",".join(unicode(vi) for vi in v)

            else:
                new_result = []
                basictype_list = True  # Is our list something like [1, 2] or ["a", "b"] not [{"a": 1}, "b"]
                for item in iter(result):
                    if not isinstance(item, Flattener.BASIC_TYPES):
                        basictype_list = False
                    if isinstance(item, list):
                        new_result.append(",".join(unicode(vi) for vi in item))
                    else:
                        new_result.append(item)

                if basictype_list:
                    if self.keep_simple_lists and not self.is_basiclist(result):
                        new_result = ",".join([str(el) for el in new_result])

                result = new_result

        return result

    def flatten_dict(self, data, prefix=None):
        flat_dict = SortedDictPlus()

        for k, v in data.items():
            k = k.replace('.', '').replace(' ', '_')  # Reformat the key
            k = prefix + "_" + k if prefix else k

            if isinstance(v, DictType):  # Dict within dict
                sub_dict = self.flatten_dict(v, prefix=k)
                # Combine the flat_dict with the flattened sub_dict
                flat_dict = self.combine_listdict([flat_dict, sub_dict])  # Should not be combine_listdict
                flat_dict = self.flatten_single_lists(flat_dict)

            elif isinstance(v, ListType):
                flat_els = []
                for el in v:
                    flat_els.append(self.flatten(el, prefix=k))
                flat_dict = self.combine_listdict([flat_dict, self.combine_list(flat_els, k)])
            else:  # Base case, unflattenable value
                if self.autoparse_dt_strs:
                    if isinstance(v, StringTypes):  # Attempt to parse string into datetime
                        v = self._try_parse_dt(v)
                    elif isinstance(v, (IntType, FloatType)):  # Attempt to parse int/float into a timestamp datetime
                        v = self._try_parse_dt(v, is_number=True)

                flat_dict[k] = v

        return flat_dict


def do_flatten(data, prefix=None, stringify_lists=True, shallow_flatten=False,
               keep_simple_lists=True, autoparse_dt_strs=True):
    """
    Simple alias for creating a flattener then running flatten() with options
    """

    fl = Flattener(prefix=prefix, stringify_lists=stringify_lists, shallow_flatten=shallow_flatten,
                   keep_simple_lists=keep_simple_lists, autoparse_dt_strs=autoparse_dt_strs)

    return fl.flatten(data)


def hoist_key(key, from_list):
    """
    Hoist out a specific key within a given listdict
    Ex: hoist_key("a", [{"a": 1, "b": 4},{"a": 2}, ..]) -> [1,2,3]
    :param key: Key to grab from each dict within the list of dictionaries
    :param from_list: listdict to source from
    :return: list of hoisted values
    """
    hoisted = []
    for element in from_list:
        if key not in element:
            raise Exception("Key {} not found in dict {}".format(key, element))
        hoisted.append(element[key])
    return hoisted


def hoist_keys(key_list, from_list):
    """
    Hoist out a specific keys within a given listdict
    Ex: hoist_keys(["a", "b"], [{"a": 1, "b": 4},{"a": 2, "b": 2, "c": 3}, ..]) ->
    [[all a keys], [all b keys]] -> [[1,2],[4,2]]
    :param key_list: List of keys to hoist from the list of dictionaries
    :param from_list:
    :return: List of the list of hoisted keys
    """
    hoisted = []
    for key in key_list:
        hoisted.append(hoist_key(key, from_list))
    return hoisted


def replace_dict_prefix(prefix, replace_val, from_dict):
    """
    Change a similar prefix on keys within a dict to something else, say 'annoying_stuff_' -> 'a_'
    Ex {"annoying_stuff_important_stuff": "data", "annoying_stuff_asdf": "data2"} ->
    {"a_important_stuff": "data", "a_asdf": "data2"}

    :param prefix: Prefix to replace
    :param replace_val: Prefix to replace with
    :param from_dict: Dictionary to replace prefix on
    :return: Changed from_dict
    """
    for k in from_dict.keys():
        if k.startswith(prefix):
            newk = k.replace(prefix, replace_val, 1)
            if newk in from_dict:
                raise Exception("Can't remove prefix, results in namespace collision!")
            from_dict[newk] = from_dict.pop(k)
    return from_dict


def merge_listdict(data, subdict_data):
    """
    Helper method for flatten_data, used to help flatten recursive list-dicts
    Takes the data of the dict to store the flattened output like {"a": "val1", "b": ...}
    And the value of the subdict with similar keys, like {"a": "val2"}
    Merges the two into a list {"a": ["val1", "val2"], "b": ...}

    :param data: Original data dict
    :param subdict_data: subdict to add to the outer dictionary
    :return: modified data dict
    """
    data_keys = data.keys()
    sub_keys = subdict_data.keys()
    for key in set(data_keys).intersection(sub_keys):  # Keys that they share
        if isinstance(data[key], list):  # Already a list of this object
            data[key].append(subdict_data[key])
        else:  # It isn't a list, so to merge it we must make it into one
            data[key] = [data[key], subdict_data[key]]

    for key in set(sub_keys).difference(data_keys):  # Keys that are in the subdict to preserve data
        data[key] = subdict_data[key]

    return data


def clean_xmltodict_result(data, to_remove_list=None):
    """
    Helper method to clean the output of an xmltodict with messy '#' and '@' trailing
    :param data: dict
    :param to_remove_list: list of strings to replace with underscores in the resulting dict
    :return: dict
    """
    keys_to_delete = []
    pairs_to_add = []

    for k, v in six.iteritems(data):
        match = re.match(".*_([@#].*$)", k)  # Ends with _#text or _@property
        if match:
            # Remove the '#' or '@' ie  asdf_@property -> asdf_property
            pairs_to_add.append((k.replace(match.groups()[0], match.groups()[0][1:]), v))
            keys_to_delete.append(k)

    for k in keys_to_delete:
        data.pop(k)

    for k, v in pairs_to_add:
        if k in data:
            raise Exception("Cannot clean {}, results in namespace collision".format(k))
        data[k] = v

    data = SortedDictPlus(data)
    if not to_remove_list:
        to_remove_list = []
    
    to_remove_list.extend(["@", "-", ":", "#", "$", "%"])
    to_remove_list = list(set(to_remove_list))  # Make sure we don't have duplicates
    
    def new_kv(k, v):  # Replace all invalid characters with underscores
        for to_remove in to_remove_list:
            k = k.replace(to_remove, "_")
        return k, v

    data.map(new_kv)

    return data
