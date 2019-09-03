import copy
import hashlib
import itertools
import json
import re
import time
import uuid
from collections import OrderedDict, namedtuple, defaultdict
from enum import Enum
from pprint import pprint
from typing import Callable, Optional, Any, Tuple, Mapping, Set, Union, List

import arrow
import attr
import faker
import pandas as pd
import pydash
from pygments import highlight, lexers, formatters
from six import string_types

Function1 = Callable[[object], object]


# ---------------------------------- TYPE UTILS ----------------------------------

def attr_fields_except(cls:type, fields_to_ignore: List[attr._make.Attribute]) -> List[attr._make.Attribute]:
    return [attribute for attribute in attr.fields(cls) if attribute not in fields_to_ignore]


def keep_fields_for_attr_value(value:type, fields_to_keep: List[attr._make.Attribute]) -> Mapping[str, Any]:
    return attr.asdict(value, recurse=False, filter=lambda a, v: a in fields_to_keep)


def modify_attr_class(attrClass: type, modifications:dict) -> namedtuple:
    return attr.evolve(attrClass, **modifications)


def namedtuple_asdict(obj):
    """
    Turns a named tuple into a dict recursively
    From: https://stackoverflow.com/questions/16938456/serializing-a-nested-namedtuple-into-json-with-python-2-7
    """
    if hasattr(obj, "_asdict"): # detect namedtuple
        return OrderedDict(zip(obj._fields, (attr.asdict(item) for item in obj)))
    elif isinstance(obj, string_types): # iterables - strings
        return obj
    elif hasattr(obj, "keys"): # iterables - mapping
        return OrderedDict(zip(obj.keys(), (attr.asdict(item) for item in obj.values())))
    elif hasattr(obj, "__iter__"): # iterables - sequence
        return type(obj)((attr.asdict(item) for item in obj))
    else: # non-iterable cannot contain namedtuples
        return obj


def field_names_of_attr_class(attr_class:type) -> List[str]:
    return list(map(lambda x: x.name, attr.fields(attr_class)))


def converter_for_list_of_classes(l:List[object], cls) -> List:
    if not l:
        return []

    invalid_types_in_list = list(map(
        lambda x: type(x),
        filter(
            lambda x: not isinstance(x, (cls, dict)),
            l
        )
    ))

    if invalid_types_in_list:
        raise Exception("Invalid type(s) {} in list".format(invalid_types_in_list))

    return list(map(
        lambda y: y if isinstance(y, cls) else cls(**y),
        l
    ))


def union_type_validator(union_type:type) -> Callable[[Any, Any], bool]:
    def validator(self, attribute, value):
        return type(value) in union_type.__args__
    return validator


def converter_for_union_type(union_type:type, handlers:Mapping[type, Callable[[Any], Any]]) -> Callable[[Any], Any]:
    def converter(data:Any):
        # Shouldnt assert from union.__args__ ... the union types eats up any types that are subclasses of each other ... such as int and bool ...
        assert type(data) in handlers.keys(), "Value of unexpected type ({}) encountered. Expecting: {}".format(type(data), handlers.keys())
        return handlers[type(data)](data)
    return converter


def converter_for_classes(data:object, desired_attr_type:type, dict_constructor:Optional[Callable[[dict], object]]=None) -> object:
    """
    Convert a attribute into an attr class ...
    :param data:
    :param desired_attr_type:
    :param dict_constructor:
    :return:
    """
    if data is None:
        return None
    if not isinstance(data, (desired_attr_type, dict)):
        raise Exception("Invalid type {} of data.".format(type(data)))
    return data if isinstance(data, desired_attr_type) else (
        desired_attr_type(**data) if not dict_constructor else dict_constructor(data)
    )


def list_converter(l:List[object], desired_attr_type_for_elements:type, item_constructor:Optional[Callable[[dict], object]]=None) -> List[object]:
    if l is None:
        return None
    if not l:
        return []
    return [
        converter_for_classes(x, desired_attr_type_for_elements, item_constructor) for x in l
    ]


def attr_instance_to_dict(instance:Any, hide_internal_attributes:Optional[bool]=False):
    if hide_internal_attributes:
        return attr.asdict(instance, filter=lambda attribute, value: not attribute.metadata.get("internal", False))
    else:
        return attr.asdict(instance)


# -------------------------------- COMMON UTILS --------------------------------


def utc_timestamp() -> str:
    return str(arrow.utcnow())


def unique_id() -> str:
    return str(uuid.uuid4())


def hash_query(query):
    return hashlib.md5("".join(query.lower().split()).encode('utf-8')).hexdigest()


