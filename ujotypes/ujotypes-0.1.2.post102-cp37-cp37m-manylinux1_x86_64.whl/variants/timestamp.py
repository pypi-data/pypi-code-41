#
# Copyright (c) 2018-present, wobe-systems GmbH
#
# This source code is licensed under the MIT license found in the
# LICENSE file in the root directory of this source tree.
#

""" Ujo Types Timestamp wrapper class
"""

import datetime

import ujotypes
from .base import UjoBase


class UjoTimestamp(UjoBase):
    """ Wrap Ujo Timestamp type

    Args:
        value (datetime, None) : The value can be None if a valid
            variant handle is passed.
        variant_handle (int) : A handle returned by the Ujo C-API
            representing a variant. If a handle is passed
            the value is ignored.
        owner (bool) : Indicates if the class owns the variant
    """

    variant_type = ujotypes.UJOT_VARIANT_TYPE_TIMESTAMP

    def __init__(self, value=None, variant_handle=None, owner=False):
        if not isinstance(value, datetime.datetime) and value is not None:
            raise TypeError("{} doesn't accept values of type {}"
                            .format(self.__class__.__name__,
                                    value.__class__.__name__))

        if variant_handle is None:
            variant_handle = \
                ujotypes.ujot_variant_new_timestamp(value.year, value.month, value.day,
                                                    value.hour, value.minute, value.second,
                                                    value.microsecond)
            owner = True

        UjoBase.__init__(self, variant_handle=variant_handle, owner=owner)

    @property
    def value(self):
        """ (datetime): Current Value
        """
        year, month, day, hour, minute, second, microsecond = \
            ujotypes.ujot_variant_as_timestamp(self.handle)

        return datetime.datetime(year, month, day, hour, minute, second, microsecond)
