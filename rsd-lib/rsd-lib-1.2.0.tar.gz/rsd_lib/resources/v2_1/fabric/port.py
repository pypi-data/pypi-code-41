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

import logging

from sushy import exceptions
from sushy.resources import base
from sushy.resources import common
from sushy import utils

from rsd_lib import base as rsd_lib_base
from rsd_lib import utils as rsd_lib_utils

LOG = logging.getLogger(__name__)


class LinksIntelRackScaleField(base.CompositeField):

    neighbor_port = base.Field(
        "NeighborPort", adapter=utils.get_members_identities
    )
    """This indicates neighbor port which is connected to this port"""


class LinksOemField(base.CompositeField):

    intel_rackscale = LinksIntelRackScaleField("Intel_RackScale")
    """Intel Rack Scale Design specific properties."""


class ActionsField(base.CompositeField):

    reset = common.ResetActionField("#Port.Reset")
    """The action port reset"""


class IntelRackScaleField(base.CompositeField):

    pcie_connection_id = base.Field("PCIeConnectionId")
    """An array of references to the PCIe connection identifiers (e.g. cable
       ID).
    """


class LinksField(base.CompositeField):

    associated_endpoints = base.Field(
        "AssociatedEndpoints", adapter=utils.get_members_identities
    )
    """An array of references to the endpoints that connect to the switch
       through this port.
    """

    connected_switches = base.Field(
        "ConnectedSwitches", adapter=utils.get_members_identities
    )
    """An array of references to the switches that connect to the switch
       through this port.
    """

    connected_switch_ports = base.Field(
        "ConnectedSwitchPorts", adapter=utils.get_members_identities
    )
    """An array of references to the ports that connect to the switch through
       this port.
    """

    oem = LinksOemField("Oem")
    """Oem specific properties."""


class OemField(base.CompositeField):

    intel_rackscale = IntelRackScaleField("Intel_RackScale")
    """The oem intel rack scale"""


class Port(rsd_lib_base.ResourceBase):
    """Port resource class

       Port contains properties describing a port of a switch.
    """

    status = rsd_lib_base.StatusField("Status")
    """This indicates the known state of the resource, such as if it is
       enabled.
    """

    port_id = base.Field("PortId")
    """This is the label of this port on the physical switch package."""

    port_protocol = base.Field("PortProtocol")
    """The protocol being sent over this port."""

    port_type = base.Field("PortType")
    """This is the type of this port."""

    current_speed_gbps = base.Field(
        "CurrentSpeedGbps", adapter=rsd_lib_utils.num_or_none
    )
    """The current speed of this port."""

    max_speed_gbps = base.Field(
        "MaxSpeedGbps", adapter=rsd_lib_utils.num_or_none
    )
    """The maximum speed of this port as currently configured."""

    width = base.Field("Width", adapter=rsd_lib_utils.num_or_none)
    """The number of lanes, phys, or other physical transport links that this
       port contains.
    """

    links = LinksField("Links")
    """Contains references to other resources that are related to this
       resource.
    """

    oem = OemField("Oem")
    """Oem specific properties."""

    actions = ActionsField("Actions")
    """The port actions"""

    def _get_reset_action_element(self):
        reset_action = self.actions.reset
        if not reset_action:
            raise exceptions.MissingActionError(
                action="#Port.Reset", resource=self._path
            )
        return reset_action

    def get_allowed_reset_port_values(self):
        """Get the allowed values for resetting the port.

        :returns: A set with the allowed values.
        """
        reset_action = self._get_reset_action_element()

        return reset_action.allowed_values

    def reset_port(self, value):
        """Reset the port.

        :param value: The target value.
        :raises: InvalidParameterValueError, if the target value is not
            allowed.
        """
        valid_resets = self.get_allowed_reset_port_values()
        if value not in valid_resets:
            raise exceptions.InvalidParameterValueError(
                parameter="value", value=value, valid_values=valid_resets
            )

        target_uri = self._get_reset_action_element().target_uri

        self._conn.post(target_uri, data={"ResetType": value})


class PortCollection(rsd_lib_base.ResourceCollectionBase):
    @property
    def _resource_type(self):
        return Port
