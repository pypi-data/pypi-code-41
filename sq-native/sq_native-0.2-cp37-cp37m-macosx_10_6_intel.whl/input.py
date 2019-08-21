# -*- coding: utf-8 -*-
# Copyright (c) 2016, 2017, 2018, 2019 Sqreen. All rights reserved.
# Please refer to our terms for more information:
#
#     https://www.sqreen.io/terms.html
#
""" Binding for the WAF Input Data Structure
"""
from ctypes import (POINTER, Structure, byref, c_bool, c_char_p, c_int,
                    c_int64, c_size_t, c_uint64, c_void_p)

from . import lib
from ._compat import UNICODE_CLASS

PWI_INVALID = 0
PWI_SIGNED_NUMBER = 1 << 0
PWI_UNSIGNED_NUMBER = 1 << 1
PWI_STRING = 1 << 2
PWI_ARRAY = 1 << 3
PWI_MAP = 1 << 4


class C_PWInput(Structure):

    _fields_ = [
        ("name", c_char_p),
        ("value", c_void_p),
        ("nb_entries", c_uint64),
        ("type", c_int),
    ]


if lib is not None:
    lib.powerwaf_createArray.argstype = []
    lib.powerwaf_createArray.restype = C_PWInput
    lib.powerwaf_createInt.argstype = [c_int64]
    lib.powerwaf_createInt.restype = C_PWInput
    lib.powerwaf_createUint.argstype = [c_uint64]
    lib.powerwaf_createUint.restype = C_PWInput
    lib.powerwaf_createMap.restype = C_PWInput
    lib.powerwaf_createStringWithLength.argstype = [c_char_p, c_size_t]
    lib.powerwaf_createStringWithLength.restype = C_PWInput

    lib.powerwaf_addToPWInputArray.argtypes = [POINTER(C_PWInput), C_PWInput]
    lib.powerwaf_addToPWInputArray.restype = c_bool
    lib.powerwaf_addToPWInputMap.argtypes = [
        POINTER(C_PWInput), c_char_p, C_PWInput]
    lib.powerwaf_addToPWInputMap.restype = c_bool

    lib.powerwaf_freeInput.argtypes = [POINTER(C_PWInput), c_bool]
    lib.powerwaf_freeInput.restype = None


def create_array():
    if lib is None:
        return

    return lib.powerwaf_createArray()


def create_int(value):
    if lib is None:
        return

    return lib.powerwaf_createInt(c_int64(value))


def create_uint(value):
    if lib is None:
        return

    return lib.powerwaf_createUint(c_uint64(value))


def create_map():
    if lib is None:
        return

    return lib.powerwaf_createMap()


def create_string(value):
    if lib is None:
        return

    if isinstance(value, UNICODE_CLASS):
        value = value.encode("utf-8")

    if not isinstance(value, bytes):
        raise ValueError("value must be a string or bytes")

    return lib.powerwaf_createStringWithLength(value, len(value))


def append_to_array(array, value):
    if lib is None:
        return

    return lib.powerwaf_addToPWInputArray(byref(array), value)


def append_to_map(array, key, value):
    if lib is None:
        return

    if isinstance(key, UNICODE_CLASS):
        key = key.encode("utf-8")

    if not isinstance(key, bytes):
        raise ValueError("value must be a string or bytes")

    return lib.powerwaf_addToPWInputMap(byref(array), key, value)


def free(value):
    if lib is None:
        return

    lib.powerwaf_freeInput(byref(value), False)


def create(value, max_depth=32, ignore_none=True):
    """ Lower-level function to convert a Python value to input value
    """
    if isinstance(value, str) or isinstance(value, bytes):
        return create_string(value)

    if isinstance(value, bool):
        return create_uint(int(value))

    if isinstance(value, int):
        if value < 0:
            return create_int(value)
        else:
            return create_uint(value)

    if isinstance(value, list) or isinstance(value, tuple):
        if max_depth <= 0:
            raise ValueError("could not convert nested structure")

        obj = create_array()
        for item in value:
            if item is None and ignore_none:
                continue
            item_obj = create(item, max_depth=max_depth - 1)
            ret = append_to_array(obj, item_obj)
            if ret is False:
                free(item_obj)
        return obj

    if isinstance(value, dict):
        if max_depth <= 0:
            raise ValueError("could not convert nested structure")

        obj = create_map()
        for k, v in value.items():
            if v is None and ignore_none:
                continue
            item_obj = create(v, max_depth=max_depth - 1)
            ret = append_to_map(obj, k, item_obj)
            if ret is False:
                free(item_obj)
        return obj

    raise ValueError("Unknown value type {}".format(type(value)))


class PWInput:
    """
    Higher-level bridge between Python values and input values.
    """

    def __init__(self, obj):
        self._obj = obj

    def __del__(self):
        if self._obj is None:
            return
        free(self._obj)
        self._obj = None

    @classmethod
    def from_python(cls, value, max_depth=32, ignore_none=True):
        """ Convert a Python value to a PWInput.
        """
        return cls(create(value, max_depth=max_depth, ignore_none=ignore_none))

    def __repr__(self):
        return "<{} obj={!r}>".format(self.__class__.__name__, self._obj)
