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
from rsd_lib.resources.v2_2.system import processor
from rsd_lib import utils as rsd_lib_utils


class OnPackageMemoryField(base.ListField):

    memory_type = base.Field('Type')
    """Type of memory"""

    capacity_mb = base.Field('CapacityMB', adapter=rsd_lib_utils.num_or_none)
    """Memory capacity"""

    speed_mhz = base.Field('SpeedMHz', adapter=rsd_lib_utils.num_or_none)
    """Memory speed"""


class ReconfigurationSlotsDetailsField(base.ListField):

    slot_id = base.Field('SlotId')
    """Reconfiguration slot identity"""

    uuid = base.Field('UUID')
    """Reconfiguration slot uuid"""

    programmable_from_host = base.Field('ProgrammableFromHost', adapter=bool)
    """Indict whether programmable from host"""


class FpgaField(base.CompositeField):

    fpga_type = base.Field('Type')
    """Type of FPGA"""

    model = base.Field('Model')
    """Model of FPGA"""

    fw_id = base.Field('FwId')
    """Firmware identity of FPGA"""

    fw_manufacturer = base.Field('FwManufacturer')
    """Firmware manufacturer of FPGA"""

    fw_version = base.Field('FwVersion')
    """Firmware version of FPGA"""

    host_interface = base.Field('HostInterface')
    """Host interface of FPGA"""

    external_interfaces = base.Field('ExternalInterfaces')
    """External interfaces of FPGA"""

    sideband_interface = base.Field('SidebandInterface')
    """Sideband interface of FPGA"""

    pcie_virtual_functions = base.Field(
        'PCIeVirtualFunctions', adapter=rsd_lib_utils.num_or_none)
    """PCIe Virtual functions of FPGA"""

    programmable_from_host = base.Field('ProgrammableFromHost', adapter=bool)
    """Indict whether programmable from host"""

    reconfiguration_slots = base.Field(
        'ReconfigurationSlots', adapter=rsd_lib_utils.num_or_none)
    """Number of supported reconfiguration slots"""

    reconfiguration_slots_details = ReconfigurationSlotsDetailsField(
        'ReconfigurationSlotsDetails')
    """Details of supported reconfiguration slots"""

    # TODO(linyang): might need to return instance instead of URI
    acceleration_functions = base.Field(
        'AccelerationFunctions', adapter=rsd_lib_utils.get_resource_identity)
    """The reference to a resource of type AccelerationFunctions"""


class IntelRackScaleField(processor.IntelRackScaleField):

    on_package_memory = OnPackageMemoryField('OnPackageMemory')
    """An array of references to the endpoints that connect to this processor
    """

    thermal_design_power_watt = base.Field(
        'ThermalDesignPowerWatt', adapter=rsd_lib_utils.num_or_none)
    """Thermal Design Power (TDP) of this processor"""

    metrics = base.Field(
        'Metrics', adapter=rsd_lib_utils.get_resource_identity)
    """A reference to the Metrics associated with this Processor"""

    extended_identification_registers = rsd_lib_base.DynamicField(
        'ExtendedIdentificationRegisters')
    """Extended contents of the Identification Registers (CPUID) for this
       processor
    """

    fpga = FpgaField('FPGA')
    """FPGA specific properties for FPGA ProcessorType"""

    # TODO(linyang): might need to return instance instead of URI
    pcie_function = base.Field(
        'PCIeFunction', adapter=rsd_lib_utils.get_resource_identity)
    """The reference to a resource of type PCIeFunction"""


class OemField(base.CompositeField):

    intel_rackscale = IntelRackScaleField('Intel_RackScale')
    """Intel Rack Scale Design extensions ('Intel_RackScale' object)"""


class LinksIntelRackScaleField(base.CompositeField):

    connected_port = base.Field(
        'ConnectedPort', adapter=rsd_lib_utils.get_resource_identity)
    """The reference to a resource of type ConnectedPort"""

    endpoints = base.Field('Endpoints', adapter=utils.get_members_identities)
    """The reference to a list of type Endpoints"""

    connected_processors = base.Field(
        'ConnectedProcessors', adapter=utils.get_members_identities)
    """The reference to a list of type ConnectedProcessors"""


class LinksOemField(base.CompositeField):

    intel_rackscale = LinksIntelRackScaleField('Intel_RackScale')
    """The Intel Rack Scale specific reference links"""


class LinksField(base.CompositeField):

    chassis = base.Field(
        'Chassis', adapter=rsd_lib_utils.get_resource_identity)
    """The reference to a resource of type Chassis that represent the physical
       container associated with this processor
    """

    oem = LinksOemField('Oem')
    """The Oem specific reference links"""


class Processor(processor.Processor):

    links = LinksField('Links')
    """Contain references to resources that are related to, but not contained
       by (subordinate to), this processor
    """

    oem = OemField('Oem')
    """Oem extension object"""

    def _get_sub_processors_path(self):
        """Helper function to find the System process metrics path"""
        return utils.get_sub_resource_path_by(self, 'SubProcessors')

    @property
    @utils.cache_it
    def sub_processors(self):
        """Property to provide reference to `ProcessorCollection` instance

        It is calculated once the first time it is queried. On refresh,
        this property is reset.
        """
        return ProcessorCollection(
            self._conn, self._get_sub_processors_path(),
            redfish_version=self.redfish_version)


class ProcessorCollection(processor.ProcessorCollection):

    @property
    def _resource_type(self):
        return Processor
