# Copyright 2018 Intel, Inc.
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

from rsd_lib import base as rsd_lib_base
from rsd_lib.resources.v2_1.common import rack_location
from rsd_lib import utils as rsd_lib_utils


class PowerSupplyCollectionField(base.ListField):

    name = base.Field("Name")
    """The Power Supply name"""

    power_capacity_watts = base.Field(
        "PowerCapacityWatts", adapter=rsd_lib_utils.num_or_none
    )
    """The maximum capacity of this Power Supply"""

    last_power_output_watts = base.Field(
        "LastPowerOutputWatts", adapter=rsd_lib_utils.num_or_none
    )
    """The average power output of this Power Supply"""

    manufacturer = base.Field("Manufacturer")
    """The manufacturer of this Power Supply"""

    model_number = base.Field("ModelNumber")
    """The model number for this Power Supply"""

    firmware_revision = base.Field("FirmwareRevision")
    """The firmware version for this Power Supply"""

    serial_number = base.Field("SerialNumber")
    """The serial number for this Power Supply"""

    part_number = base.Field("PartNumber")
    """The part number for this Power Supply"""

    status = rsd_lib_base.StatusField("Status")
    """The Power supply status"""

    rack_location = rack_location.RackLocationField("RackLocation")
    """The PowerZone physical location"""


class PowerZone(rsd_lib_base.ResourceBase):

    status = rsd_lib_base.StatusField("Status")
    """The PowerZone status"""

    rack_location = rack_location.RackLocationField("RackLocation")
    """The PowerZone physical location"""

    max_psus_supported = base.Field(
        "MaxPSUsSupported", adapter=rsd_lib_utils.num_or_none
    )
    """The maximum number of Power Supply Units supported by PowerZone"""

    presence = base.Field("Presence")
    """Indicates the aggregated Power Supply Unit presence information
       Aggregated Power Supply Unit presence format: Length of string indicate
       total slot of Power Supply Units in PowerZone.

       For each byte the string:
       "1" means present
       "0" means not present
    """

    number_of_psus_present = base.Field(
        "NumberOfPSUsPresent", adapter=rsd_lib_utils.num_or_none
    )
    """Indicates the number of existing Power Supply Units in PowerZone"""

    power_consumed_watts = base.Field(
        "PowerConsumedWatts", adapter=rsd_lib_utils.num_or_none
    )
    """The total power consumption of PowerZone, sum of trays'
       power consumption
    """

    power_output_watts = base.Field(
        "PowerOutputWatts", adapter=rsd_lib_utils.num_or_none
    )
    """The total power production of PowerZone, sum of PSUs' output"""

    power_capacity_watts = base.Field(
        "PowerCapacityWatts", adapter=rsd_lib_utils.num_or_none
    )
    """The maximum power capacity supported by PowerZone"""

    power_supplies = PowerSupplyCollectionField("PowerSupplies")
    """Details of the power supplies associated with this system or device"""


class PowerZoneCollection(rsd_lib_base.ResourceCollectionBase):
    @property
    def _resource_type(self):
        return PowerZone
