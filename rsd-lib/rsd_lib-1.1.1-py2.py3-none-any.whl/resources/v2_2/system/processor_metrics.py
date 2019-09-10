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
from rsd_lib import utils as rsd_lib_utils


class ProcessorMetrics(rsd_lib_base.ResourceBase):
    """ProcessorMetrics resource class

       ProcessorMetrics contains usage and health statistics for a Processor
       (all Cores) .
    """

    bandwidth_percent = base.Field(
        "BandwidthPercent", adapter=rsd_lib_utils.num_or_none
    )
    """CPU Bandwidth in [%]"""

    average_frequency_mhz = base.Field(
        "AverageFrequencyMHz", adapter=rsd_lib_utils.num_or_none
    )
    """Average frequency [MHz]"""

    throttling_celsius = base.Field(
        "ThrottlingCelsius", adapter=rsd_lib_utils.num_or_none
    )
    """CPU Margin to throttle (temperature offset in degree Celsius)"""

    temperature_celsius = base.Field(
        "TemperatureCelsius", adapter=rsd_lib_utils.num_or_none
    )
    """Temperature of the Processor resource"""

    consumed_power_watt = base.Field(
        "ConsumedPowerWatt", adapter=rsd_lib_utils.num_or_none
    )
    """Power consumed by Processor resource"""

    health = base.Field("Health")
    """CPU Health as a discrete sensor reading"""
