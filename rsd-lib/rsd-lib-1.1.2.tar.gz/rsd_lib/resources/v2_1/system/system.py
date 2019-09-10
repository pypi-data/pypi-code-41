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

import logging

from sushy import exceptions
from sushy.resources import base
from sushy.resources import common
from sushy import utils

from rsd_lib import base as rsd_lib_base
from rsd_lib import constants
from rsd_lib.resources.v2_1.chassis import log_service
from rsd_lib.resources.v2_1.system import ethernet_interface
from rsd_lib.resources.v2_1.system import memory
from rsd_lib.resources.v2_1.system import network_interface
from rsd_lib.resources.v2_1.system import pcie_device
from rsd_lib.resources.v2_1.system import pcie_function
from rsd_lib.resources.v2_1.system import processor
from rsd_lib.resources.v2_1.system import simple_storage
from rsd_lib.resources.v2_1.system import storage
from rsd_lib import utils as rsd_lib_utils


LOG = logging.getLogger(__name__)


class ProcessorSummaryField(base.CompositeField):
    """ProcessorSummary field

       This object describes the central processors of the system in general
       detail.
    """

    count = base.Field("Count", adapter=rsd_lib_utils.num_or_none)
    """The number of processors in the system."""

    model = base.Field("Model")
    """The processor model for the primary or majority of processors in this
       system.
    """

    status = rsd_lib_base.StatusField("Status")
    """This indicates the known state of the resource, such as if it is
       enabled.
    """


class LinksField(base.CompositeField):

    chassis = base.Field("Chassis", adapter=utils.get_members_identities)
    """An array of references to the chassis in which this system is contained
    """

    managed_by = base.Field("ManagedBy", adapter=utils.get_members_identities)
    """An array of references to the Managers responsible for this system"""

    powered_by = base.Field("PoweredBy", adapter=utils.get_members_identities)
    """An array of ID[s] of resources that power this computer system.
       Normally the ID will be a chassis or a specific set of powerSupplies
    """

    cooled_by = base.Field("CooledBy", adapter=utils.get_members_identities)
    """An array of ID[s] of resources that cool this computer system. Normally
       the ID will be a chassis or a specific set of fans.
    """

    endpoints = base.Field("Endpoints", adapter=utils.get_members_identities)
    """An array of references to the endpoints that connect to this system."""


class BootField(base.CompositeField):
    """Boot field

       This object contains the boot information for the current resource.
    """

    boot_source_override_target = base.Field("BootSourceOverrideTarget")
    """The current boot source to be used at next boot instead of the normal
       boot device, if BootSourceOverrideEnabled is true.
    """

    boot_source_override_target_allowed_values = base.Field(
        "BootSourceOverrideTarget@Redfish.AllowableValues"
    )

    boot_source_override_enabled = base.Field("BootSourceOverrideEnabled")
    """Describes the state of the Boot Source Override feature"""

    uefi_target_boot_source_override = base.Field(
        "UefiTargetBootSourceOverride"
    )
    """This property is the UEFI Device Path of the device to boot from when
       BootSourceOverrideSupported is UefiTarget.
    """

    boot_source_override_mode = base.Field("BootSourceOverrideMode")
    """The BIOS Boot Mode (either Legacy or UEFI) to be used when
       BootSourceOverrideTarget boot source is booted from.
    """

    boot_source_override_mode_allowed_values = base.Field(
        "BootSourceOverrideMode@Redfish.AllowableValues"
    )


class MemorySummaryField(base.CompositeField):
    """MemorySummary field

       This object describes the memory of the system in general detail.
    """

    total_system_memory_gib = base.Field(
        "TotalSystemMemoryGiB", adapter=rsd_lib_utils.num_or_none
    )
    """The total installed, operating system-accessible memory (RAM), measured
       in GiB.
    """

    status = rsd_lib_base.StatusField("Status")
    """This indicates the known state of the resource, such as if it is
       enabled.
    """


class PciDeviceCollectionField(base.ListField):

    vendor_id = base.Field("VendorId")

    device_id = base.Field("DeviceId")


class IntelRackScaleField(base.CompositeField):

    pcie_connection_id = base.Field("PCIeConnectionId")
    """This property is an array of IDs of cable or cables connected to this
       port.
    """

    pci_devices = PciDeviceCollectionField("PciDevices")
    """This indicates array of PCI devices present in computer system"""

    discovery_state = base.Field("DiscoveryState")
    """This indicates computer system discovery state"""

    processor_sockets = base.Field(
        "ProcessorSockets", adapter=rsd_lib_utils.num_or_none
    )
    """This indicates number of processor sockets available in system"""

    memory_sockets = base.Field(
        "MemorySockets", adapter=rsd_lib_utils.num_or_none
    )
    """This indicates number of memory sockets available in system"""


class OemField(base.CompositeField):

    intel_rackscale = IntelRackScaleField("Intel_RackScale")
    """Intel Rack Scale Design specific properties."""