# -------------------------------- STRUCTURE UTILS --------------------------------


def assign_to_dict(dictionary:dict, key:str, value:object) -> dict:
    return merge_dicts(dictionary, {key: value})


def map_object(object:Optional[Any], method:Callable[[Any], Any], default:Optional[Any]=None) -> Any:
    return method(object) if object is not None else default


def nest_values_under(d, under):
    return {k: {under: v} for k, v in d.items()}


def append_key_to_values_as(d, key_title):
    return [pydash.merge(value, {key_title: key}) for key, value in d.items()]


def _drop_from_dict(d: dict, skip: List[object]) -> dict:
    if d is None:
        d = None
    if isinstance(d, list):
        return [drop_from_dict(e, skip) for e in d]
    if isinstance(d, dict):
        return {
            k: drop_from_dict(v, skip) for k, v in d.items() if k not in skip
        }
    return d


def drop_from_dict(d: dict, skip: List[object]) -> dict:
    return _drop_from_dict(d, skip)


def modify_named_tuple(nt: namedtuple, modifications:dict) -> namedtuple:
    attr_dict = namedtuple_asdict(nt)
    attr_dict.update(modifications)
    return type(nt)(**attr_dict)


# def flatten_list_recursively(l: list):
#     if not isinstance(l, list):
#         return [l]
#     returnVal = []
#     for x in l:
#         returnVal = returnVal + flatten_list_recursively(x)
#     return returnVal


def flatten_list_recursively(l: Union[List[Any], Any], remove_empty_lists=False):
    if l is None:
        return []
    if not isinstance(l, list):
        return [l]
    # THIS DOES WEIRD STUFF WITH TUPLES!
    return list(itertools.chain(*[flatten_list_recursively(x) for x in l if (not remove_empty_lists or x)]))


def flatmap(listToItterate: List, inputToAppendTo: List, function: Callable) -> List :
    if not listToItterate:
        return []
    head = listToItterate[0]
    tail = listToItterate[1:]
    return flatmap(tail, function(inputToAppendTo, head), function)


def join_inner_arrays(_dict, caster=lambda x: x):
    return {
        k: ",".join(map(caster, v)) if isinstance(v, list) else v
        for (k, v) in _dict.items()
    }


def invert_dict_lookup(d):
    return {v: k for k, v in d.items()}


def pluck(path, d, default={}):
    split_path = [x for x in path.split('.') if x]
    if len(split_path) > 0:
        return pluck('.'.join(split_path[1:]), d.get(split_path[0], default))
    return d


def tuples_with_nans_to_tuples_with_nones(iter:List[Any]) -> Tuple[Any]:
    # - [x] TODO: Dont like the instance check here ... python has no way of saying "isPrimitive"
        # ... I only want to check for NaNs on primitives... and replace them with None ... not Lists ...
        # Realization: NaNs are floats ...!
    return (
        tuple(map(lambda x: None if isinstance(x, float) and pd.isna(x) else x, list(tup)))
        for tup in iter
    )


def append_to_list(l:List, thing_to_append:Optional[object]) -> List:
    return l + [thing_to_append] if thing_to_append else l


def merge_dicts(a:dict, b:dict) -> dict:
    c = copy.deepcopy(a)
    c.update(b)
    return c


def reverse_index_dictionary(d:dict) -> dict:
    new_keys = list(set(flatten_list_recursively(list(d.values()))))
    return {
        new_key: [old_key for old_key in list(d.keys()) if new_key in d[old_key]] for new_key in new_keys
    }


def partition_list(l:List, partitions:int) -> List[List]:
    assert partitions >= 1, "Partitions must be >= 1"
    size_of_each_parition = int(len(l) / partitions)
    partitions = zip([x for x in range(0, partitions)], [x for x in range(1, partitions)] + [None])
    return [
        l[start*size_of_each_parition:None if end is None else end*size_of_each_parition]
        for start, end in partitions
    ]


def head(l:List) -> object:
    return l[0] if l else None


def tail(l:List) -> List:
    return None if l is None else l[1:]


def dervie_set_by_element_id(l:List[Any], identifier:Callable[[Any], str]=lambda x: x) -> Set[Any]:
    # from itertools import combinations
    # combinations(l, 2)
    return set({identifier(x): x for x in l}.values())


def group_by_key(l:List[Any], key:Callable[[Any], str]) -> Mapping[str, List[Any]]:
    key_deriver = key if callable(key) else lambda x: x[key]
    returnVal = defaultdict(list)
    for x in l:
        returnVal[key_deriver(x)].append(x)
    return returnVal


