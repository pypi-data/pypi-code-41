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

from sushy import exceptions
from sushy.resources import base
from sushy.resources import common

from rsd_lib import base as rsd_lib_base
from rsd_lib import utils as rsd_lib_utils


class CurrentPeriodField(base.CompositeField):
    """CurrentPeriod field

       This object contains the Memory metrics since last reset or
       ClearCurrentPeriod action.
    """

    blocks_read = base.Field("BlocksRead", adapter=rsd_lib_utils.num_or_none)
    """Number of blocks read since reset."""

    blocks_written = base.Field(
        "BlocksWritten", adapter=rsd_lib_utils.num_or_none
    )
    """Number of blocks written since reset."""


class LifeTimeField(base.CompositeField):
    """LifeTime field

       This object contains the Memory metrics for the lifetime of the Memory.
    """

    blocks_read = base.Field("BlocksRead", adapter=rsd_lib_utils.num_or_none)
    """Number of blocks read for the lifetime of the Memory."""

    blocks_written = base.Field(
        "BlocksWritten", adapter=rsd_lib_utils.num_or_none
    )
    """Number of blocks written for the lifetime of the Memory."""


class AlarmTripsField(base.CompositeField):
    """AlarmTrips field

       Alarm trip information about the memory.
    """

    temperature = base.Field("Temperature", adapter=bool)
    """Temperature threshold crossing alarm trip detected status."""

    spare_block = base.Field("SpareBlock", adapter=bool)
    """Spare block capacity crossing alarm trip detected status."""

    uncorrectable_ecc_error = base.Field("UncorrectableECCError", adapter=bool)
    """Uncorrectable data error threshold crossing alarm trip detected status.
    """

    correctable_ecc_error = base.Field("CorrectableECCError", adapter=bool)
    """Correctable data error threshold crossing alarm trip detected status."""

    address_parity_error = base.Field("AddressParityError", adapter=bool)
    """Address parity error detected status."""


class HealthDataField(base.CompositeField):
    """HealthData field

       This type describes the health information of the memory.
    """

    remaining_spare_block_percentage = base.Field(
        "RemainingSpareBlockPercentage", adapter=rsd_lib_utils.num_or_none
    )
    """Remaining spare blocks in percentage."""

    last_shutdown_success = base.Field("LastShutdownSuccess", adapter=bool)
    """Status of last shutdown."""

    data_loss_detected = base.Field("DataLossDetected", adapter=bool)
    """Data loss detection status."""

    performance_degraded = base.Field("PerformanceDegraded", adapter=bool)
    """Performance degraded mode status."""

    alarm_trips = AlarmTripsField("AlarmTrips")
    """Alarm trip information about the memory."""

    predicted_media_life_left_percent = base.Field(
        "PredictedMediaLifeLeftPercent", adapter=rsd_lib_utils.num_or_none
    )
    """The percentage of reads and writes that are predicted to still be
       available for the media.
    """


class IntelRackScaleField(base.CompositeField):

    temperature_celsius = base.Field(
        "TemperatureCelsius", adapter=rsd_lib_utils.num_or_none
    )
    """Temperature of the Memory resource"""

    bandwidth_percent = base.Field(
        "BandwidthPercent", adapter=rsd_lib_utils.num_or_none
    )
    """Memory Bandwidth in Percent"""

    throttled_cycles_percent = base.Field(
        "ThrottledCyclesPercent", adapter=rsd_lib_utils.num_or_none
    )
    """The percentage of memory cycles that were throttled due to power
       limiting.
    """

    consumed_power_watt = base.Field(
        "ConsumedPowerWatt", adapter=rsd_lib_utils.num_or_none
    )
    """Power consumed by Memory domain resource"""

    thermal_margin_celsius = base.Field(
        "ThermalMarginCelsius", adapter=rsd_lib_utils.num_or_none
    )
    """Memory Thermal Margin in degree Celsius"""

    ecc_errors_count = base.Field(
        "ECCErrorsCount", adapter=rsd_lib_utils.num_or_none
    )
    """Number of ECC Errors found on this Memory module"""

    health = base.Field("Health")
    """Memory module Health as a discrete sensor reading"""


class OemField(base.CompositeField):

    intel_rackscale = IntelRackScaleField("Intel_RackScale")
    """Intel Rack Scale Design specific properties."""


class ActionsField(base.CompositeField):

    clear_current_period = common.ActionField(
        "#MemoryMetrics.ClearCurrentPeriod"
    )


class MemoryMetrics(rsd_lib_base.ResourceBase):
    """MemoryMetrics resource class

       MemoryMetrics contains usage and health statistics for a single Memory
       module or device instance.
    """

    block_size_bytes = base.Field(
        "BlockSizeBytes", adapter=rsd_lib_utils.num_or_none
    )
    """Block size in bytes."""

    current_period = CurrentPeriodField("CurrentPeriod")
    """This object contains the Memory metrics since last reset or
       ClearCurrentPeriod action.
    """

    life_time = LifeTimeField("LifeTime")
    """This object contains the Memory metrics for the lifetime of the Memory.
    """

    health_data = HealthDataField("HealthData")
    """This object describes the health information of the memory."""

    oem = OemField("Oem")
    """Oem specific properties."""

    _actions = ActionsField("Actions")
    """The Actions property shall contain the
        available actions for this resource.
    """

    def _get_clear_current_period_action_element(self):
        clear_current_period_action = self._actions.clear_current_period

        if not clear_current_period_action:
            raise exceptions.MissingActionError(
                action="#MemoryMetrics.ClearCurrentPeriod", resource=self._path
            )
        return clear_current_period_action

    def clear_current_period(self):
        """Clear the current the period of memory_metrics.

        :raises: MissingActionError, if no clear_current_period action exists.
        """
        target_uri = self._get_clear_current_period_action_element().target_uri

        self._conn.post(target_uri, data={})
