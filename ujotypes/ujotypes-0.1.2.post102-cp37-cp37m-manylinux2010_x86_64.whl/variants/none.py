#
# Copyright (c) 2018-present, wobe-systems GmbH
#
# This source code is licensed under the MIT license found in the
# LICENSE file in the root directory of this source tree.
#

""" Ujo Types None wrapper class
"""

import ujotypes
from .base import UjoBase


class UjoNone(UjoBase):
    """ Wrap Ujo None type

    Args:
        variant_handle (int) : A handle returned by the Ujo C-API
            representing a variant. If no handle is passed
            a new handle will be created.
        owner (bool) : Indicates if the class owns the variant
    """

    variant_type = ujotypes.UJOT_VARIANT_TYPE_NONE

    def __init__(self, variant_handle=None, owner=False):
        if variant_handle is None:
            variant_handle = ujotypes.ujot_variant_new_none()
            owner = True

        UjoBase.__init__(self, variant_handle=variant_handle, owner=owner)

    @property
    def value(self):
        """ (None): Current Value
        """
        return None


UJO_VARIANT_NONE = UjoNone()
