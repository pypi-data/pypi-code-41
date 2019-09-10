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


class PowerMetricField(base.CompositeField):

    interval_in_min = base.Field(
        "IntervalInMin", adapter=rsd_lib_utils.num_or_none
    )
    """The time interval (or window) in which the PowerMetrics are measured
       over.
    """

    min_consumed_watts = base.Field(
        "MinConsumedWatts", adapter=rsd_lib_utils.num_or_none
    )
    """The lowest power consumption level over the measurement window (the
       last IntervalInMin minutes).
    """

    max_consumed_watts = base.Field(
        "MaxConsumedWatts", adapter=rsd_lib_utils.num_or_none
    )
    """The highest power consumption level that has occured over the
       measurement window (the last IntervalInMin minutes).
    """

    average_consumed_watts = base.Field(
        "AverageConsumedWatts", adapter=rsd_lib_utils.num_or_none
    )
    """The average power level over the measurement window (the last
       IntervalInMin minutes).
    """


class PowerLimitField(base.CompositeField):
    """PowerLimit field

       This object contains power limit status and configuration information
       for the chassis.
    """

    limit_in_watts = base.Field(
        "LimitInWatts", adapter=rsd_lib_utils.num_or_none
    )
    """The Power limit in watts. Set to null to disable power capping."""

    limit_exception = base.Field("LimitException")
    """The action that is taken if the power cannot be maintained below the
       LimitInWatts.
    """

    correction_in_ms = base.Field(
        "CorrectionInMs", adapter=rsd_lib_utils.num_or_none
    )
    """The time required for the limiting process to reduce power consumption
       to below the limit.
    """


class InputRangeCollectionField(base.ListField):

    input_type = base.Field("InputType")
    """The Input type (AC or DC)"""

    minimum_voltage = base.Field(
        "MinimumVoltage", adapter=rsd_lib_utils.num_or_none
    )
    """The minimum line input voltage at which this power supply input range
       is effective
    """

    maximum_voltage = base.Field(
        "MaximumVoltage", adapter=rsd_lib_utils.num_or_none
    )
    """The maximum line input voltage at which this power supply input range
       is effective
    """

    minimum_frequency_hz = base.Field(
        "MinimumFrequencyHz", adapter=rsd_lib_utils.num_or_none
    )
    """The minimum line input frequency at which this power supply input range
       is effective
    """

    maximum_frequency_hz = base.Field(
        "MaximumFrequencyHz", adapter=rsd_lib_utils.num_or_none
    )
    """The maximum line input frequency at which this power supply input range
       is effective
    """

    output_wattage = base.Field(
        "OutputWattage", adapter=rsd_lib_utils.num_or_none
    )
    """The maximum capacity of this Power Supply when operating in this input
       range
    """


class VoltageCollectionField(rsd_lib_base.ReferenceableMemberField):

    name = base.Field("Name")
    """Voltage sensor name."""

    sensor_number = base.Field(
        "SensorNumber", adapter=rsd_lib_utils.num_or_none
    )
    """A numerical identifier to represent the voltage sensor"""

    status = rsd_lib_base.StatusField("Status")
    """This indicates the known state of the resource, such as if it is
       enabled.
    """

    reading_volts = base.Field(
        "ReadingVolts", adapter=rsd_lib_utils.num_or_none
    )
    """The current value of the voltage sensor."""

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

    min_reading_range = base.Field(
        "MinReadingRange", adapter=rsd_lib_utils.num_or_none
    )
    """Minimum value for CurrentReading"""

    max_reading_range = base.Field(
        "MaxReadingRange", adapter=rsd_lib_utils.num_or_none
    )
    """Maximum value for CurrentReading"""

    physical_context = base.Field("PhysicalContext")
    """Describes the area or device to which this voltage measurement applies.
    """

    related_item = base.Field(
        "RelatedItem", adapter=utils.get_members_identities
    )
    """Describes the areas or devices to which this voltage measurement
       applies.
    """


