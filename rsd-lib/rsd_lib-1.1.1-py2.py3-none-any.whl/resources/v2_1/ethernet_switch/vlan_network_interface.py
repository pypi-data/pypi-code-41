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

from jsonschema import validate
import logging

from sushy.resources import base

from rsd_lib import base as rsd_lib_base
from rsd_lib.resources.v2_1.ethernet_switch import schemas \
    as ethernet_switch_schemas


LOG = logging.getLogger(__name__)


class VLANField(base.CompositeField):

    vlan_enable = base.Field("VLANEnable", adapter=bool)
    """This indicates if this VLAN is enabled."""

    vlan_id = base.Field("VLANId")
    """This indicates the VLAN identifier for this VLAN."""


class IntelRackScaleField(base.CompositeField):

    status = rsd_lib_base.StatusField("Status")
    """This indicates the known state of the resource, such as if it is
       enabled.
    """

    tagged = base.Field("Tagged", adapter=bool)
    """This indicates if VLAN is tagged (as defined in IEEE 802.1Q)."""


class OemField(base.CompositeField):

    intel_rackscale = IntelRackScaleField("Intel_RackScale")
    """Intel Rack Scale Design specific properties."""


class VLanNetworkInterface(rsd_lib_base.ResourceBase):
    """VLanNetworkInterface resource class

       This resource contains information for a Virtual LAN (VLAN) network
       instance available on a manager, system or other device.
    """

    vlan_enable = base.Field("VLANEnable", adapter=bool)
    """This indicates if this VLAN is enabled."""

    vlan_id = base.Field("VLANId")
    """This indicates the VLAN identifier for this VLAN."""

    oem = OemField("Oem")
    """Oem specific properties."""

    def delete(self):
        """Delete this vlan network interface"""
        self._conn.delete(self.path)


class VLanNetworkInterfaceCollection(rsd_lib_base.ResourceCollectionBase):
    @property
    def _resource_type(self):
        return VLanNetworkInterface

    def add_vlan(self, vlan_network_interface_req):
        """Add a vlan to port

        :param vlan_network_interface_req: JSON for vlan network interface
        :returns: The location of the vlan network interface
        """
        target_uri = self._path
        validate(
            vlan_network_interface_req,
            ethernet_switch_schemas.vlan_network_interface_req_schema,
        )
        resp = self._conn.post(target_uri, data=vlan_network_interface_req)
        LOG.info("VLAN add at %s", resp.headers["Location"])
        vlan_network_interface_url = resp.headers["Location"]
        return vlan_network_interface_url[
            vlan_network_interface_url.find(self._path):
        ]
