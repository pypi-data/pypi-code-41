#
# Copyright (c) 2018-present, wobe-systems GmbH
#
# This source code is licensed under the MIT license found in the
# LICENSE file in the root directory of this source tree.
#

""" Ujo Types Integer wrapper class
"""

import ujotypes
from .base import UjoBase


class UjoUInt8(UjoBase):
    """ Wrap Ujo uint8 type

    Args:
        value (int, None) : The value can be None if a valid
            variant handle is passed.
        variant_handle (int) : A handle returned by the Ujo C-API
            representing a variant. If a handle is passed
            the value is ignored.
        owner (bool) : Indicates if the class owns the variant
    """

    variant_type = ujotypes.UJOT_VARIANT_TYPE_UINT8

    def __init__(self, value=None, variant_handle=None, owner=False):
        if not isinstance(value, int) and value is not None:
            raise TypeError("{} doesn't accept values of type {}"
                            .format(self.__class__.__name__,
                                    value.__class__.__name__))

        if variant_handle is None:
            variant_handle = ujotypes.ujot_variant_new_uint8(value)
            owner = True

        UjoBase.__init__(self, variant_handle=variant_handle, owner=owner)

    @property
    def value(self):
        """ (int): Current Value
        """
        return ujotypes.ujot_variant_as_uint8(self.handle)


class UjoInt8(UjoBase):
    """ Wrap Ujo int8 type

    Args:
        value (int, None) : The value can be None if a valid
            variant handle is passed.
        variant_handle (int) : A handle returned by the Ujo C-API
            representing a variant. If a handle is passed
            the value is ignored.
        owner (bool) : Indicates if the class owns the variant
    """

    variant_type = ujotypes.UJOT_VARIANT_TYPE_INT8

    def __init__(self, value=None, variant_handle=None, owner=False):
        if not isinstance(value, int) and value is not None:
            raise TypeError("{} doesn't accept values of type {}"
                            .format(self.__class__.__name__,
                                    value.__class__.__name__))

        if variant_handle is None:
            variant_handle = ujotypes.ujot_variant_new_int8(value)
            owner = True

        UjoBase.__init__(self, variant_handle=variant_handle, owner=owner)

    @property
    def value(self):
        """ (int): Current Value
        """
        return ujotypes.ujot_variant_as_int8(self.handle)


class UjoUInt16(UjoBase):
    """ Wrap Ujo uint16 type

    Args:
        value (int, None) : The value can be None if a valid
            variant handle is passed.
        variant_handle (int) : A handle returned by the Ujo C-API
            representing a variant. If a handle is passed
            the value is ignored.
        owner (bool) : Indicates if the class owns the variant
    """

    variant_type = ujotypes.UJOT_VARIANT_TYPE_UINT16

    def __init__(self, value=None, variant_handle=None, owner=False):
        if not isinstance(value, int) and value is not None:
            raise TypeError("{} doesn't accept values of type {}"
                            .format(self.__class__.__name__,
                                    value.__class__.__name__))

        if variant_handle is None:
            variant_handle = ujotypes.ujot_variant_new_uint16(value)
            owner = True

        UjoBase.__init__(self, variant_handle=variant_handle, owner=owner)

    @property
    def value(self):
        """ (int): Current Value
        """
        return ujotypes.ujot_variant_as_uint16(self.handle)


class UjoInt16(UjoBase):
    """ Wrap Ujo int16 type

    Args:
        value (int, None) : The value can be None if a valid
            variant handle is passed.
        variant_handle (int) : A handle returned by the Ujo C-API
            representing a variant. If a handle is passed
            the value is ignored.
        owner (bool) : Indicates if the class owns the variant
    """

    variant_type = ujotypes.UJOT_VARIANT_TYPE_INT16

    def __init__(self, value=None, variant_handle=None, owner=False):
        if not isinstance(value, int) and value is not None:
            raise TypeError("{} doesn't accept values of type {}"
                            .format(self.__class__.__name__,
                                    value.__class__.__name__))

        if variant_handle is None:
            variant_handle = ujotypes.ujot_variant_new_int16(value)
            owner = True

        UjoBase.__init__(self, variant_handle=variant_handle, owner=owner)

    @property
    def value(self):
        """ (int): Current Value
        """
        return ujotypes.ujot_variant_as_int16(self.handle)


