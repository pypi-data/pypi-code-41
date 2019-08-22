#
# Copyright (c) 2018-present, wobe-systems GmbH
#
# This source code is licensed under the MIT license found in the
# LICENSE file in the root directory of this source tree.
#

""" Ujo Types container wrapper classes
"""
import collections.abc
import copy

import ujotypes
from .base import UjoBase
from .boolean import UjoBool
from .none import UjoNone, UJO_VARIANT_NONE
from .integer import UjoInt8, UjoUInt8, \
                     UjoInt16, UjoUInt16, \
                     UjoInt32, UjoUInt32, \
                     UjoInt64, UjoUInt64
from .float import UjoFloat64, \
                   UjoFloat32, \
                   UjoFloat16
from .string import UjoStringC, UjoStringUTF8
from .timestamp import UjoTimestamp


def variant_factory(variant_handle, owner=False):
    """ Put an Ujo variant handle inside a class

    Args:
        variant_handle (int): C-API variant handle
        owner (bool): indicates if the class wrapper owns the handle

    Returns:
        (UjoBase): A variant wrapper class containing the handle
    """
    variant_type = ujotypes.ujot_variant_get_type(variant_handle)

    type_to_class = {
        (ujotypes.UJOT_VARIANT_TYPE_BOOL, 0): UjoBool,
        (ujotypes.UJOT_VARIANT_TYPE_NONE, 0): UjoNone,
        (ujotypes.UJOT_VARIANT_TYPE_UINT8, 0): UjoUInt8,
        (ujotypes.UJOT_VARIANT_TYPE_INT8, 0): UjoInt8,
        (ujotypes.UJOT_VARIANT_TYPE_UINT16, 0): UjoUInt16,
        (ujotypes.UJOT_VARIANT_TYPE_INT16, 0): UjoInt16,
        (ujotypes.UJOT_VARIANT_TYPE_UINT32, 0): UjoUInt32,
        (ujotypes.UJOT_VARIANT_TYPE_INT32, 0): UjoInt32,
        (ujotypes.UJOT_VARIANT_TYPE_UINT64, 0): UjoUInt64,
        (ujotypes.UJOT_VARIANT_TYPE_INT64, 0): UjoInt64,
        (ujotypes.UJOT_VARIANT_TYPE_FLOAT64, 0): UjoFloat64,
        (ujotypes.UJOT_VARIANT_TYPE_FLOAT32, 0): UjoFloat32,
        (ujotypes.UJOT_VARIANT_TYPE_FLOAT16, 0): UjoFloat16,
        (ujotypes.UJOT_VARIANT_TYPE_STRING, ujotypes.UJOT_STRING_TYPE_C):
            UjoStringC,
        (ujotypes.UJOT_VARIANT_TYPE_STRING, ujotypes.UJOT_STRING_TYPE_UTF8):
            UjoStringUTF8,
        (ujotypes.UJOT_VARIANT_TYPE_TIMESTAMP, 0): UjoTimestamp,
        (ujotypes.UJOT_VARIANT_TYPE_LIST, 0): UjoList,
        (ujotypes.UJOT_VARIANT_TYPE_MAP, 0): UjoMap,
    }

    if variant_type not in type_to_class.keys():
        raise ValueError('handle type not supported')

    return type_to_class[variant_type](variant_handle=variant_handle,
                                       owner=owner)


def read_file(filename):
    """Read Ujo file from disc to in memory Ujo Types variant

    Args:
        filename (str) : Full path of file to read

    Returns:
        (UjoTypesBase): Ujo Types variant instance
    """
    variant_handle = ujotypes.ujot_read_from_file(filename)
    return variant_factory(variant_handle)


def write_file(variant, filename):
    """Write in memory Ujo Types variant to Ujo file on disk

    Args:
        variant (UjoTypesBase) : List or map Ujo Types variant
        filename (str) : Full path of file to write
    """
    ujotypes.ujot_write_to_file(variant.handle, filename)


def read_buffer(buffer):
    """Read Ujo container from in memory buffer to in memory Ujo Types variant

    Args:
        buffer (bytes) : Binary buffer containing an Ujo container

    Returns:
        (UjoTypesBase): Ujo Types variant instance
    """
    variant_handle = ujotypes.ujot_read_from_buffer(buffer)
    return variant_factory(variant_handle)


def write_buffer(variant):
    """Write in memory Ujo Types variant to in memory binary buffer

    Args:
        variant (UjoTypesBase) : List or map Ujo Types variant

    Returns:
        (bytes): Binary buffer containing Ujo container
    """
    return ujotypes.ujot_write_to_buffer(variant.handle)