class ActionsField(base.CompositeField):
    reset = common.ResetActionField("#ComputerSystem.Reset")


class System(rsd_lib_base.ResourceBase):
    """ComputerSystem resource class

       This schema defines a computer system and its respective properties.  A
       computer system represents a machine (physical or virtual) and the
       local resources such as memory, cpu and other devices that can be
       accessed from that machine.
    """

    system_type = base.Field("SystemType")
    """The type of computer system represented by this resource."""

    links = LinksField("Links")
    """Contains references to other resources that are related to this
       resource.
    """

    asset_tag = base.Field("AssetTag")
    """The user definable tag that can be used to track this computer system
       for inventory or other client purposes
    """

    manufacturer = base.Field("Manufacturer")
    """The manufacturer or OEM of this system."""

    model = base.Field("Model")
    """The model number for this system"""

    sku = base.Field("SKU")
    """The manufacturer SKU for this system"""

    serial_number = base.Field("SerialNumber")
    """The serial number for this system"""

    part_number = base.Field("PartNumber")
    """The part number for this system"""

    uuid = base.Field("UUID")
    """The universal unique identifier (UUID) for this system"""

    host_name = base.Field("HostName")
    """The DNS Host Name, without any domain information"""

    indicator_led = base.Field("IndicatorLED")
    """The state of the indicator LED, used to identify the system"""

    power_state = base.Field("PowerState")
    """This is the current power state of the system"""

    boot = BootField("Boot")
    """Information about the boot settings for this system"""

    bios_version = base.Field("BiosVersion")
    """The version of the system BIOS or primary system firmware."""

    processor_summary = ProcessorSummaryField("ProcessorSummary")
    """This object describes the central processors of the system in general
       detail.
    """

    memory_summary = MemorySummaryField("MemorySummary")
    """This object describes the central memory of the system in general
       detail.
    """

    status = rsd_lib_base.StatusField("Status")
    """This indicates the known state of the resource, such as if it is
       enabled.
    """

    hosting_roles = base.Field("HostingRoles")
    """The hosing roles that this computer system supports."""

    oem = OemField("Oem")
    """Oem specific properties."""

    _actions = ActionsField("Actions", required=True)

    def _get_reset_action_element(self):
        reset_action = self._actions.reset

        if not reset_action:
            raise exceptions.MissingActionError(
                action="#ComputerSystem.Reset", resource=self._path
            )
        return reset_action

    def get_allowed_reset_system_values(self):
        """Get the allowed values for resetting the system.

        :returns: A set with the allowed values.
        """
        reset_action = self._get_reset_action_element()

        if not reset_action.allowed_values:
            LOG.warning(
                "Could not figure out the allowed values for the "
                "reset system action for System %s",
                self.identity,
            )
            return set(constants.RESET_TYPE_VALUE)

        return set(constants.RESET_TYPE_VALUE).intersection(
            reset_action.allowed_values
        )

    def reset_system(self, value):
        """Reset the system.

        :param value: The target value.
        :raises: InvalidParameterValueError, if the target value is not
            allowed.
        """
        valid_resets = self.get_allowed_reset_system_values()
        if value not in valid_resets:
            raise exceptions.InvalidParameterValueError(
                parameter="value", value=value, valid_values=valid_resets
            )

        target_uri = self._get_reset_action_element().target_uri

        self._conn.post(target_uri, data={"ResetType": value})

    def get_allowed_system_boot_source_values(self):
        """Get the allowed values for changing the boot source.

        :returns: A set with the allowed values.
        """
        if not self.boot.boot_source_override_target_allowed_values:
            LOG.warning(
                "Could not figure out the allowed values for "
                "configuring the boot source for System %s",
                self.identity,
            )
            return set(constants.BOOT_SOURCE_TARGET_VALUE)

        return set(constants.BOOT_SOURCE_TARGET_VALUE).intersection(
            self.boot.boot_source_override_target_allowed_values
        )

    def get_allowed_system_boot_mode_values(self):
        """Get the allowed values for the boot source mode.

        :returns: A set with the allowed values.
        """
        if not self.boot.boot_source_override_mode_allowed_values:
            LOG.warning(
                "Could not figure out the allowed values for "
                "configuring the boot mode for System %s",
                self.identity,
            )
            return set(constants.BOOT_SOURCE_MODE_VALUE)

        return set(constants.BOOT_SOURCE_MODE_VALUE).intersection(
            self.boot.boot_source_override_mode_allowed_values
        )

    def set_system_boot_source(self, target, enabled="Once", mode=None):
        """Set the boot source.

        Set the boot source to use on next reboot of the System.

        :param target: The target boot source.
        :param enabled: The frequency, whether to set it for the next
            reboot only ("Once") or persistent to all future reboots
            ("Continuous") or disabled ("Disabled").
        :param mode: The boot mode, UEFI ("UEFI") or BIOS ("Legacy").
        :raises: InvalidParameterValueError, if any information passed is
            invalid.
        """
        valid_targets = self.get_allowed_system_boot_source_values()
        if target not in valid_targets:
            raise exceptions.InvalidParameterValueError(
                parameter="target", value=target, valid_values=valid_targets
            )

        if enabled not in constants.BOOT_SOURCE_ENABLED_VALUE:
            raise exceptions.InvalidParameterValueError(
                parameter="enabled",
                value=enabled,
                valid_values=constants.BOOT_SOURCE_ENABLED_VALUE,
            )

        data = {
            "Boot": {
                "BootSourceOverrideTarget": target,
                "BootSourceOverrideEnabled": enabled,
            }
        }

        if mode is not None:
            valid_modes = self.get_allowed_system_boot_mode_values()
            if mode not in valid_modes:
                raise exceptions.InvalidParameterValueError(
                    parameter="mode", value=mode, valid_values=valid_modes
                )

            data["Boot"]["BootSourceOverrideMode"] = mode

        self._conn.patch(self.path, data=data)

    def update(self, asset_tag):
        """Update AssetTag

        :param asset_tag: The user assigned asset tag for this computer system
        """

        data = {"AssetTag": asset_tag}

        self._conn.patch(self.path, data=data)

    @property
    @utils.cache_it
    def processors(self):
        """Property to provide reference to `ProcessorCollection` instance

           It is calculated once when it is queried for the first time. On
           refresh, this property is reset.
        """
        return processor.ProcessorCollection(
            self._conn,
            utils.get_sub_resource_path_by(self, "Processors"),
            redfish_version=self.redfish_version,
        )

    @property
    @utils.cache_it
    def ethernet_interfaces(self):
        """Property to provide reference to `EthernetInterfaceCollection` instance

           It is calculated once when it is queried for the first time. On
           refresh, this property is reset.
        """
        return ethernet_interface.EthernetInterfaceCollection(
            self._conn,
            utils.get_sub_resource_path_by(self, "EthernetInterfaces"),
            redfish_version=self.redfish_version,
        )

    @property
    @utils.cache_it
    def simple_storage(self):
        """Property to provide reference to `SimpleStorageCollection` instance

           It is calculated once when it is queried for the first time. On
           refresh, this property is reset.
        """
        return simple_storage.SimpleStorageCollection(
            self._conn,
            utils.get_sub_resource_path_by(self, "SimpleStorage"),
            redfish_version=self.redfish_version,
        )

    @property
    @utils.cache_it
    def log_services(self):
        """Property to provide reference to `LogServiceCollection` instance

           It is calculated once when it is queried for the first time. On
           refresh, this property is reset.
        """
        return log_service.LogServiceCollection(
            self._conn,
            utils.get_sub_resource_path_by(self, "LogServices"),
            redfish_version=self.redfish_version,
        )

    @property
    @utils.cache_it
    def memory(self):
        """Property to provide reference to `MemoryCollection` instance

           It is calculated once when it is queried for the first time. On
           refresh, this property is reset.
        """
        return memory.MemoryCollection(
            self._conn,
            utils.get_sub_resource_path_by(self, "Memory"),
            redfish_version=self.redfish_version,
        )

    @property
    @utils.cache_it
    def storage(self):
        """Property to provide reference to `StorageCollection` instance

           It is calculated once when it is queried for the first time. On
           refresh, this property is reset.
        """
        return storage.StorageCollection(
            self._conn,
            utils.get_sub_resource_path_by(self, "Storage"),
            redfish_version=self.redfish_version,
        )

    @property
    @utils.cache_it
    def pcie_devices(self):
        """Property to provide a list of `PCIeDevice` instance

           It is calculated once when it is queried for the first time. On
           refresh, this property is reset.
        """
        return [
            pcie_device.PCIeDevice(
                self._conn, path, redfish_version=self.redfish_version
            )
            for path in rsd_lib_utils.get_sub_resource_path_list_by(
                self, "PCIeDevices"
            )
        ]

    @property
    @utils.cache_it
    def pcie_functions(self):
        """Property to provide a list of `PCIeFunction` instance

           It is calculated once when it is queried for the first time. On
           refresh, this property is reset.
        """
        return [
            pcie_function.PCIeFunction(
                self._conn, path, redfish_version=self.redfish_version
            )
            for path in rsd_lib_utils.get_sub_resource_path_list_by(
                self, "PCIeFunctions"
            )
        ]

    @property
    @utils.cache_it
    def network_interfaces(self):
        """Property to provide reference to `NetworkInterfaceCollection` instance

           It is calculated once when it is queried for the first time. On
           refresh, this property is reset.
        """
        return network_interface.NetworkInterfaceCollection(
            self._conn,
            utils.get_sub_resource_path_by(self, "NetworkInterfaces"),
            redfish_version=self.redfish_version,
        )


class SystemCollection(rsd_lib_base.ResourceCollectionBase):
    @property
    def _resource_type(self):
        return System
