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
from rsd_lib.resources.v2_1.system import system
from rsd_lib.resources.v2_2.system import computer_system_metrics
from rsd_lib.resources.v2_2.system import memory
from rsd_lib.resources.v2_2.system import processor
from rsd_lib import utils as rsd_lib_utils


class IntelRackScaleField(system.IntelRackScaleField):

    user_mode_enabled = base.Field("UserModeEnabled", adapter=bool)
    """This indicates if platform user mode is enabled"""

    trusted_execution_technology_enabled = base.Field(
        "TrustedExecutionTechnologyEnabled", adapter=bool
    )
    """This indicates if TXT mode is enabled"""

    metrics = base.Field(
        "Metrics", adapter=rsd_lib_utils.get_resource_identity
    )
    """A reference to the Metrics associated with this ComputerSystem"""


class OemField(base.CompositeField):

    intel_rackscale = IntelRackScaleField("Intel_RackScale")
    """Intel Rack Scale Design specific properties."""


class TrustedModulesCollectionField(base.ListField):
    """TrustedModules field

       This object describes the inventory of a Trusted Modules installed in
       the system.
    """

    firmware_version = base.Field("FirmwareVersion")
    """The firmware version of this Trusted Module."""

    interface_type = base.Field("InterfaceType")
    """This property indicates the interface type of the Trusted Module."""

    status = rsd_lib_base.StatusField("Status")
    """This indicates the known state of the resource, such as if it is
       enabled.
    """

    oem = base.Field("Oem")
    """The trusted_modules oem"""

    firmware_version2 = base.Field("FirmwareVersion2")
    """The 2nd firmware version of this Trusted Module, if applicable."""

    interface_type_selection = base.Field("InterfaceTypeSelection")
    """The Interface Type selection supported by this Trusted Module."""


class System(system.System):

    trusted_modules = TrustedModulesCollectionField("TrustedModules")
    """This object describes the array of Trusted Modules in the system."""

    oem = OemField("Oem")
    """Oem specific properties."""

    def _get_metrics_path(self):
        """Helper function to find the System metrics path"""
        return utils.get_sub_resource_path_by(
            self, ["Oem", "Intel_RackScale", "Metrics"]
        )

    @property
    @utils.cache_it
    def metrics(self):
        """Property to provide reference to `ComputerSystemMetrics` instance

        It is calculated once the first time it is queried. On refresh,
        this property is reset.
        """
        return computer_system_metrics.ComputerSystemMetrics(
            self._conn,
            self._get_metrics_path(),
            redfish_version=self.redfish_version,
        )

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


class SystemCollection(system.SystemCollection):
    @property
    def _resource_type(self):
        return System