def group_objects_by(l:List[Any], group_by:Callable[[Any], str]) -> Mapping[str, List[Any]]:
    # print(l)
    # print(list(map(group_by, l)))
    unique_groups = set(map(group_by, l))
    return {
        g: list(filter(lambda x: group_by(x) == g, l))
        for g in unique_groups
    }


def merge_unique_objects_on(objects: List[Any], identifier:Callable, reducer:Callable=head) -> List[Any]:
    groups = group_by_key(objects, identifier)
    return list({
        groupId: reducer(values) for groupId, values in groups.items()
    }.values())


def map_key(o:dict, key:str, mapper:Callable) -> dict:
    return pydash.set_(o, key, mapper(pydash.get(o, key)))


# def list_of_dicts_to_list_of_classes(l:List[dict], cls:T) -> List[T]:
#     return list(map(lambda d: cls(**d), l))
# T = TypeVar("T")
# TypeVars and isinstnace does weird stuf ... https://github.com/python/typing/issues/62

# ----------------------------------- TIME UTILS -----------------------------------


def timeit(method):
    def timed(*args, **kw):
        ts = time.time()
        result = method(*args, **kw)
        te = time.time()
        return ('%2.2f' % (te - ts), result)

    return timed


def derive_hour_from_date(iso_timestamp:str):
    d = arrow.get(iso_timestamp)
    return {
        "hour_number": int(d.format("H")),
        "hour": d.format("hhA"),
        "timezone": d.format("ZZ")
    }


def derive_day_from_date(iso_timestamp):
    return str(arrow.get(iso_timestamp).date())


def remap_date_formats(date_dict, date_formats, original_format):
    return {
        k: arrow.get(v, original_format).format(date_formats.get(k, original_format))
        for (k, v) in date_dict.items()
    }

def pick_random_time_between(faker:faker.Generator, start:arrow.Arrow, stop:arrow.Arrow) -> arrow.arrow:
    return arrow.get(faker.date_time_between(start.datetime, stop.datetime))


def seconds_between_times(arrow_time_a:arrow.Arrow, arrow_time_b:arrow.Arrow) -> float:
    return abs(arrow_time_a.float_timestamp - arrow_time_b.float_timestamp)


# -------------------------------- FORMATTING UTILS ------------------------------


def de_whitespate_dict(_dict):
    return {
        k: v.replace(" ", "") if isinstance(v, str) else v
        for (k, v) in _dict.items()
    }

def pprint_with_header(header, obj):
    print("^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^")
    print(header)
    pprint(obj)
    print("__________________________________________________")
    print("")


def print_json_with_header(header, obj):
    print("^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^")
    print(header)
    print(json_makeup(obj))
    print("__________________________________________________")
    print("")


def print_attr_class_with_header(header, obj):
    if isinstance(obj, list):
        obj = list(map(attr.asdict, obj))
    print("^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^")
    print(header)
    print(json_makeup(attr.asdict(obj)))
    print("__________________________________________________")
    print("")


def print_with_header(header, obj):
    print("^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^")
    print(header)
    print(obj)
    print("__________________________________________________")
    print("")


def json_makeup(json_object):
    formatted_json = json.dumps(json_object, sort_keys=True, indent=4)
    colorful_json = highlight(
        formatted_json.encode('UTF-8'),
        lexers.JsonLexer(), formatters.TerminalFormatter()
    )
    return colorful_json


def json_to_image_bytes(json_object) -> bytes:
    formatted_json = json.dumps(json_object, sort_keys=True, indent=4)
    colorful_json = highlight(
        formatted_json.encode('UTF-8'),
        lexers.JsonLexer(), formatters.ImageFormatter(font_size=12, line_numbers=False)
    )
    return colorful_json


def filter_empty_records(l:List) -> List:
    return [x for x in l if x]


# -------------------------------- ASSERTION UTILS ------------------------------


def is_not_none_or_nan(v:object) -> bool:
    return (True if v else False) if not isinstance(v,float) else (not pd.isna(v) if v else False)


def all_values_in_list_are_not_nones_or_nans(l:List) -> bool:
    return all_values_in_list_pass(l, is_not_none_or_nan)


def all_values_in_list_pass(l:List, validity_filter:callable) -> bool:
    return all(map(validity_filter, l))


def first_arg_is_type_wrapper(_callable, tuple_of_types) -> Callable[[Any], bool]:
    return lambda x: x if not isinstance(x, tuple_of_types) else _callable(x)


# ------------------------- CLASS UTILS --------------------------------------


