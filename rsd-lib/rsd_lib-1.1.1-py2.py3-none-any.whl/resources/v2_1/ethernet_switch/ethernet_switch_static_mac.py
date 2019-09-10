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

from sushy import exceptions
from sushy.resources import base

from rsd_lib import base as rsd_lib_base
from rsd_lib import utils as rsd_lib_utils

LOG = logging.getLogger(__name__)


class EthernetSwitchStaticMAC(rsd_lib_base.ResourceBase):
    """EthernetSwitchStaticMAC resource class

       A Ethernet Switch ACL represents Access Control List for switch.
    """

    vlan_id = base.Field("VLANId", adapter=rsd_lib_utils.num_or_none)
    """The static mac vlan id"""

    mac_address = base.Field("MACAddress")
    """The static mac address"""

    def update(self, mac_address, vlan_id=None):
        """Update attributes of static MAC

        :param mac_address: MAC address that should be forwarded to this port
        :param vlan_id: If specified, defines which packets tagged with
                        specific VLANId should be forwarded to this port
        """
        if not isinstance(mac_address, type("")):
            raise exceptions.InvalidParameterValueError(
                parameter="mac_address",
                value=mac_address,
                valid_values="string",
            )
        data = {"MACAddress": mac_address}

        if vlan_id is not None:
            if not isinstance(vlan_id, int):
                raise exceptions.InvalidParameterValueError(
                    parameter="vlan_id", value=vlan_id, valid_values="int"
                )
            data["VLANId"] = vlan_id

        self._conn.patch(self.path, data=data)

    def delete(self):
        """Delete this static mac address"""
        self._conn.delete(self._path)


class EthernetSwitchStaticMACCollection(rsd_lib_base.ResourceCollectionBase):
    @property
    def _resource_type(self):
        return EthernetSwitchStaticMAC

    def create_static_mac(self, mac_address, vlan_id=None):
        """Create new static MAC entry

        :param mac_address: MAC address that should be forwarded to this port
        :param vlan_id: If specified, defines which packets tagged with
                        specific VLANId should be forwarded to this port
        :returns: The location of new static MAC entry
        """
        validate(mac_address, {"type": "string"})
        data = {"MACAddress": mac_address}

        if vlan_id is not None:
            validate(vlan_id, {"type": "number"})
            data["VLANId"] = vlan_id

        resp = self._conn.post(self.path, data=data)
        LOG.info("Static MAC created at %s", resp.headers["Location"])

        static_mac_url = resp.headers["Location"]
        return static_mac_url[static_mac_url.find(self._path):]
