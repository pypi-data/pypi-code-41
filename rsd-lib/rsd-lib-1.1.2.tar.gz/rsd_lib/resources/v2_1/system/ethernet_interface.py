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
from sushy import utils

from rsd_lib import base as rsd_lib_base
from rsd_lib.resources.v2_1.common import ip_addresses
from rsd_lib.resources.v2_1.ethernet_switch import vlan_network_interface
from rsd_lib import utils as rsd_lib_utils


class LinksIntelRackScaleField(base.CompositeField):
    neighbor_port = base.Field(
        "NeighborPort", adapter=rsd_lib_utils.get_resource_identity
    )
    """The neighbor port of Rack ScaleIntel"""


class LinksOemField(base.CompositeField):
    intel_rackScale = LinksIntelRackScaleField("Intel_RackScale")
    """The Oem Intel_RackScale"""


class LinksField(base.CompositeField):

    endpoints = base.Field("Endpoints", adapter=utils.get_members_identities)
    """An array of references to the endpoints that connect to this ethernet
       interface.
    """

    oem = LinksOemField("Oem")
    """"The oem of Links"""


class IPv6AddressPolicyEntryCollectionField(base.ListField):

    prefix = base.Field("Prefix")
    """The IPv6 Address Prefix (as defined in RFC 6724 section 2.1)"""

    precedence = base.Field("Precedence", adapter=rsd_lib_utils.num_or_none)
    """The IPv6 Precedence (as defined in RFC 6724 section 2.1"""

    label = base.Field("Label", adapter=rsd_lib_utils.num_or_none)
    """The IPv6 Label (as defined in RFC 6724 section 2.1)"""


class EthernetInterface(rsd_lib_base.ResourceBase):
    """EthernetInterface resource class

       This schema defines a simple ethernet NIC resource.
    """

    uefi_device_path = base.Field("UefiDevicePath")
    """The UEFI device path for this interface"""

    status = rsd_lib_base.StatusField("Status")
    """This indicates the known state of the resource, such as if it is
       enabled.
    """

    interface_enabled = base.Field("InterfaceEnabled", adapter=bool)
    """This indicates whether this interface is enabled."""

    permanent_mac_address = base.Field("PermanentMACAddress")
    """This is the permanent MAC address assigned to this interface (port)"""

    mac_address = base.Field("MACAddress")
    """This is the currently configured MAC address of the (logical port)
       interface.
    """

    speed_mbps = base.Field("SpeedMbps", adapter=rsd_lib_utils.num_or_none)
    """This is the current speed in Mbps of this interface."""

    auto_neg = base.Field("AutoNeg", adapter=bool)
    """This indicates if the speed and duplex are automatically negotiated and
       configured on this interface.
    """

    full_duplex = base.Field("FullDuplex", adapter=bool)
    """This indicates if the interface is in Full Duplex mode or not."""

    mtu_size = base.Field("MTUSize", adapter=rsd_lib_utils.num_or_none)
    """This is the currently configured Maximum Transmission Unit (MTU) in
       bytes on this interface.
    """

    host_name = base.Field("HostName")
    """The DNS Host Name, without any domain information"""

    fqdn = base.Field("FQDN")
    """This is the complete, fully qualified domain name obtained by DNS for
       this interface.
    """

    max_ipv6_static_addresses = base.Field(
        "MaxIPv6StaticAddresses", adapter=rsd_lib_utils.num_or_none
    )
    """This indicates the maximum number of Static IPv6 addresses that can be
       configured on this interface.
    """

    vlan = vlan_network_interface.VLANField("VLAN")
    """If this Network Interface supports more than one VLAN, this property
       will not be present and the client should look for VLANs collection in
       the link section of this resource.
    """

    ipv4_addresses = ip_addresses.IPv4AddressCollectionField("IPv4Addresses")
    """The IPv4 addresses assigned to this interface"""

    ipv6_address_policy_table = IPv6AddressPolicyEntryCollectionField(
        "IPv6AddressPolicyTable"
    )
    """An array representing the RFC 6724 Address Selection Policy Table."""

    ipv6_addresses = ip_addresses.IPv6AddressCollectionField("IPv6Addresses")
    """This array of objects enumerates all of the currently assigned IPv6
       addresses on this interface.
    """

    ipv6_static_addresses = ip_addresses.IPv6StaticAddressCollectionField(
        "IPv6StaticAddresses"
    )
    """This array of objects represents all of the IPv6 static addresses to be
       assigned on this interface.
    """

    ipv6_default_gateway = base.Field("IPv6DefaultGateway")
    """This is the IPv6 default gateway address that is currently in use on
       this interface.
    """

    name_servers = base.Field("NameServers")
    """This represents DNS name servers that are currently in use on this
       interface.
    """

    link_status = base.Field("LinkStatus")
    """The link status of this interface (port)"""

    links = LinksField("Links")
    """Contains references to other resources that are related to this
       resource.
    """

    @property
    @utils.cache_it
    def vlans(self):
        """Property to provide reference to `VLanNetworkInterfaceCollection` instance

           It is calculated once when it is queried for the first time. On
           refresh, this property is reset.
        """
        return vlan_network_interface.VLanNetworkInterfaceCollection(
            self._conn,
            utils.get_sub_resource_path_by(self, "VLANs"),
            redfish_version=self.redfish_version,
        )


class EthernetInterfaceCollection(rsd_lib_base.ResourceCollectionBase):
    @property
    def _resource_type(self):
        return EthernetInterface