class UjoUInt32(UjoBase):
    """ Wrap Ujo uint32 type

    Args:
        value (int, None) : The value can be None if a valid
            variant handle is passed.
        variant_handle (int) : A handle returned by the Ujo C-API
            representing a variant. If a handle is passed
            the value is ignored.
        owner (bool) : Indicates if the class owns the variant
    """

    variant_type = ujotypes.UJOT_VARIANT_TYPE_UINT32

    def __init__(self, value=None, variant_handle=None, owner=False):
        if not isinstance(value, int) and value is not None:
            raise TypeError("{} doesn't accept values of type {}"
                            .format(self.__class__.__name__,
                                    value.__class__.__name__))

        if variant_handle is None:
            variant_handle = ujotypes.ujot_variant_new_uint32(value)
            owner = True

        UjoBase.__init__(self, variant_handle=variant_handle, owner=owner)

    @property
    def value(self):
        """ (int): Current Value
        """
        return ujotypes.ujot_variant_as_uint32(self.handle)


class UjoInt32(UjoBase):
    """ Wrap Ujo int32 type

    Args:
        value (int, None) : The value can be None if a valid
            variant handle is passed.
        variant_handle (int) : A handle returned by the Ujo C-API
            representing a variant. If a handle is passed
            the value is ignored.
        owner (bool) : Indicates if the class owns the variant
    """

    variant_type = ujotypes.UJOT_VARIANT_TYPE_INT32

    def __init__(self, value=None, variant_handle=None, owner=False):
        if not isinstance(value, int) and value is not None:
            raise TypeError("{} doesn't accept values of type {}"
                            .format(self.__class__.__name__,
                                    value.__class__.__name__))

        if variant_handle is None:
            variant_handle = ujotypes.ujot_variant_new_int32(value)
            owner = True

        UjoBase.__init__(self, variant_handle=variant_handle, owner=owner)

    @property
    def value(self):
        """ (int): Current Value
        """
        return ujotypes.ujot_variant_as_int32(self.handle)


class UjoUInt64(UjoBase):
    """ Wrap Ujo uint64 type

    Args:
        value (int, None) : The value can be None if a valid
            variant handle is passed.
        variant_handle (int) : A handle returned by the Ujo C-API
            representing a variant. If a handle is passed
            the value is ignored.
        owner (bool) : Indicates if the class owns the variant
    """

    variant_type = ujotypes.UJOT_VARIANT_TYPE_UINT64

    def __init__(self, value=None, variant_handle=None, owner=False):
        if not isinstance(value, int) and value is not None:
            raise TypeError("{} doesn't accept values of type {}"
                            .format(self.__class__.__name__,
                                    value.__class__.__name__))

        if variant_handle is None:
            variant_handle = ujotypes.ujot_variant_new_uint64(value)
            owner = True

        UjoBase.__init__(self, variant_handle=variant_handle, owner=owner)

    @property
    def value(self):
        """ (int): Current Value
        """
        return ujotypes.ujot_variant_as_uint64(self.handle)


class UjoInt64(UjoBase):
    """ Wrap Ujo int64 type

    Args:
        value (int, None) : The value can be None if a valid
            variant handle is passed.
        variant_handle (int) : A handle returned by the Ujo C-API
            representing a variant. If a handle is passed
            the value is ignored.
        owner (bool) : Indicates if the class owns the variant
    """

    variant_type = ujotypes.UJOT_VARIANT_TYPE_INT64

    def __init__(self, value=None, variant_handle=None, owner=False):
        if not isinstance(value, int) and value is not None:
            raise TypeError("{} doesn't accept values of type {}"
                            .format(self.__class__.__name__,
                                    value.__class__.__name__))

        if variant_handle is None:
            variant_handle = ujotypes.ujot_variant_new_int64(value)
            owner = True

        UjoBase.__init__(self, variant_handle=variant_handle, owner=owner)

    @property
    def value(self):
        """ (int): Current Value
        """
        return ujotypes.ujot_variant_as_int64(self.handle)
