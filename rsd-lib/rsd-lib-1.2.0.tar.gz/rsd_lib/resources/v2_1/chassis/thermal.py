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
from sushy import utils

from rsd_lib import base as rsd_lib_base
from rsd_lib.resources.v2_1.common import redundancy
from rsd_lib import utils as rsd_lib_utils


class FanCollectionField(rsd_lib_base.ReferenceableMemberField):

    fan_name = base.Field("FanName")
    """Name of the fan"""

    physical_context = base.Field("PhysicalContext")
    """Describes the area or device associated with this fan."""

    status = rsd_lib_base.StatusField("Status")
    """This indicates the known state of the resource, such as if it is
       enabled.
    """

    reading = base.Field("Reading", adapter=rsd_lib_utils.num_or_none)
    """Current fan speed"""

    upper_threshold_non_critical = base.Field(
        "UpperThresholdNonCritical", adapter=rsd_lib_utils.num_or_none
    )
    """Above normal range"""

    upper_threshold_critical = base.Field(
        "UpperThresholdCritical", adapter=rsd_lib_utils.num_or_none
    )
    """Above normal range but not yet fatal"""

    upper_threshold_fatal = base.Field(
        "UpperThresholdFatal", adapter=rsd_lib_utils.num_or_none
    )
    """Above normal range and is fatal"""

    lower_threshold_non_critical = base.Field(
        "LowerThresholdNonCritical", adapter=rsd_lib_utils.num_or_none
    )
    """Below normal range"""

    lower_threshold_critical = base.Field(
        "LowerThresholdCritical", adapter=rsd_lib_utils.num_or_none
    )
    """Below normal range but not yet fatal"""

    lower_threshold_fatal = base.Field(
        "LowerThresholdFatal", adapter=rsd_lib_utils.num_or_none
    )
    """Below normal range and is fatal"""

    min_reading_range = base.Field(
        "MinReadingRange", adapter=rsd_lib_utils.num_or_none
    )
    """Minimum value for Reading"""

    max_reading_range = base.Field(
        "MaxReadingRange", adapter=rsd_lib_utils.num_or_none
    )
    """Maximum value for Reading"""

    related_item = base.Field(
        "RelatedItem", adapter=utils.get_members_identities
    )
    """The ID(s) of the resources serviced with this fan"""

    redundancy = redundancy.RedundancyCollectionField("Redundancy")
    """This structure is used to show redundancy for fans.  The Component ids
       will reference the members of the redundancy groups.
    """

    reading_units = base.Field("ReadingUnits")
    """Units in which the reading and thresholds are measured."""

    name = base.Field("Name")
    """Name of the fan"""


class TemperatureCollectionField(rsd_lib_base.ReferenceableMemberField):

    name = base.Field("Name")
    """Temperature sensor name."""

    sensor_number = base.Field(
        "SensorNumber", adapter=rsd_lib_utils.num_or_none
    )
    """A numerical identifier to represent the temperature sensor"""

    status = rsd_lib_base.StatusField("Status")
    """This indicates the known state of the resource, such as if it is
       enabled.
    """

    reading_celsius = base.Field(
        "ReadingCelsius", adapter=rsd_lib_utils.num_or_none
    )
    """Temperature"""

    upper_threshold_non_critical = base.Field(
        "UpperThresholdNonCritical", adapter=rsd_lib_utils.num_or_none
    )
    """Above normal range"""

    upper_threshold_critical = base.Field(
        "UpperThresholdCritical", adapter=rsd_lib_utils.num_or_none
    )
    """Above normal range but not yet fatal."""

    upper_threshold_fatal = base.Field(
        "UpperThresholdFatal", adapter=rsd_lib_utils.num_or_none
    )
    """Above normal range and is fatal"""

    lower_threshold_non_critical = base.Field(
        "LowerThresholdNonCritical", adapter=rsd_lib_utils.num_or_none
    )
    """Below normal range"""

    lower_threshold_critical = base.Field(
        "LowerThresholdCritical", adapter=rsd_lib_utils.num_or_none
    )
    """Below normal range but not yet fatal."""

    lower_threshold_fatal = base.Field(
        "LowerThresholdFatal", adapter=rsd_lib_utils.num_or_none
    )
    """Below normal range and is fatal"""

    min_reading_range_temp = base.Field(
        "MinReadingRangeTemp", adapter=rsd_lib_utils.num_or_none
    )
    """Minimum value for ReadingCelsius"""

    max_reading_range_temp = base.Field(
        "MaxReadingRangeTemp", adapter=rsd_lib_utils.num_or_none
    )
    """Maximum value for ReadingCelsius"""

    physical_context = base.Field("PhysicalContext")
    """Describes the area or device to which this temperature measurement
       applies.
    """

    related_item = base.Field(
        "RelatedItem", adapter=utils.get_members_identities
    )
    """Describes the areas or devices to which this temperature measurement
       applies.
    """


class Thermal(rsd_lib_base.ResourceBase):
    """Thermal resource class

       This is the schema definition for the Thermal properties.  It
       represents the properties for Temperature and Cooling.
    """

    status = rsd_lib_base.StatusField("Status")
    """This indicates the known state of the resource, such as if it is
       enabled.
    """

    temperatures = TemperatureCollectionField("Temperatures")
    """This is the definition for temperature sensors."""

    fans = FanCollectionField("Fans")
    """This is the definition for fans."""

    redundancy = redundancy.RedundancyCollectionField("Redundancy")
    """This structure is used to show redundancy for fans.  The Component ids
       will reference the members of the redundancy groups.
    """
