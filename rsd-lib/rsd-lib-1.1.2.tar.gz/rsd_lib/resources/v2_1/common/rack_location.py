# Copyright 2019 Intel, Inc.
# All Rights Reserved.
#
#    Licensed under the Apache License, Version 2.0 (the "License"); you may
#    not use this file except in compliance with the License. You may obtain
#    a copy of the License at
#
#         http://www.apache.org/licenses/LICENSE-2.0
#
#    Unless required by applicable law or agreed to in writing, software
#    distributed under the License is distributed on an "AS IS" BASIS, WITHOUT
#    WARRANTIES OR CONDITIONS OF ANY KIND, either express or implied. See the
#    License for the specific language governing permissions and limitations
#    under the License.

from sushy.resources import base

from rsd_lib import utils as rsd_lib_utils


class RackLocationField(base.CompositeField):

    rack_units = base.Field("RackUnits")
    """Indicates the rack unit type"""

    xlocation = base.Field("XLocation", adapter=rsd_lib_utils.num_or_none)
    """The horizontal location within uLocation, from left to right
       (1.. MAXIMUM) 0 indicate not available
    """

    ulocation = base.Field("ULocation", adapter=rsd_lib_utils.num_or_none)
    """The index of the top-most U of the component, from top to bottom
       (1.. MAXIMUM) 0 indicate not available
    """

    uheight = base.Field("UHeight", adapter=rsd_lib_utils.num_or_none)
    """The height of managed zone, e.g. 8 for 8U, 16 for 16U"""
