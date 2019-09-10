# Copyright 2018 99cloud, Inc.
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
from rsd_lib.resources.v2_1.chassis import log_service
from rsd_lib.resources.v2_1.common import redundancy
from rsd_lib.resources.v2_1.manager import manager_network_protocol
from rsd_lib.resources.v2_1.manager import serial_interface
from rsd_lib.resources.v2_1.manager import virtual_media
from rsd_lib.resources.v2_1.system import ethernet_interface
from rsd_lib import utils as rsd_lib_utils


class LinksIntelRackScaleField(base.CompositeField):

    manager_for_services = base.Field(
        "ManagerForServices", adapter=utils.get_members_identities
    )

    manager_for_switches = base.Field(
        "ManagerForSwitches", adapter=utils.get_members_identities
    )


class LinksOemField(base.CompositeField):

    intel_rackscale = LinksIntelRackScaleField("Intel_RackScale")
    """Intel Rack Scale Design specific properties."""


class LinksField(base.CompositeField):

    manager_for_servers = base.Field(
        "ManagerForServers", adapter=utils.get_members_identities
    )
    """This property is an array of references to the systems that this
       manager has control over.
    """

    manager_for_chassis = base.Field(
        "ManagerForChassis", adapter=utils.get_members_identities
    )
    """This property is an array of references to the chassis that this
       manager has control over.
    """

    manager_in_chassis = base.Field(
        "ManagerInChassis", adapter=rsd_lib_utils.get_resource_identity
    )
    """This property is a reference to the chassis that this manager is
       located in.
    """

    oem = LinksOemField("Oem")
    """Oem specific properties."""


class SerialConsoleField(base.CompositeField):
    """SerialConsole field

       Used for describing services like Serial Console, Command Shell or
       Graphical Console
    """

    service_enabled = base.Field("ServiceEnabled", adapter=bool)
    """Indicates if the service is enabled for this manager."""

    max_concurrent_sessions = base.Field(
        "MaxConcurrentSessions", adapter=rsd_lib_utils.num_or_none
    )
    """Indicates the maximum number of service sessions, regardless of
       protocol, this manager is able to support.
    """

    connect_types_supported = base.Field("ConnectTypesSupported")
    """This object is used to enumerate the Serial Console connection types
       allowed by the implementation.
    """


class GraphicalConsoleField(base.CompositeField):
    """GraphicalConsole field

       Used for describing services like Serial Console, Command Shell or
       Graphical Console
    """

    service_enabled = base.Field("ServiceEnabled", adapter=bool)
    """Indicates if the service is enabled for this manager."""

    max_concurrent_sessions = base.Field(
        "MaxConcurrentSessions", adapter=rsd_lib_utils.num_or_none
    )
    """Indicates the maximum number of service sessions, regardless of
       protocol, this manager is able to support.
    """

    connect_types_supported = base.Field("ConnectTypesSupported")
    """This object is used to enumerate the Graphical Console connection types
       allowed by the implementation.
    """


class CommandShellField(base.CompositeField):
    """CommandShell field

       Used for describing services like Serial Console, Command Shell or
       Graphical Console
    """

    service_enabled = base.Field("ServiceEnabled", adapter=bool)
    """Indicates if the service is enabled for this manager."""

    max_concurrent_sessions = base.Field(
        "MaxConcurrentSessions", adapter=rsd_lib_utils.num_or_none
    )
    """Indicates the maximum number of service sessions, regardless of
       protocol, this manager is able to support.
    """

    connect_types_supported = base.Field("ConnectTypesSupported")
    """This object is used to enumerate the Command Shell connection types
       allowed by the implementation.
    """


class Manager(rsd_lib_base.ResourceBase):
    """Manager resource class

       This is the schema definition for a Manager.  Examples of managers are
       BMCs, Enclosure Managers, Management Controllers and other subsystems
       assigned managability functions.
    """

    manager_type = base.Field("ManagerType")
    """This property represents the type of manager that this resource
       represents.
    """

    links = LinksField("Links")
    """Contains references to other resources that are related to this
       resource.
    """

    service_entry_point_uuid = base.Field("ServiceEntryPointUUID")
    """The UUID of the Redfish Service provided by this manager"""

    uuid = base.Field("UUID")
    """The Universal Unique Identifier (UUID) for this Manager"""

    model = base.Field("Model")
    """The model information of this Manager as defined by the manufacturer"""

    date_time = base.Field("DateTime")
    """The current DateTime (with offset) for the manager, used to set or read
       time.
    """

    date_time_local_offset = base.Field("DateTimeLocalOffset")
    """The time offset from UTC that the DateTime property is set to in
       format: +06:00 .
    """

    firmware_version = base.Field("FirmwareVersion")
    """The firmware version of this Manager"""

    serial_console = SerialConsoleField("SerialConsole")
    """Information about the Serial Console service provided by this manager.
    """

    command_shell = CommandShellField("CommandShell")
    """Information about the Command Shell service provided by this manager."""

    graphical_console = GraphicalConsoleField("GraphicalConsole")
    """The value of this property shall contain the information about the
       Graphical Console (KVM-IP) service of this manager.
    """

    status = rsd_lib_base.StatusField("Status")
    """This indicates the known state of the resource, such as if it is
       enabled.
    """

    redundancy = redundancy.RedundancyCollectionField("Redundancy")
    """Redundancy information for the managers of this system"""

    power_state = base.Field("PowerState")
    """This is the current power state of the Manager."""

    # TODO(linyang): Add Action Field

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
    def serial_interfaces(self):
        """Property to provide reference to `SerialInterfaceCollection` instance

           It is calculated once when it is queried for the first time. On
           refresh, this property is reset.
        """
        return serial_interface.SerialInterfaceCollection(
            self._conn,
            utils.get_sub_resource_path_by(self, "SerialInterfaces"),
            redfish_version=self.redfish_version,
        )

    @property
    @utils.cache_it
    def network_protocol(self):
        """Property to provide reference to `ManagerNetworkProtocol` instance

           It is calculated once when it is queried for the first time. On
           refresh, this property is reset.
        """
        return manager_network_protocol.ManagerNetworkProtocol(
            self._conn,
            utils.get_sub_resource_path_by(self, "NetworkProtocol"),
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
    def virtual_media(self):
        """Property to provide reference to `VirtualMediaCollection` instance

           It is calculated once when it is queried for the first time. On
           refresh, this property is reset.
        """
        return virtual_media.VirtualMediaCollection(
            self._conn,
            utils.get_sub_resource_path_by(self, "VirtualMedia"),
            redfish_version=self.redfish_version,
        )


class ManagerCollection(rsd_lib_base.ResourceCollectionBase):
    @property
    def _resource_type(self):
        return Manager
