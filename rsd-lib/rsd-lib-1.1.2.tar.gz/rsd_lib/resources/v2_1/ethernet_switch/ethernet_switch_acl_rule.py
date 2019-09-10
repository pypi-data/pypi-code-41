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
from rsd_lib.resources.v2_1.ethernet_switch import ethernet_switch_port
from rsd_lib.resources.v2_1.ethernet_switch import schemas as acl_rule_schema
from rsd_lib import utils as rsd_lib_utils

LOG = logging.getLogger(__name__)


class PortConditionTypeField(base.CompositeField):

    port = base.Field("Port", adapter=rsd_lib_utils.num_or_none)

    mask = base.Field("Mask", adapter=rsd_lib_utils.num_or_none)


class VlanIdConditionTypeField(base.CompositeField):

    identity = base.Field("Id", adapter=rsd_lib_utils.num_or_none)

    mask = base.Field("Mask", adapter=rsd_lib_utils.num_or_none)


class MACConditionTypeField(base.CompositeField):

    mac_address = base.Field("MACAddress")

    mask = base.Field("Mask")


class IPConditionTypeField(base.CompositeField):

    ipv4_address = base.Field("IPv4Address")

    mask = base.Field("Mask")


class ConditionTypeField(base.CompositeField):

    ip_source = IPConditionTypeField("IPSource")

    ip_destination = IPConditionTypeField("IPDestination")

    mac_source = MACConditionTypeField("MACSource")

    mac_destination = MACConditionTypeField("MACDestination")

    vlan_id = VlanIdConditionTypeField("VLANId")

    l4_source_port = PortConditionTypeField("L4SourcePort")

    l4_destination_port = PortConditionTypeField("L4DestinationPort")

    l4_protocol = base.Field("L4Protocol", adapter=rsd_lib_utils.num_or_none)


class EthernetSwitchACLRule(rsd_lib_base.ResourceBase):
    """EthernetSwitchACLRule resource class

       A Ethernet Switch ACL Rule represents Access Control List rule for
       switch.
    """

    rule_id = base.Field("RuleId", adapter=rsd_lib_utils.num_or_none)
    """This is ACL rule ID which determine rule priority."""

    action = base.Field("Action")
    """Action that will be executed when rule condition will be met.s"""

    mirror_type = base.Field("MirrorType")
    """Type of mirroring that should be use for Mirror action."""

    condition = ConditionTypeField("Condition")
    """Property contain set of conditions that should be met to trigger Rule
       action.
    """

    def delete(self):
        """Delete this ACL rule"""
        self._conn.delete(self._path)

    @property
    @utils.cache_it
    def forward_mirror_interface(self):
        """Property to provide reference to `EthernetSwitchPort` instance

           It is calculated once when it is queried for the first time. On
           refresh, this property is reset.
        """
        return ethernet_switch_port.EthernetSwitchPort(
            self._conn,
            utils.get_sub_resource_path_by(self, "ForwardMirrorInterface"),
            redfish_version=self.redfish_version,
        )

    @property
    @utils.cache_it
    def mirror_port_region(self):
        """Property to provide a list of `EthernetSwitchPort` instance

           It is calculated once when it is queried for the first time. On
           refresh, this property is reset.
        """
        return [
            ethernet_switch_port.EthernetSwitchPort(
                self._conn, path, redfish_version=self.redfish_version
            )
            for path in rsd_lib_utils.get_sub_resource_path_list_by(
                self, "MirrorPortRegion"
            )
        ]

    def update(self, data=None):
        """Update a new ACL rule

        :param data: JSON for acl_rule
        """
        update_schema = acl_rule_schema.acl_rule_req_schema
        del update_schema["required"]
        if data is not None or len(data) > 0:
            validate(data, update_schema)
        self._conn.patch(self.path, data=data)


class EthernetSwitchACLRuleCollection(rsd_lib_base.ResourceCollectionBase):
    @property
    def _resource_type(self):
        return EthernetSwitchACLRule

    def create_acl_rule(self, acl_rule_req):
        """Create a new ACL rule

        :param acl_rule: JSON for acl_rule
        :returns: The location of the acl rule
        """
        target_uri = self._path
        validate(acl_rule_req, acl_rule_schema.acl_rule_req_schema)
        resp = self._conn.post(target_uri, data=acl_rule_req)
        acl_rule_url = resp.headers["Location"]
        LOG.info("Create ACL Rule at %s", acl_rule_url)
        return acl_rule_url[acl_rule_url.find(self._path):]
