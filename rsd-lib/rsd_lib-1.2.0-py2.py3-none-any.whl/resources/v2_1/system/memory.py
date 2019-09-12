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


class IntelRackScaleField(base.CompositeField):

    voltage_volt = base.Field("VoltageVolt", adapter=rsd_lib_utils.num_or_none)
    """This indicates current voltage of memory module"""


class OemField(base.CompositeField):

    intel_rackscale = IntelRackScaleField("Intel_RackScale")
    """Intel Rack Scale Design specific properties."""


class MemoryLocationField(base.CompositeField):

    socket = base.Field("Socket", adapter=rsd_lib_utils.num_or_none)
    """Socket number in which Memory is connected"""

    memory_controller = base.Field(
        "MemoryController", adapter=rsd_lib_utils.num_or_none
    )
    """Memory controller number in which Memory is connected"""

    channel = base.Field("Channel", adapter=rsd_lib_utils.num_or_none)
    """Channel number in which Memory is connected"""

    slot = base.Field("Slot", adapter=rsd_lib_utils.num_or_none)
    """Slot number in which Memory is connected"""


class RegionSetCollectionField(base.ListField):
    """RegionSet field

       Memory memory region information.
    """

    region_id = base.Field("RegionId")
    """Unique region ID representing a specific region within the Memory"""

    memory_classification = base.Field("MemoryClassification")
    """Classification of memory occupied by the given memory region"""

    offset_mib = base.Field("OffsetMiB", adapter=rsd_lib_utils.num_or_none)
    """Offset with in the Memory that corresponds to the starting of this
       memory region in MiB
    """

    size_mib = base.Field("SizeMiB", adapter=rsd_lib_utils.num_or_none)
    """Size of this memory region in MiB"""

    passphrase_state = base.Field("PassphraseState", adapter=bool)
    """State of the passphrase for this region"""


class Memory(rsd_lib_base.ResourceBase):
    """Memory resource class

       This is the schema definition for definition of a Memory and its
       configuration
    """

    memory_type = base.Field("MemoryType")
    """The type of Memory"""

    memory_device_type = base.Field("MemoryDeviceType")
    """Type details of the Memory"""

    base_module_type = base.Field("BaseModuleType")
    """The base module type of Memory"""

    memory_media = base.Field("MemoryMedia")
    """Media  of this Memory"""

    capacity_mib = base.Field("CapacityMiB", adapter=rsd_lib_utils.num_or_none)
    """Memory Capacity in MiB."""

    data_width_bits = base.Field(
        "DataWidthBits", adapter=rsd_lib_utils.num_or_none
    )
    """Data Width in bits."""

    bus_width_bits = base.Field(
        "BusWidthBits", adapter=rsd_lib_utils.num_or_none
    )
    """Bus Width in bits."""

    manufacturer = base.Field("Manufacturer")
    """The Memory manufacturer"""

    serial_number = base.Field("SerialNumber")
    """The product serial number of this device"""

    part_number = base.Field("PartNumber")
    """The product part number of this device"""

    allowed_speeds_mhz = base.Field("AllowedSpeedsMHz")
    """Speed bins supported by this Memory"""

    firmware_revision = base.Field("FirmwareRevision")
    """Revision of firmware on the Memory controller"""

    firmware_api_version = base.Field("FirmwareApiVersion")
    """Version of API supported by the firmware"""

    function_classes = base.Field("FunctionClasses")
    """Function Classes by the Memory"""

    vendor_id = base.Field("VendorID")
    """Vendor ID"""

    device_id = base.Field("DeviceID")
    """Device ID"""

    subsystem_vendor_id = base.Field("SubsystemVendorID")
    """SubSystem Vendor ID"""

    subsystem_device_id = base.Field("SubsystemDeviceID")
    """Subsystem Device ID"""

    max_tdp_milli_watts = base.Field("MaxTDPMilliWatts")
    """Maximum TDPs in milli Watts"""

    spare_device_count = base.Field(
        "SpareDeviceCount", adapter=rsd_lib_utils.num_or_none
    )
    """Number of unused spare devices available in the Memory"""

    rank_count = base.Field("RankCount", adapter=rsd_lib_utils.num_or_none)
    """Number of ranks available in the Memory"""

    device_locator = base.Field("DeviceLocator")
    """Location of the Memory in the platform"""

    memory_location = MemoryLocationField("MemoryLocation")
    """Memory connection information to sockets and memory controllers."""

    error_correction = base.Field("ErrorCorrection")
    """Error correction scheme supported for this memory"""

    operating_speed_mhz = base.Field(
        "OperatingSpeedMhz", adapter=rsd_lib_utils.num_or_none
    )
    """Operating speed of Memory in MHz"""

    volatile_region_size_limit_mib = base.Field(
        "VolatileRegionSizeLimitMiB", adapter=rsd_lib_utils.num_or_none
    )
    """Total size of volatile regions in MiB"""

    persistent_region_size_limit_mib = base.Field(
        "PersistentRegionSizeLimitMiB", adapter=rsd_lib_utils.num_or_none
    )
    """Total size of persistent regions in MiB"""

    regions = RegionSetCollectionField("Regions")
    """Memory regions information within the Memory"""

    operating_memory_modes = base.Field("OperatingMemoryModes")
    """Memory modes supported by the Memory"""

    is_spare_device_enabled = base.Field("IsSpareDeviceEnabled", adapter=bool)
    """Spare device enabled status"""

    is_rank_spare_enabled = base.Field("IsRankSpareEnabled", adapter=bool)
    """Rank spare enabled status"""

    status = rsd_lib_base.StatusField("Status")
    """This indicates the known state of the resource, such as if it is
       enabled.
    """

    oem = OemField("Oem")
    """Oem specific properties."""

    # TODO(linyang): Add Action Field


class MemoryCollection(rsd_lib_base.ResourceCollectionBase):
    @property
    def _resource_type(self):
        return Memory
