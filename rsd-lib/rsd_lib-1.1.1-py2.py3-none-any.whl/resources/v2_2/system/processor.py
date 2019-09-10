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
from rsd_lib.resources.v2_1.system import processor
from rsd_lib.resources.v2_2.system import processor_metrics
from rsd_lib import utils as rsd_lib_utils


class ProcessorMemoryCollectionField(base.ListField):
    """ProcessorMemory field

       On die processor memory
    """

    type = base.Field("Type")
    """Type of memory."""

    capacity_mb = base.Field("CapacityMB", adapter=rsd_lib_utils.num_or_none)
    """Memory capacity."""

    speed_mhz = base.Field("SpeedMHz", adapter=rsd_lib_utils.num_or_none)
    """Memory speed."""


class FPGAField(base.CompositeField):
    """FPGA field

       FPGA properties
    """

    type = base.Field("Type")
    """FPGA type."""

    bit_stream_version = base.Field("BitStreamVersion")
    """Version of BitStream loaded on FPGA."""

    hssi_configuration = base.Field("HSSIConfiguration")
    """High Speed Serial Interface configuration."""

    hssi_sideband = base.Field("HSSISideband")
    """High Speed Serial Interface sideband interface type."""

    reconfiguration_slots = base.Field(
        "ReconfigurationSlots", adapter=rsd_lib_utils.num_or_none
    )
    """Number of supported reconfiguration slots."""


class IntelRackScaleField(processor.IntelRackScaleField):

    brand = base.Field("Brand")
    """This indicates processor brand"""

    capabilities = base.Field("Capabilities")
    """This indicates array of processor capabilities"""

    on_package_memory = ProcessorMemoryCollectionField("OnPackageMemory")
    """An array of references to the endpoints that connect to this processor.
    """

    thermal_design_power_watt = base.Field(
        "ThermalDesignPowerWatt", adapter=rsd_lib_utils.num_or_none
    )
    """Thermal Design Power (TDP) of this processor."""

    fpga = FPGAField("FPGA")
    """FPGA specific properties for FPGA ProcessorType."""

    extended_identification_registers = rsd_lib_base.DynamicField(
        "ExtendedIdentificationRegisters"
    )
    """Extended contents of the Identification Registers (CPUID) for this
       processor
    """

    metrics = base.Field(
        "Metrics", adapter=rsd_lib_utils.get_resource_identity
    )
    """A reference to the Metrics associated with this Processor"""


class OemField(base.CompositeField):

    intel_rackscale = IntelRackScaleField("Intel_RackScale")
    """Intel Rack Scale Design extensions ('Intel_RackScale' object)"""


class Processor(processor.Processor):

    oem = OemField("Oem")
    """Oem extension object"""

    @property
    @utils.cache_it
    def metrics(self):
        """Property to provide reference to `Metrics` instance

        It is calculated once the first time it is queried. On refresh,
        this property is reset.
        """
        return processor_metrics.ProcessorMetrics(
            self._conn,
            utils.get_sub_resource_path_by(
                self, ["Oem", "Intel_RackScale", "Metrics"]
            ),
            redfish_version=self.redfish_version,
        )


class ProcessorCollection(processor.ProcessorCollection):
    @property
    def _resource_type(self):
        return Processor