class _AttrsAsDictMeta(type):
    def __iter__(self):
        return zip(self.keys(), self.values())

    def __getitem__(self, arg):
        return dict(list(self)).get(arg)

    def keys(cls):
        return list(filter(lambda x: x[0] != "_", cls.__dict__.keys()))

    def values(cls):
        return [ getattr(cls, k) for k in cls.keys()]

    def items(cls):
        return dict(list(cls)).items()



class AttrsAsDict(metaclass=_AttrsAsDictMeta):
    pass


class ValuedObject(object):
    def __init__(self, value):
        self.value = value


class AddableWithObjectsWithValues(object):
    def __add__(self, other):
        if other is None:
            return self
        elif isinstance(other, (ValuedObject, Enum)):
            return ValuedObject(self.value + other.value)
        else:
            raise TypeError("Cannot add {} with {}.".format(type(self), type(other)))


class MappableList(list):

    def map(self, f:Function1) -> 'MappableList':
        return MappableList(map(f, self))

    def filter(self, f:Function1) -> 'MappableList':
        return MappableList(filter(f, self))

    def sort(self, f:Function1) -> 'MappableList':
        return MappableList(sorted(self, key=f))

    @staticmethod
    def from_dict(d:dict) -> 'MappableList':
        return MappableList(d.items())

    @staticmethod
    def from_set(s:set) -> 'MappableList':
        return MappableList(s)

    def to_set(self) -> set:
        return set(self)

    def to_dict(self, value_from_key_function:Function1, dict_instantiator:Callable[[List[Tuple]], dict]=dict) -> dict:
        return dict_instantiator(zip(self, self.map(value_from_key_function)))

    # This can be done with a .map().sum()
    # def sum(self, f:callable):
    #     return sum(self.map(f))


# -------------------------- GENERATOR UTILS ------------------------------------


ToYeild = Any


def get_until(
        yielder:Callable[[], Any],
        appender:Callable[[Any, ToYeild], Any],
        ignore_condition:Callable[[Any, ToYeild], bool],
        stop_condition:Callable[[ToYeild], bool],
        to_yield:List) -> ToYeild:
    ignored = 0
    returnVal = to_yield
    while not stop_condition(returnVal):
        next_item = yielder()
        if ignore_condition(next_item, returnVal):
            ignored += 1
        else:
            returnVal = appender(next_item, returnVal)
    # print(ignored, len(returnVal))
    return returnVal


def get_unique_cortex_objects(yielder, limit:int) -> List:
    return list(
        get_until(
            yielder,
            appender=lambda obj, dictionary: assign_to_dict(dictionary, obj["id"], obj),
            ignore_condition=lambda obj, dictionary: obj["id"] in dictionary,
            stop_condition=lambda dictionary: len(dictionary) >= limit,
            to_yield={}
        ).values()
    )


def label_generator(word:str, used_labels:List[str], label_length:int=3) -> Optional[str]:
    """
    Right now, labels are only three letters long!
    :param word:
    :param used_labels:
    :return:
    """
    words = re.split(r'[^a-zA-Z0-9]', word)
    if len(words) != label_length:
        word = "".join(words)
        words = split_string_into_parts(word, label_length)
    try:
        return "".join(next(filter(lambda x: "".join(x).upper() not in used_labels, itertools.product(*words)))).upper()
    except StopIteration as e:
        print("Failed to generate label")
        return None

    # longest_word = max(map(len, words))
    # extended_words = [
    #     list(word) + ['']*(longest_word-len(word)) for word in words
    # ]
    # list(itertools.combinations((itertools.chain(*list(zip(*extended_words)))), 3))


# --------------------------------- STRING UTILS --------------------------------


def split_camel_case(string:str) -> List[str]:
    """
    Turns "CLevelChangeInsights" into ['C', 'Level', 'Change ', 'Insights']
    :param string:
    :return:
    """
    l = [x for x in re.split(r'([A-Z])', string) if x]
    if not l:
        return l
    if not tail(l):
        return l

    upper_case_chrs = list(map(chr, range(ord("A"), ord("Z") + 1)))
    lower_case_chrs = list(map(chr, range(ord("a"), ord("z") + 1)))
    # print(upper_case_chrs)
    # print(lower_case_chrs)
    # print(head(l), head(tail(l)))
    if head(l) in upper_case_chrs and head(head(tail(l))) in upper_case_chrs:
        # print(1)
        return [head(l)] + split_camel_case("".join(tail(l)))
    elif head(l) in upper_case_chrs and head(head(tail(l))) in lower_case_chrs:
        # print(2)
        return ["{}{}".format(head(l), head(tail(l)))] + split_camel_case("".join(tail(tail(l))))
    else:
        # print(3)
        return [head(l), head(tail(l))] + split_camel_case("".join(tail(tail(l))))