class PowerControlCollectionField(rsd_lib_base.ReferenceableMemberField):

    name = base.Field("Name")
    """Power Control Function name."""

    power_consumed_watts = base.Field(
        "PowerConsumedWatts", adapter=rsd_lib_utils.num_or_none
    )
    """The actual power being consumed by the chassis."""

    power_requested_watts = base.Field(
        "PowerRequestedWatts", adapter=rsd_lib_utils.num_or_none
    )
    """The potential power that the chassis resources are requesting which may
       be higher than the current level being consumed since requested power
       includes budget that the chassis resource wants for future use.
    """

    power_available_watts = base.Field(
        "PowerAvailableWatts", adapter=rsd_lib_utils.num_or_none
    )
    """The amount of power not already budgeted and therefore available for
       additional allocation. (powerCapacity - powerAllocated).  This
       indicates how much reserve power capacity is left.
    """

    power_capacity_watts = base.Field(
        "PowerCapacityWatts", adapter=rsd_lib_utils.num_or_none
    )
    """The total amount of power available to the chassis for allocation. This
       may the power supply capacity, or power budget assigned to the chassis
       from an up-stream chassis.
    """

    power_allocated_watts = base.Field(
        "PowerAllocatedWatts", adapter=rsd_lib_utils.num_or_none
    )
    """The total amount of power that has been allocated (or budegeted)to
       chassis resources.
    """

    power_metrics = PowerMetricField("PowerMetrics")
    """Power readings for this chassis."""

    power_limit = PowerLimitField("PowerLimit")
    """Power limit status and configuration information for this chassis"""

    status = rsd_lib_base.StatusField("Status")
    """This indicates the known state of the resource, such as if it is
       enabled.
    """

    related_item = base.Field(
        "RelatedItem", adapter=utils.get_members_identities
    )
    """The ID(s) of the resources associated with this Power Limit"""


class PowerSupplyCollectionField(rsd_lib_base.ReferenceableMemberField):
    """PowerSupply field

       Details of a power supplies associated with this system or device
    """

    name = base.Field("Name")
    """The name of the Power Supply"""

    power_supply_type = base.Field("PowerSupplyType")
    """The Power Supply type (AC or DC)"""

    line_input_voltage_type = base.Field("LineInputVoltageType")
    """The line voltage type supported as an input to this Power Supply"""

    line_input_voltage = base.Field(
        "LineInputVoltage", adapter=rsd_lib_utils.num_or_none
    )
    """The line input voltage at which the Power Supply is operating"""

    power_capacity_watts = base.Field(
        "PowerCapacityWatts", adapter=rsd_lib_utils.num_or_none
    )
    """The maximum capacity of this Power Supply"""

    last_power_output_watts = base.Field(
        "LastPowerOutputWatts", adapter=rsd_lib_utils.num_or_none
    )
    """The average power output of this Power Supply"""

    model = base.Field("Model")
    """The model number for this Power Supply"""

    firmware_version = base.Field("FirmwareVersion")
    """The firmware version for this Power Supply"""

    serial_number = base.Field("SerialNumber")
    """The serial number for this Power Supply"""

    part_number = base.Field("PartNumber")
    """The part number for this Power Supply"""

    spare_part_number = base.Field("SparePartNumber")
    """The spare part number for this Power Supply"""

    status = rsd_lib_base.StatusField("Status")
    """This indicates the known state of the resource, such as if it is
       enabled.
    """

    related_item = base.Field(
        "RelatedItem", adapter=utils.get_members_identities
    )
    """The ID(s) of the resources associated with this Power Limit"""

    redundancy = redundancy.RedundancyCollectionField("Redundancy")
    """This structure is used to show redundancy for power supplies.  The
       Component ids will reference the members of the redundancy groups.
    """

    manufacturer = base.Field("Manufacturer")
    """This is the manufacturer of this power supply."""

    input_ranges = InputRangeCollectionField("InputRanges")
    """This is the input ranges that the power supply can use."""


class Power(rsd_lib_base.ResourceBase):
    """Power resource class

       This is the schema definition for the Power Metrics.  It represents the
       properties for Power Consumption and Power Limiting.
    """

    power_control = PowerControlCollectionField("PowerControl")
    """This is the definition for power control function (power
       reading/limiting).
    """

    voltages = VoltageCollectionField("Voltages")
    """This is the definition for voltage sensors."""

    power_supplies = PowerSupplyCollectionField("PowerSupplies")
    """Details of the power supplies associated with this system or device"""

    redundancy = redundancy.RedundancyCollectionField("Redundancy")
    """Redundancy information for the power subsystem of this system or device
    """
