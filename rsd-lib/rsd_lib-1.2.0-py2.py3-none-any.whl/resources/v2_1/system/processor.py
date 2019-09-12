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

from rsd_lib import base as rsd_lib_base
from rsd_lib import utils as rsd_lib_utils


class IntelRackScaleField(base.CompositeField):

    brand = base.Field("Brand")
    """This indicates processor brand"""

    capabilities = base.Field("Capabilities")
    """This indicates array of processor capabilities"""


class ProcessorIdField(base.CompositeField):

    vendor_id = base.Field("VendorId")
    """The Vendor Identification for this processor"""

    identification_registers = base.Field("IdentificationRegisters")
    """The contents of the Identification Registers (CPUID) for this processor
    """

    effective_family = base.Field("EffectiveFamily")
    """The effective Family for this processor"""

    effective_model = base.Field("EffectiveModel")
    """The effective Model for this processor"""

    step = base.Field("Step")
    """The Step value for this processor"""

    microcode_info = base.Field("MicrocodeInfo")
    """The Microcode Information for this processor"""


class OemField(base.CompositeField):

    intel_rackscale = IntelRackScaleField("Intel_RackScale")
    """Intel Rack Scale Design specific properties."""


class Processor(rsd_lib_base.ResourceBase):
    """Processor resource class

       This is the schema definition for the Processor resource.  It
       represents the properties of a processor attached to a System.
    """

    socket = base.Field("Socket")
    """The socket or location of the processor"""

    processor_type = base.Field("ProcessorType")
    """The type of processor"""

    processor_architecture = base.Field("ProcessorArchitecture")
    """The architecture of the processor"""

    instruction_set = base.Field("InstructionSet")
    """The instruction set of the processor"""

    processor_id = ProcessorIdField("ProcessorId")
    """Identification information for this processor."""

    status = rsd_lib_base.StatusField("Status")
    """This indicates the known state of the resource, such as if it is
       enabled.
    """

    manufacturer = base.Field("Manufacturer")
    """The processor manufacturer"""

    model = base.Field("Model")
    """The product model number of this device"""

    max_speed_mhz = base.Field(
        "MaxSpeedMHz", adapter=rsd_lib_utils.num_or_none
    )
    """The maximum clock speed of the processor"""

    total_cores = base.Field("TotalCores", adapter=rsd_lib_utils.num_or_none)
    """The total number of cores contained in this processor"""

    total_threads = base.Field(
        "TotalThreads", adapter=rsd_lib_utils.num_or_none
    )
    """The total number of execution threads supported by this processor"""

    oem = OemField("Oem")
    """Oem specific properties."""


class ProcessorCollection(rsd_lib_base.ResourceCollectionBase):
    @property
    def _resource_type(self):
        return Processor