class UjoList(UjoBase, collections.abc.MutableSequence):  # pylint: disable=too-many-ancestors
    """ Wrap Ujo list

    Args:
        variant_handle (int) : A handle returned by the Ujo C-API
            representing a variant. If None is passed a new handle is
            created.
        owner (bool) : Indicates if the class owns the variant
    """

    variant_type = ujotypes.UJOT_VARIANT_TYPE_LIST

    def __init__(self, variant_handle=None, owner=False):
        if variant_handle is None:
            variant_handle = ujotypes.ujot_variant_new_list()
            owner = True

        UjoBase.__init__(self, variant_handle=variant_handle, owner=owner)

    @property
    def value(self):
        """ (list): Python list
        """
        return self.as_pyobject()

    def __repr__(self):
        items = ', '.join(repr(item) for item in self)
        return f"{self.__class__.__name__}({items})"

    def __bytes__(self):
        """ (bytes): Buffer representation of UJO container
        """
        return write_buffer(self)

    def __contains__(self, value):
        """ Check membership of Ujo variant element in list having same
        type and value

        Args:
            value (UjoBase): The Ujo variant to check membership of

        Returns:
            (bool): True if element is in list, False otherwise
        """
        index = ujotypes.ujot_variant_list_contains(self.handle, value.handle)
        if index != ujotypes.UJOT_LIST_INDEX_UNKNOWN:
            return True
        return False

    def __copy__(self):
        return self.copy(deepcopy=False)

    def __deepcopy__(self, memodict):
        return self.copy(deepcopy=True)

    def copy(self, deepcopy=False):
        """ Create a copy of the ujo list

        Args:
            deepcopy (bool): create a copy of contained items (recursively), default: False

        Returns:
            UjoList: a new instance of an UjoList holding the same (or a copy of) the content
        """
        cpy = UjoList()
        for item in self:
            if deepcopy:
                item = copy.deepcopy(item)
            cpy.append(item)
        return cpy

    def __eq__(self, other):
        if type(self) == type(other):   # pylint: disable=unidiomatic-typecheck
            return (
                len(self) == len(other)
                and all(item == other_item for item, other_item in zip(self, other))
            )
        return False

    def __len__(self):
        """ Number of items in the list

        Returns:
            (int): item count
        """
        return ujotypes.ujot_variant_list_get_size(self.handle)

    def __setitem__(self, index, value):
        """ Replace an item in the list

        Args:
            index (int): list index to replace
            value (UjoBase): an Ujo variant
        """
        ujotypes.ujot_variant_list_set_item(self.handle, value.handle, index)

    def __getitem__(self, index):
        """ Read an item from an index position

        Args:
            index (int): item index

        Returns:
            (UjoBase): item from the list at index position
        """
        if index < 0:
            index += len(self)
        try:
            variant_handle = ujotypes.ujot_variant_list_get_item(self.handle, index)
        except ujotypes.ujotypesError_INDEX_OUT_OF_RANGE:
            # replace UjoTypes index out of range exception by Python standard index error
            raise IndexError

        return variant_factory(variant_handle)

    def __delitem__(self, index):
        """ Delete an item from the list

        Args:
            index (int): item index
        """
        if index < 0:
            index += len(self)
        ujotypes.ujot_variant_list_delete_item(self.handle, index)

    def append(self, value):
        """ Append an Ujo Types element to the end of the list

        Args:
            value (UjoBase): The Ujo variant to be added to the list

        Raises:
            TypeError: If objects other than objects derived from UjoBase
                       are appended
        """
        if not isinstance(value, UjoBase):
            raise TypeError('Ujo list only accepts elements derived from '
                            'UjoBase. Element is: {}'
                            .format(value.__class__.__name__))
        ujotypes.ujot_variant_list_append(self.handle, value.handle)

    def count(self, value):
        """ Return number of occurrences of Ujo elements in list having same
        type and value

        Args:
            value (UjoBase): The Ujo variant to count occurrences for

        Returns:
            (int): Number of occurrences
        """
        element_type = value.type
        element_value = value.value
        return sum((1 for element in self
                    if element.type == element_type
                    and element.value == element_value))

    def index(self, value, start=0, stop=None):
        """ Return first index of Ujo element in list having same type and value

        For searching the element just inside a slice of the list a start
        and stop index can be passed to the index function. Negative numbers
        to count from the end of the list are allowed.

        Args:
            value (UjoBase): The Ujo variant to return index for
            index (int): Index of element to insert before
            start (int): Optional index to start searching at
            stop (int): Optional index to stop searching  at

        Returns:
            (int): Index of first element in list

        Raises:
            ValueError: If element of same type and value is not present
        """
        if start is None:
            start = 0
        elif start < 0:
            start = max(len(self) + start, 0)

        if stop is None:
            stop = len(self)
        elif stop < 0:
            stop += len(self)

        # convert from python slice stop to c type stop
        stop = stop - 1

        index = ujotypes.ujot_variant_list_contains_in_subset(self.handle,
                                                              value.handle,
                                                              start,
                                                              stop)

        if index == ujotypes.UJOT_LIST_INDEX_UNKNOWN:
            raise ValueError
        return index

    def insert(self, index, value):
        """ Insert an Ujo variant element before index

        Args:
            index (int): Index of element to insert before
            value (UjoBase): The Ujo variant to be added to the list

        Raises:
            TypeError: If objects other than objects derived from UjoBase
                       are inserted
        """
        if not isinstance(value, UjoBase):
            raise TypeError('Ujo list only accepts elements derived from '
                            'UjoBase. Element is: {}'
                            .format(value.__class__.__name__))
        ujotypes.ujot_variant_list_insert(self.handle, value.handle, index)

    def get_variant(self, index, default=UjoNone, constraint=None):
        """ Read an item from an index position with default fallback and
        constraint check

        Args:
            index (int): item index
            default (UjoBase): default fallback value
            constraint (class): class type as constraint for the list item

        Returns:
            (UjoBase): item from the list at index position or default
        """
        if index < 0:
            index += len(self)

        if 0 <= index < len(self):
            item = self[index]
            if (constraint is None) or isinstance(item, constraint):
                return item

        if default is UjoNone:
            return UJO_VARIANT_NONE

        return default

    def get_value(self, index, default=None, constraint=None):
        """ Read a value from an index position with default fallback and
        constraint check

        Args:
            index (int): item index
            default (any): default fallback value
            constraint (class): class type as constraint for the list item

        Returns:
            (UjoBase): item value from the list at index position or default
        """
        result = self.get_variant(index, default, constraint)

        if isinstance(result, UjoBase):
            return result.value

        return result

    def set_value(self, index, value, value_type):
        """ Replace a value at an index position

        The value has to fit the value_type.
        If the value is an instance of UjoBase, the value_type is ignored.

        Args:
            index (int): item index
            value (any): the value to set
            value_type (class): class type for the list item
        """
        if isinstance(value, UjoBase):
            variant_value = value
        else:
            variant_value = value_type(value)

        self[index] = variant_value

    def as_pyobject(self) -> list:
        """Converts the Ujo container to its corresponding python representation.

        Returns:
            list: Python representation of Ujo object
        """
        def to_py(ujo):
            return ujo.as_pyobject() if isinstance(ujo, UjoContainer) else ujo.value

        return [to_py(item) for item in self]


