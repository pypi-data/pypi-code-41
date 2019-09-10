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


class SSDProtocolField(base.CompositeField):

    protocol_enabled = base.Field("ProtocolEnabled", adapter=bool)
    """Indicates if the protocol is enabled or disabled"""

    port = base.Field("Port", adapter=rsd_lib_utils.num_or_none)
    """Indicates the protocol port."""

    notify_multicast_interval_seconds = base.Field(
        "NotifyMulticastIntervalSeconds", adapter=rsd_lib_utils.num_or_none
    )
    """Indicates how often the Multicast is done from this service for SSDP."""

    notify_ttl = base.Field("NotifyTTL", adapter=rsd_lib_utils.num_or_none)
    """Indicates the time to live hop count for SSDPs Notify messages."""

    notify_ipv6_scope = base.Field("NotifyIPv6Scope")
    """Indicates the scope for the IPv6 Notify messages for SSDP."""


class ProtocolField(base.CompositeField):

    protocol_enabled = base.Field("ProtocolEnabled", adapter=bool)
    """Indicates if the protocol is enabled or disabled"""

    port = base.Field("Port", adapter=rsd_lib_utils.num_or_none)
    """Indicates the protocol port."""


class ManagerNetworkProtocol(rsd_lib_base.ResourceBase):
    """ManagerNetworkProtocol resource class

       This resource is used to obtain or modify the network services managed
       by a given manager.
    """

    host_name = base.Field("HostName")
    """The DNS Host Name of this manager, without any domain information"""

    fqdn = base.Field("FQDN")
    """This is the fully qualified domain name for the manager obtained by DNS
       including the host name and top-level domain name.
    """

    http = ProtocolField("HTTP")
    """Settings for this Manager's HTTP protocol support"""

    https = ProtocolField("HTTPS")
    """Settings for this Manager's HTTPS protocol support"""

    snmp = ProtocolField("SNMP")
    """Settings for this Manager's SNMP support"""

    virtual_media = ProtocolField("VirtualMedia")
    """Settings for this Manager's Virtual Media support"""

    telnet = ProtocolField("Telnet")
    """Settings for this Manager's Telnet protocol support"""

    ssdp = SSDProtocolField("SSDP")
    """Settings for this Manager's SSDP support"""

    ipmi = ProtocolField("IPMI")
    """Settings for this Manager's IPMI-over-LAN protocol support"""

    ssh = ProtocolField("SSH")
    """Settings for this Manager's SSH (Secure Shell) protocol support"""

    kvmip = ProtocolField("KVMIP")
    """Settings for this Manager's KVM-IP protocol support"""

    status = rsd_lib_base.StatusField("Status")
    """This indicates the known state of the resource, such as if it is
       enabled.
    """
