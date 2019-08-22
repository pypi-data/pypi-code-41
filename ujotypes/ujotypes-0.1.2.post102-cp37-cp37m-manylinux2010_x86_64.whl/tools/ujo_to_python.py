#
# Copyright (c) 2018-present, wobe-systems GmbH
#
# This source code is licensed under the MIT license found in the
# LICENSE file in the root directory of this source tree.
#

""" Converting Ujo Container objects to Python Object
"""

from ujotypes.variants import (
    UjoVariant,
    UjoContainer,
)


def ujo_to_python(variant: UjoVariant) -> object:
    """Recursively convert Ujo container object to native Python objects

    Args:
        variant (UjoVariant): Instance of any Ujo object to convert

    Returns:
        Union[list,dict] : Python object representation of Ujo variant and all
                           contained subobjects
    """
    if isinstance(variant, UjoContainer):
        python_object = variant.as_pyobject()
    else:
        python_object = variant.value
    return python_object
