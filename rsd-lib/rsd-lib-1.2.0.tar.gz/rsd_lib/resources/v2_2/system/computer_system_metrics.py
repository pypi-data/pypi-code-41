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


class ComputerSystemMetrics(rsd_lib_base.ResourceBase):
    """ComputerSystemMetrics resource class

       ComputerSystemMetrics contains usage and health statistics for a
       ComputerSystem (all Cores) .
    """

    processor_bandwidth_percent = base.Field(
        "ProcessorBandwidthPercent", adapter=rsd_lib_utils.num_or_none
    )
    """CPU Bandwidth in Percent."""

    memory_bandwidth_percent = base.Field(
        "MemoryBandwidthPercent", adapter=rsd_lib_utils.num_or_none
    )
    """Memory Bandwidth in Percent"""

    memory_throttled_cycles_percent = base.Field(
        "MemoryThrottledCyclesPercent", adapter=rsd_lib_utils.num_or_none
    )
    """The percentage of memory cycles that were throttled due to power
       limiting (all packages and memory controllers).
    """

    processor_power_watt = base.Field(
        "ProcessorPowerWatt", adapter=rsd_lib_utils.num_or_none
    )
    """Power consumed by Processor resource"""

    memory_power_watt = base.Field(
        "MemoryPowerWatt", adapter=rsd_lib_utils.num_or_none
    )
    """Power consumed by Memory domain resource"""

    io_bandwidth_gbps = base.Field(
        "IOBandwidthGBps", adapter=rsd_lib_utils.num_or_none
    )
    """IO Bandwidth rate in ComputerSystem resource based on PCIe data
       transmission rate in GB/s
    """

    health = base.Field("Health")
    """ComputerSystem Health as a discrete sensor reading"""