def split_string_into_parts(string:str, num_of_parts:int) -> List:
    l = len(string)
    splittings = list(zip(
        [0] + list(map(lambda x: int(x * l / num_of_parts), range(1, num_of_parts))),
        list(map(lambda x: int(x * l / num_of_parts), range(1, num_of_parts))) + [None]
    ))
    return [
        "".join(list(itertools.islice(string, x, y))) for x, y in splittings
    ]


## ------------------------------- ENUM UTILS --------------------------------


class EnumWithCamelCasedNamesAsDefaultValue(Enum):
    def _generate_next_value_(name, start, count, last_values):
        return pydash.strings.camel_case(name)


class EnumWithNamesAsDefaultValue(Enum):
    def _generate_next_value_(name, start, count, last_values):
        return name


def merge_enum_values(values:List[Enum], merger:Callable[[list], object]=lambda values: ".".join(values)) -> object:
    return merger(list(map(lambda x: x.value, values)))


## ------------------------------- EQUALITY UTILS --------------------------------


def equal(x, y, equality_function=lambda a, b: a == b):
    if isinstance(x, list):
        return lists_are_equal(x, y)
    if isinstance(x, dict):
        return dicts_are_equal(x, y)
    return equality_function(x, y)


def lists_are_equal(l1:List, l2:List):
    return (
            isinstance(l1, list)
        and isinstance(l2, list)
        and (len(l1) == len(l2))
        and (all([t1 == t2 for t1, t2 in zip(map(type, l1), map(type, l2))]))
        and (all([equal(x, y) for x, y in zip(l1, l2)]) )
    )

def dicts_are_equal(d1, d2):
    return (
            isinstance(d1, dict)
        and isinstance(d2, dict)
        and lists_are_equal(sorted(d1.keys()), sorted(d2.keys()))
        and all([equal(d1[x], d2[x]) for x in d1.keys()])
    )


def merge_hashes(*hn):
    """
    For combining hashes: https://stackoverflow.com/questions/29435556/how-to-combine-hash-codes-in-in-python3
    :return:
    """
    only_1_hash = head(tail(hn)) is None
    h1 = head(hn)
    h2 = head(tail(hn))
    return hash(None) if not hn else (
        h1 if only_1_hash else
        merge_hashes(h1 ^ h2, *tail(tail(hn)))
    )


def hasher(x, hash_function=lambda a: hash(a)):
    if isinstance(x, list):
        return list_hasher(x)
    if isinstance(x, dict):
        return dict_hasher(x)
    return hash_function(x)


def list_hasher(l1:List):
    return merge_hashes(*[hasher(x) for x in l1])


def dict_hasher(d1:Mapping):
    return merge_hashes(
        list_hasher(sorted(d1.keys())),
        list_hasher([d1[k] for k in sorted(d1.keys())])
    )


def determine_weekly_ranges(dates):
    "Assumption ... first item in range is included, but last is not ..."
    first_date = min(dates)
    last_date = max(dates)
    # Make sure benning is sunday ... or move it back to last sunday ...
        # Move beginning to sunday ... if still same date ... use it ... (already sunday)
        #     If different date ... go back a week
    first_date_already_sunday = (first_date + pd.offsets.Week(n=0, weekday=6)) == first_date
    sunday_of_range_start = first_date if first_date_already_sunday else first_date + pd.offsets.Week(n=-1, weekday=6)
    last_date_already_sunday = (last_date + pd.offsets.Week(n=0, weekday=6)) == last_date
    sunday_of_range_end =  last_date + pd.offsets.Week(n=1, weekday=6) if last_date_already_sunday else last_date + pd.offsets.Week(n=0, weekday=6)
    l = list(zip(
        pd.date_range(
            start=sunday_of_range_start, end=sunday_of_range_end, freq="W-SUN", closed=None
        ),
        pd.date_range(
            start=sunday_of_range_start+ pd.offsets.Week(n=1, weekday=6), end=sunday_of_range_end + pd.offsets.Week(n=1, weekday=6), freq="W-SUN", closed=None
        )
    ))
    # Drop last item from list
    return l[0:-1]


if __name__ == '__main__':
    # json_to_image({"hello":"world"})
    # determine_weekly_ranges(weekly_dfs["date"].apply(pd.Timestamp))
    # determine_weekly_ranges([pd.Timestamp("2019-01-06"), pd.Timestamp("2019-02-03")])
    # determine_weekly_ranges([pd.Timestamp("2019-01-06"), pd.Timestamp("2019-02-02")])
    # determine_weekly_ranges([pd.Timestamp("2019-01-07"), pd.Timestamp("2019-02-02")])
    pass