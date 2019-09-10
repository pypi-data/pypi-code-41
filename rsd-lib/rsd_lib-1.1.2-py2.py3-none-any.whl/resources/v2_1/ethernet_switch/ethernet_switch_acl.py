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

from sushy import exceptions
from sushy.resources import base
from sushy.resources import common
from sushy import utils

from rsd_lib import base as rsd_lib_base
from rsd_lib.resources.v2_1.ethernet_switch import ethernet_switch_acl_rule

LOG = logging.getLogger(__name__)


class BindActionField(common.ActionField):

    allowed_values = base.Field(
        "Port@Redfish.AllowableValues", adapter=utils.get_members_identities
    )


class UnbindActionField(common.ActionField):

    allowed_values = base.Field(
        "Port@Redfish.AllowableValues", adapter=utils.get_members_identities
    )


class EthernetSwitchACLActionsField(base.CompositeField):

    bind = BindActionField("#EthernetSwitchACL.Bind")
    unbind = UnbindActionField("#EthernetSwitchACL.Unbind")


class LinksField(base.CompositeField):

    bound_ports = base.Field(
        "BoundPorts", adapter=utils.get_members_identities
    )


class EthernetSwitchACL(rsd_lib_base.ResourceBase):
    """EthernetSwitchACL resource class

       A Ethernet Switch ACL represents Access Control List for switch.
    """

    links = LinksField("Links")

    _actions = EthernetSwitchACLActionsField("Actions")

    def _get_bind_action_element(self):
        bind_action = self._actions.bind
        if not bind_action:
            raise exceptions.MissingActionError(
                action="#EthernetSwitchACL.Bind", resource=self._path
            )
        return bind_action

    def get_allowed_bind_ports(self):
        """Get the allowed ports for bind action.

        :returns: A set with the allowed bind ports.
        """
        bind_action = self._get_bind_action_element()
        return bind_action.allowed_values

    def bind_port(self, port):
        """Bind port from this switch ACL

        :param port: Link to port to bind.
        :raises: InvalidParameterValueError
        """
        bind_action = self._get_bind_action_element()
        valid_ports = bind_action.allowed_values
        target_uri = bind_action.target_uri

        if port and port not in valid_ports:
            raise exceptions.InvalidParameterValueError(
                parameter="port", value=port, valid_values=valid_ports
            )

        data = {"Port": {"@odata.id": port}}

        self._conn.post(target_uri, data=data)

    def _get_unbind_action_element(self):
        unbind_action = self._actions.unbind
        if not unbind_action:
            raise exceptions.MissingActionError(
                action="#EthernetSwitchACL.Unbind", resource=self._path
            )
        return unbind_action

    def get_allowed_unbind_ports(self):
        """Get the allowed ports for unbind action.

        :returns: A set with the allowed unbind ports.
        """
        unbind_action = self._get_unbind_action_element()
        return unbind_action.allowed_values

    def unbind_port(self, port):
        """Unbind port from this switch ACL

        :param port: Link to port to unbind.
        :raises: InvalidParameterValueError
        """
        unbind_action = self._get_unbind_action_element()
        valid_ports = unbind_action.allowed_values
        target_uri = unbind_action.target_uri

        if port and port not in valid_ports:
            raise exceptions.InvalidParameterValueError(
                parameter="port", value=port, valid_values=valid_ports
            )

        data = {"Port": {"@odata.id": port}}

        self._conn.post(target_uri, data=data)

    def delete(self):
        """Delete this ACL"""
        self._conn.delete(self._path)

    @property
    @utils.cache_it
    def rules(self):
        """Property to provide reference to `EthernetSwitchACLRuleCollection` instance

           It is calculated once when it is queried for the first time. On
           refresh, this property is reset.
        """
        return ethernet_switch_acl_rule.EthernetSwitchACLRuleCollection(
            self._conn,
            utils.get_sub_resource_path_by(self, "Rules"),
            redfish_version=self.redfish_version,
        )


class EthernetSwitchACLCollection(rsd_lib_base.ResourceCollectionBase):

    @property
    def _resource_type(self):
        return EthernetSwitchACL

    def create_acl(self):
        """Create a new ACL

        :returns: The location of the acl rule
        """
        target_uri = self._path

        resp = self._conn.post(target_uri, data={})
        acl_url = resp.headers["Location"]

        LOG.info("Create ACL at %s", acl_url)
        return acl_url[acl_url.find(self._path):]
