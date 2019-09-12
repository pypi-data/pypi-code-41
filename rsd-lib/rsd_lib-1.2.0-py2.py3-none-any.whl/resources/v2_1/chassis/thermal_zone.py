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


class TemperatureSensorCollectionField(base.ListField):

    name = base.Field("Name")
    """The Power Supply name"""

    reading_celsius = base.Field(
        "ReadingCelsius", adapter=rsd_lib_utils.num_or_none
    )
    """Current value of the temperature sensor's reading"""

    physical_context = base.Field("PhysicalContext")
    """Describes the area or device to which this temperature measurement
       applies:
       "Intake" - The intake point of the chassis
       "Exhaust" - The exhaust point of the chassis
       "Backplane" - A backplane within the chassis
       "PowerSupply" - A power supply
       "SystemBoard" - The system board (PCB)
       "ComputeBay" - Within a compute bay
       "PowerSupplyBay" - Within a power supply bay
    """

    status = rsd_lib_base.StatusField("Status")
    """The temperature sensors status"""


class FanCollectionField(base.ListField):

    name = base.Field("Name")
    """The Power Supply name"""

    reading_rpm = base.Field("ReadingRPM", adapter=rsd_lib_utils.num_or_none)
    """Fan RPM reading"""

    status = rsd_lib_base.StatusField("Status")
    """The Fan status"""

    rack_location = rack_location.RackLocationField("RackLocation")
    """The Fan physical location"""


class ThermalZone(rsd_lib_base.ResourceBase):

    status = rsd_lib_base.StatusField("Status")
    """The ThermalZone status"""

    rack_location = rack_location.RackLocationField("RackLocation")
    """The ThermalZone physical location"""

    presence = base.Field("Presence")
    """Indicates the aggregated Power Supply Unit presence information
       Aggregated Power Supply Unit presence format: Length of string indicate
       total slot of Power Supply Units in PowerZone.

       For each byte the string:
       "1" means present
       "0" means not present
    """

    desired_speed_pwm = base.Field(
        "DesiredSpeedPWM", adapter=rsd_lib_utils.num_or_none
    )
    """The desired FAN speed in current ThermalZone present in PWM unit"""

    desired_speed_rpm = base.Field(
        "DesiredSpeedRPM", adapter=rsd_lib_utils.num_or_none
    )
    """The desired FAN speed in current ThermalZone present in RPM unit"""

    max_fans_supported = base.Field(
        "MaxFansSupported", adapter=rsd_lib_utils.num_or_none
    )
    """Number of maximum fans that can be installed in a given Thermal Zone"""

    number_of_fans_present = base.Field(
        "NumberOfFansPresent", adapter=rsd_lib_utils.num_or_none
    )
    """The existing number of fans in current ThermalZone"""

    volumetric_airflow = base.Field(
        "VolumetricAirflow", adapter=rsd_lib_utils.num_or_none
    )
    """Rack Level PTAS Telemetry - Volumetric airflow in current ThermalZone"""

    fans = FanCollectionField("Fans")
    """Details of the fans associated with this thermal zone"""

    temperatures = TemperatureSensorCollectionField("Temperatures")
    """Array of temperature sensors"""


class ThermalZoneCollection(rsd_lib_base.ResourceCollectionBase):
    @property
    def _resource_type(self):
        return ThermalZone
