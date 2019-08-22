#
# Copyright (c) 2018-present, wobe-systems GmbH
#
# This source code is licensed under the MIT license found in the
# LICENSE file in the root directory of this source tree.
#

""" Ujo Types Floats wrapper class
"""

import ujotypes
from .base import UjoBase


class UjoFloat64(UjoBase):
    """ Wrap Ujo float64 type

    Args:
        value (float, None) : The value can be None if a valid
            variant handle is passed.
        variant_handle (int) : A handle returned by the Ujo C-API
            representing a variant. If a handle is passed
            the value is ignored.
        owner (bool) : Indicates if the class owns the variant
    """

    variant_type = ujotypes.UJOT_VARIANT_TYPE_FLOAT64

    def __init__(self, value=None, variant_handle=None, owner=False):
        if not isinstance(value, float) and value is not None:
            raise TypeError("{} doesn't accept values of type {}"
                            .format(self.__class__.__name__,
                                    value.__class__.__name__))

        if variant_handle is None:
            variant_handle = ujotypes.ujot_variant_new_float64(value)
            owner = True

        UjoBase.__init__(self, variant_handle=variant_handle, owner=owner)

    @property
    def value(self):
        """ (float): Current Value
        """
        return ujotypes.ujot_variant_as_float64(self.handle)


class UjoFloat32(UjoBase):
    """ Wrap Ujo float32 type

    Args:
        value (float, None) : The value can be None if a valid
            variant handle is passed.
        variant_handle (int) : A handle returned by the Ujo C-API
            representing a variant. If a handle is passed
            the value is ignored.
        owner (bool) : Indicates if the class owns the variant
    """

    variant_type = ujotypes.UJOT_VARIANT_TYPE_FLOAT32

    def __init__(self, value=None, variant_handle=None, owner=False):
        if not isinstance(value, float) and value is not None:
            raise TypeError("{} doesn't accept values of type {}"
                            .format(self.__class__.__name__,
                                    value.__class__.__name__))

        if variant_handle is None:
            variant_handle = ujotypes.ujot_variant_new_float32(value)
            owner = True

        UjoBase.__init__(self, variant_handle=variant_handle, owner=owner)

    @property
    def value(self):
        """ (float): Current Value
        """
        return ujotypes.ujot_variant_as_float32(self.handle)


class UjoFloat16(UjoBase):
    """ Wrap Ujo float16 type

    Args:
        value (float, None) : The value can be None if a valid
            variant handle is passed.
        variant_handle (int) : A handle returned by the Ujo C-API
            representing a variant. If a handle is passed
            the value is ignored.
        owner (bool) : Indicates if the class owns the variant
    """

    variant_type = ujotypes.UJOT_VARIANT_TYPE_FLOAT16

    def __init__(self, value=None, variant_handle=None, owner=False):
        if not isinstance(value, float) and value is not None:
            raise TypeError("{} doesn't accept values of type {}"
                            .format(self.__class__.__name__,
                                    value.__class__.__name__))

        if variant_handle is None:
            value_16 = ujotypes.ujot_float_to_half(value)
            variant_handle = ujotypes.ujot_variant_new_float16(value_16)
            owner = True

        UjoBase.__init__(self, variant_handle=variant_handle, owner=owner)

    @property
    def value(self):
        """ (float): Current Value
        """
        value_16 = ujotypes.ujot_variant_as_float16(self.handle)
        value_float = ujotypes.ujot_half_to_float(value_16)
        return value_float
