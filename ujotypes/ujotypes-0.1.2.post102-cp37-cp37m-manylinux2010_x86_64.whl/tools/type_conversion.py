#
# Copyright (c) 2018-present, wobe-systems GmbH
#
# This source code is licensed under the MIT license found in the
# LICENSE file in the root directory of this source tree.
#

""" Type conversion helpers
"""

from ujotypes.variants import UjoUInt16, \
                              UjoUInt64, \
                              UjoStringC, \
                              UJO_VARIANT_NONE


def ujot_ujo_uint16_by_key(dictionary, key):
    """ Get dictionary entry as UjoUInt16

    If the key isn't found in the dictionary, UjoNone is returned.

    Args:
        dictionary (dict): The dictionary to search in
        key (Any): The key to search in dictionary with

    Returns:
        (UjoUInt16 or UjoNone): The Ujo variant
    """
    if key not in dictionary:
        return UJO_VARIANT_NONE
    return UjoUInt16(dictionary[key])


def ujot_ujo_uint64_by_key(dictionary, key):
    """ Get dictionary entry as UjoUInt64

    If the key isn't found in the dictionary, UjoNone is returned.

    Args:
        dictionary (dict): The dictionary to search in
        key (Any): The key to search in dictionary with

    Returns:
        (UjoUInt64 or UjoNone): The Ujo variant
    """
    if key not in dictionary:
        return UJO_VARIANT_NONE
    return UjoUInt64(dictionary[key])


def ujot_ujo_cstr_by_key(dictionary, key):
    """ Get dictionary entry as UjoStringC

    If the key isn't found in the dictionary, UjoNone is returned.

    Args:
        dictionary (dict): The dictionary to search in
        key (Any): The key to search in dictionary with

    Returns:
        (UjoStringC or UjoNone): The Ujo variant
    """
    if key not in dictionary:
        return UJO_VARIANT_NONE
    return UjoStringC(dictionary[key])