class UjoMap(UjoBase, collections.abc.MutableMapping):  # pylint: disable=too-many-ancestors
    """ Class wrapper for Ujo Variant map

    Args:
        variant_handle (int) : A handle returned by the Ujo C-API
            representing a map variant. If None is passed a new handle is
            created.
        owner (bool) : Indicates if the class owns the variant
    """

    variant_type = ujotypes.UJOT_VARIANT_TYPE_MAP

    def __init__(self, variant_handle=None, owner=True):
        if variant_handle is None:
            variant_handle = ujotypes.ujot_variant_new_map()
            owner = True

        UjoBase.__init__(self, variant_handle=variant_handle, owner=owner)

    @property
    def value(self):
        """ (dict): Python dictionary
        """
        return self.as_pyobject()

    def __repr__(self):
        items = ', '.join(f"{repr(k)}={repr(v)}" for k, v in self.items())
        return f"{self.__class__.__name__}({items})"

    def __bytes__(self):
        """ (bytes): Buffer representation of UJO container
        """
        return write_buffer(self)

    def __copy__(self):
        return self.copy(deepcopy=False)

    def __deepcopy__(self, memodict):
        return self.copy(deepcopy=True)

    def copy(self, deepcopy=False):
        """ Create a copy of the ujo map

        Args:
            deepcopy (bool): create a copy of contained items (recursively), default: False

        Returns:
            UjoMap: a new instance of an UjoMap holding the same (or a copy of) the content
        """
        cpy = UjoMap()
        for key, item in self.items():
            if deepcopy:
                item = copy.deepcopy(item)
            cpy[key] = item
        return cpy

    def __eq__(self, other):
        if type(self) == type(other):   # pylint: disable=unidiomatic-typecheck
            return self.items() == other.items()

        return False

    def __len__(self):
        """ Return the number of items in the dictionary

        Returns:
            (int): Number of items
        """
        return ujotypes.ujot_variant_map_get_size(self.handle)

    def __iter__(self):
        """ Return an iterator over the keys of the map

        Returns:
            (UjoBase): keys of map as an instance of the Ujo Variant
        """
        ujotypes.ujot_variant_map_first(self.handle)
        while True:
            key_value_tuple = ujotypes.ujot_variant_map_next(self.handle)
            if key_value_tuple:
                yield variant_factory(key_value_tuple[0])
            else:
                break

    def __setitem__(self, key, value):
        """ Set or add a key value pair to the map

        Args:
            key (UjoBase): an Ujo variant instance
            value (UjoBase): an Ujo variant instance
        """
        ujotypes.ujot_variant_map_set(self.handle, key.handle, value.handle)

    def __getitem__(self, key):
        """ Get item from map by its key

        Args:
            key (UjoBase): an Ujo variant instance

        Returns:
            (UjoBase): item from the map by key
        """
        try:
            variant_handle = ujotypes.ujot_variant_map_get(self.handle,
                                                           key.handle)
        except ujotypes.ujotypesError_KEY_NOT_EXISTS:
            # replace UjoTypes key not exists exception by Python standard KeyError
            raise KeyError

        return variant_factory(variant_handle)

    def __delitem__(self, key):
        """ Delete key value pair from map

        Args:
            key (UJIVariantBase): an Ujo variant instance
        """
        ujotypes.ujot_variant_map_delete(self.handle, key.handle)

    def get_variant(self, key, default=UjoNone, constraint=None,
                    key_type=UjoStringC):
        """ Get item from map by its key with default fallback and constraint
        check

        The key has to fit the key_type.
        If the key is an instance of UjoBase, the key_type is ignored.

        Args:
            key (any): the key to find value with
            default (UjoBase): default fallback value
            constraint (class): class type as constraint for the map item
            key_type (class): class type for the key in the map

        Returns:
            (UjoBase): item from the map or default
        """
        if not isinstance(key, UjoBase):
            key = key_type(key)

        item = self.get(key, None)
        if (item is not None) and ((constraint is None)
                                   or isinstance(item, constraint)):
            return item

        if default is UjoNone:
            return UJO_VARIANT_NONE

        return default

    def get_value(self, key, default=None, constraint=None,
                  key_type=UjoStringC):
        """ Get value from map by its key with default fallback and constraint
        check

        The key has to fit the key_type.
        If the key is an instance of UjoBase, the key_type is ignored.

        Args:
            key (any): the key to find value with
            default (any): default fallback value
            constraint (class): class type as constraint for the map item
            key_type (class): class type for the key in the map

        Returns:
            (any): value of item from the map or default
        """
        result = self.get_variant(key, default, constraint, key_type)

        if isinstance(result, UjoBase):
            return result.value

        return result

    def set_value(self, key, value, value_type, key_type=UjoStringC):
        """ Set or add a key value pair to the map

        The key has to fit the key_type.
        The value has to fit the value_type.
        If the key is an instance of UjoBase, the key_type is ignored.
        If the value is an instance of UjoBase, the value_type is ignored.

        Args:
            key (any): the key to store the value with
            value (any): the value to store
            value_type (class): class type for the map item
            key_type (class): class type for the key in the map
        """
        if isinstance(key, UjoBase):
            variant_key = key
        else:
            variant_key = key_type(key)

        if isinstance(value, UjoBase):
            variant_value = value
        else:
            variant_value = value_type(value)

        self[variant_key] = variant_value

    def as_pyobject(self) -> dict:
        """Converts an Ujo container to its corresponding python representation.

        Duplicate keys of different Ujo key types will only create
        one entry in the Python dictionary with the value of the
        Ujo key value pair evaluated last.

        Returns:
            dict: Python representation of Ujo object
        """
        def to_py(ujo):
            return ujo.as_pyobject() if isinstance(ujo, UjoContainer) else ujo.value

        return {key.value: to_py(item) for key, item in self.items()}


UjoContainer = (UjoList, UjoMap)  # pylint: disable=C0103
