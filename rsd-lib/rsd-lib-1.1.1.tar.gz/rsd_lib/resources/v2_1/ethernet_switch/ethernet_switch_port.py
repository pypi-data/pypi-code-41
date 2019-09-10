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

import logging

from jsonschema import validate
from sushy.resources import base
from sushy import utils

from rsd_lib import base as rsd_lib_base
from rsd_lib.resources.v2_1.common import ip_addresses
from rsd_lib.resources.v2_1.ethernet_switch import ethernet_switch_static_mac
from rsd_lib.resources.v2_1.ethernet_switch import schemas as port_schema
from rsd_lib.resources.v2_1.ethernet_switch import vlan_network_interface
from rsd_lib import utils as rsd_lib_utils


LOG = logging.getLogger(__name__)


class NeighborInfoField(base.CompositeField):

    switch_id = base.Field("SwitchId")

    port_id = base.Field("PortId")

    cable_id = base.Field("CableId")


class LinksIntelRackScaleField(base.CompositeField):

    neighbor_interface = base.Field(
        "NeighborInterface", adapter=rsd_lib_utils.get_resource_identity
    )


class LinksOemField(base.CompositeField):

    intel_rackscale = LinksIntelRackScaleField("Intel_RackScale")
    """Intel Rack Scale Design specific properties."""


class LinksField(base.CompositeField):

    primary_vlan = base.Field(
        "PrimaryVLAN", adapter=rsd_lib_utils.get_resource_identity
    )

    switch = base.Field("Switch", adapter=rsd_lib_utils.get_resource_identity)

    member_of_port = base.Field(
        "MemberOfPort", adapter=rsd_lib_utils.get_resource_identity
    )

    port_members = base.Field(
        "PortMembers", adapter=utils.get_members_identities
    )

    active_acls = base.Field(
        "ActiveACLs", adapter=utils.get_members_identities
    )

    oem = LinksOemField("Oem")
    """Oem specific properties."""


class EthernetSwitchPort(rsd_lib_base.ResourceBase):

    port_id = base.Field("PortId")
    """Switch port unique identifier."""

    link_type = base.Field("LinkType")
    """Type of port link"""

    operational_state = base.Field("OperationalState")
    """Port link operational state"""

    administrative_state = base.Field("AdministrativeState")
    """Port link state forced by user."""

    link_speed_mbps = base.Field(
        "LinkSpeedMbps", adapter=rsd_lib_utils.num_or_none
    )
    """Port speed"""

    neighbor_info = NeighborInfoField("NeighborInfo")
    """For Upstream port type this property provide information about neighbor
       switch (and switch port if available) connected to this port
    """

    neighbor_mac = base.Field("NeighborMAC")
    """For Downstream port type this property provide MAC address of NIC
       connected to this port.
    """

    frame_size = base.Field("FrameSize", adapter=rsd_lib_utils.num_or_none)
    """MAC frame size in bytes"""

    autosense = base.Field("Autosense", adapter=bool)
    """Indicates if the speed and duplex is automatically configured by the NIC
    """

    full_duplex = base.Field("FullDuplex", adapter=bool)
    """Indicates if port is in Full Duplex mode or not"""

    mac_address = base.Field("MACAddress")
    """MAC address of port."""

    ipv4_addresses = ip_addresses.IPv4AddressCollectionField("IPv4Addresses")
    """Array of following IPv4 address"""

    ipv6_addresses = ip_addresses.IPv6AddressCollectionField("IPv6Addresses")
    """Array of following IPv6 address"""

    port_class = base.Field("PortClass")
    """Port class"""

    port_mode = base.Field("PortMode")
    """Port working mode. The value shall correspond to the port class
       (especially to the logical port definition).
    """

    port_type = base.Field("PortType")
    """PortType"""

    status = rsd_lib_base.StatusField("Status")
    """This indicates the known state of the resource, such as if it is
       enabled.
    """

    links = LinksField("Links")

    def delete(self):
        """Delete this ethernet switch port"""
        self._conn.delete(self._path)

    @property
    @utils.cache_it
    def vlans(self):
        """Property to provide reference to `VLanNetworkInterfaceCollection`

           It is calculated once when it is queried for the first time. On
           refresh, this property is reset.
        """
        return vlan_network_interface.VLanNetworkInterfaceCollection(
            self._conn,
            utils.get_sub_resource_path_by(self, "VLANs"),
            redfish_version=self.redfish_version,
        )

    @property
    @utils.cache_it
    def static_macs(self):
        """Property to provide reference to `EthernetSwitchStaticMACCollection`

           It is calculated once when it is queried for the first time. On
           refresh, this property is reset.
        """
        return ethernet_switch_static_mac.EthernetSwitchStaticMACCollection(
            self._conn,
            utils.get_sub_resource_path_by(self, "StaticMACs"),
            redfish_version=self.redfish_version,
        )

    def update(self, data=None):
        """Update a new Port

        :param data: JSON for Port
        """
        update_schema = port_schema.port_req_schema
        del update_schema["required"]
        if data is not None or len(data) > 0:
            validate(data, update_schema)
        self._conn.patch(self.path, data=data)


class EthernetSwitchPortCollection(rsd_lib_base.ResourceCollectionBase):
    @property
    def _resource_type(self):
        return EthernetSwitchPort

    def create_port(self, port_req):
        """Create a new Port

        :param Port: JSON for Port
        :returns: The location of the Port
        """
        validate(port_req, port_schema.port_req_schema)
        resp = self._conn.post(self._path, data=port_req)
        port_url = resp.headers["Location"]
        LOG.info("Create Port at %s", port_url)
        return port_url[port_url.find(self._path):]
