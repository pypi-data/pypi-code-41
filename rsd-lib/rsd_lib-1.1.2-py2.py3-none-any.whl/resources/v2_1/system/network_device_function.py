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


class iSCSIBootField(base.CompositeField):

    ip_address_type = base.Field("IPAddressType")
    """The type of IP address (IPv6 or IPv4) being populated in the iSCSIBoot
       IP address fields.
    """

    initiator_ip_address = base.Field("InitiatorIPAddress")
    """The IPv6 or IPv4 address of the iSCSI initiator."""

    initiator_name = base.Field("InitiatorName")
    """The iSCSI initiator name."""

    initiator_default_gateway = base.Field("InitiatorDefaultGateway")
    """The IPv6 or IPv4 iSCSI boot default gateway."""

    initiator_netmask = base.Field("InitiatorNetmask")
    """The IPv6 or IPv4 netmask of the iSCSI boot initiator."""

    target_info_via_dhcp = base.Field("TargetInfoViaDHCP", adapter=bool)
    """Whether the iSCSI boot target name, LUN, IP address, and netmask should
       be obtained from DHCP.
    """

    primary_target_name = base.Field("PrimaryTargetName")
    """The name of the iSCSI primary boot target."""

    primary_target_ip_address = base.Field("PrimaryTargetIPAddress")
    """The IP address (IPv6 or IPv4) for the primary iSCSI boot target."""

    primary_target_tcp_port = base.Field(
        "PrimaryTargetTCPPort", adapter=rsd_lib_utils.num_or_none
    )
    """The TCP port for the primary iSCSI boot target."""

    primary_lun = base.Field("PrimaryLUN", adapter=rsd_lib_utils.num_or_none)
    """The logical unit number (LUN) for the primary iSCSI boot target."""

    primary_vlan_enable = base.Field("PrimaryVLANEnable", adapter=bool)
    """This indicates if the primary VLAN is enabled."""

    primary_vlan_id = base.Field(
        "PrimaryVLANId", adapter=rsd_lib_utils.num_or_none
    )
    """The 802.1q VLAN ID to use for iSCSI boot from the primary target."""

    primary_dns = base.Field("PrimaryDNS")
    """The IPv6 or IPv4 address of the primary DNS server for the iSCSI boot
       initiator.
    """

    secondary_target_name = base.Field("SecondaryTargetName")
    """The name of the iSCSI secondary boot target."""

    secondary_target_ip_address = base.Field("SecondaryTargetIPAddress")
    """The IP address (IPv6 or IPv4) for the secondary iSCSI boot target."""

    secondary_target_tcp_port = base.Field(
        "SecondaryTargetTCPPort", adapter=rsd_lib_utils.num_or_none
    )
    """The TCP port for the secondary iSCSI boot target."""

    secondary_lun = base.Field(
        "SecondaryLUN", adapter=rsd_lib_utils.num_or_none
    )
    """The logical unit number (LUN) for the secondary iSCSI boot target."""

    secondary_vlan_enable = base.Field("SecondaryVLANEnable", adapter=bool)
    """This indicates if the secondary VLAN is enabled."""

    secondary_vlan_id = base.Field(
        "SecondaryVLANId", adapter=rsd_lib_utils.num_or_none
    )
    """The 802.1q VLAN ID to use for iSCSI boot from the secondary target."""

    secondary_dns = base.Field("SecondaryDNS")
    """The IPv6 or IPv4 address of the secondary DNS server for the iSCSI boot
       initiator.
    """

    ip_mask_dns_via_dhcp = base.Field("IPMaskDNSViaDHCP", adapter=bool)
    """Whether the iSCSI boot initiator uses DHCP to obtain the iniator name,
       IP address, and netmask.
    """

    router_advertisement_enabled = base.Field(
        "RouterAdvertisementEnabled", adapter=bool
    )
    """Whether IPv6 router advertisement is enabled for the iSCSI boot target.
    """

    authentication_method = base.Field("AuthenticationMethod")
    """The iSCSI boot authentication method for this network device function.
    """

    chap_username = base.Field("CHAPUsername")
    """The username for CHAP authentication."""

    chap_secret = base.Field("CHAPSecret")
    """The shared secret for CHAP authentication."""

    mutual_chap_username = base.Field("MutualCHAPUsername")
    """The CHAP Username for 2-way CHAP authentication."""

    mutual_chap_secret = base.Field("MutualCHAPSecret")
    """The CHAP Secret for 2-way CHAP authentication."""


class EthernetField(base.CompositeField):

    mac_address = base.Field("MACAddress")
    """This is the currently configured MAC address of the (logical port)
       network device function.
    """


class NetworkDeviceFunction(rsd_lib_base.ResourceBase):
    """NetworkDeviceFunction resource class

       A Network Device Function represents a logical interface exposed by the
       network adapter.
    """

    status = rsd_lib_base.StatusField("Status")
    """This indicates the known state of the resource, such as if it is
       enabled.
    """

    device_enabled = base.Field("DeviceEnabled", adapter=bool)
    """Whether the network device function is enabled."""

    ethernet = EthernetField("Ethernet")
    """Ethernet."""

    iscsi_boot = iSCSIBootField("iSCSIBoot")
    """iSCSI Boot."""

    def update(self, ethernet=None, iscsi_boot=None):
        """Enable iSCSI boot of compute node

        :param ethernet: Ethernet capabilities for this network device function
        :param iscsi_boot: iSCSI boot capabilities, status, and configuration
                           values for this network device function
        """
        data = {}
        if ethernet is not None:
            data["Ethernet"] = ethernet
        if iscsi_boot is not None:
            data["iSCSIBoot"] = iscsi_boot

        self._conn.patch(self.path, data=data)


class NetworkDeviceFunctionCollection(rsd_lib_base.ResourceCollectionBase):
    @property
    def _resource_type(self):
        return NetworkDeviceFunction
