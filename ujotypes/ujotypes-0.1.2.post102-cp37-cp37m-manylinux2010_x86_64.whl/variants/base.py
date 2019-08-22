#
# Copyright (c) 2018-present, wobe-systems GmbH
#
# This source code is licensed under the MIT license found in the
# LICENSE file in the root directory of this source tree.
#

"""
Ujo Types variants

This module provides an object wrapper to simplify the usage of Ujo variants
and automate reference counting.
"""

import ujotypes


class UjoBase:   # pylint: disable=too-few-public-methods
    """ General handling of Ujo Variants

    Args:
        variant_handle (int) : A handle returned by the Ujo C-API
                                representing a variant
        owner (bool) : Indicates if the class takes the ownership of the variant handle
    """

    variant_type = 0        # The base class doesn't have a type
    variant_subtype = 0     # Per default there is no subtype

    def __init__(self, variant_handle, owner=False):
        if not isinstance(variant_handle, int):
            raise TypeError

        if ujotypes.ujot_variant_get_type(variant_handle) != \
                (self.variant_type, self.variant_subtype):
            raise TypeError("{} doesn't accept variant handles of type {}"
                            .format(self.__class__.__name__,
                                    self._variant_handle_name(variant_handle)))

        self.__handle = variant_handle

        if not owner:
            ujotypes.ujot_variant_incref(self.__handle)

    @property
    def refcount(self):
        """ (int): Current reference count of Ujo variant
        """
        return ujotypes.ujot_variant_get_refcount(self.__handle)

    @property
    def handle(self):
        """ (int): C API handle of the variant
        """
        return self.__handle

    @property
    def value(self):
        """ Abstract method to be implemented in concrete classes.
        """
        raise Exception("abstract method called")

    @property
    def type(self):
        """ (int): Type constant of the variant
        """
        variant_type, _ = ujotypes.ujot_variant_get_type(self.__handle)
        return variant_type

    @property
    def subtype(self):
        """ (int): Subtype constant of the variant
        """
        _, variant_subtype = ujotypes.ujot_variant_get_type(self.__handle)
        return variant_subtype

    def __del__(self):
        try:
            if isinstance(self.__handle, int):
                ujotypes.ujot_variant_decref(self.__handle)
        except AttributeError:
            # should class instantiation fail the instance variable
            # __handle is not present
            pass

    def __str__(self):
        return str(self.value)

    def __eq__(self, other):
        if type(other) is type(self):
            return self.value == other.value
        return False

    def __ne__(self, other):
        return not self == other

    def __repr__(self):
        return f"{self.__class__.__name__}({repr(self.value)})"

    def __copy__(self):
        return self

    def __deepcopy__(self, memodict):
        return self

    @staticmethod
    def _variant_handle_name(variant_handle):
        """ Determine the type name of an Ujo variant handle

        Args:
            variant_handle (int): C-API variant handle

        Returns:
            (str): Type name of the variant handle
        """

        no_sub_type = 0
        type_to_name = {
            (ujotypes.UJOT_VARIANT_TYPE_BOOL, no_sub_type): 'Bool',
            (ujotypes.UJOT_VARIANT_TYPE_UINT8, no_sub_type): 'UInt8',
            (ujotypes.UJOT_VARIANT_TYPE_INT8, no_sub_type): 'Int8',
            (ujotypes.UJOT_VARIANT_TYPE_UINT16, no_sub_type): 'UInt16',
            (ujotypes.UJOT_VARIANT_TYPE_INT16, no_sub_type): 'Int16',
            (ujotypes.UJOT_VARIANT_TYPE_UINT32, no_sub_type): 'UInt32',
            (ujotypes.UJOT_VARIANT_TYPE_INT32, no_sub_type): 'Int32',
            (ujotypes.UJOT_VARIANT_TYPE_UINT64, no_sub_type): 'UInt64',
            (ujotypes.UJOT_VARIANT_TYPE_INT64, no_sub_type): 'Int64',
            (ujotypes.UJOT_VARIANT_TYPE_FLOAT64, no_sub_type): 'Float64',
            (ujotypes.UJOT_VARIANT_TYPE_FLOAT32, no_sub_type): 'Float32',
            (ujotypes.UJOT_VARIANT_TYPE_FLOAT16, no_sub_type): 'Float16',
            (ujotypes.UJOT_VARIANT_TYPE_STRING, ujotypes.UJOT_STRING_TYPE_C): 'String-C',
            (ujotypes.UJOT_VARIANT_TYPE_STRING, ujotypes.UJOT_STRING_TYPE_UTF8): 'String-UTF8',
            (ujotypes.UJOT_VARIANT_TYPE_LIST, no_sub_type): 'List'
        }

        type_and_subtype = ujotypes.ujot_variant_get_type(variant_handle)
        type_name = type_to_name.get(type_and_subtype, 'Unknown')

        return type_name
