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

from sushy.resources import base
from sushy import utils

from rsd_lib import base as rsd_lib_base
from rsd_lib.resources.v2_1.fabric import port
from rsd_lib.resources.v2_2.fabric import port_metrics
from rsd_lib import utils as rsd_lib_utils


LOG = logging.getLogger(__name__)


class IntelRackScaleField(base.CompositeField):

    pc_ie_connection_id = base.Field("PCIeConnectionId")
    """An array of references to the PCIe connection identifiers (e.g. cable
       ID).
    """

    metrics = base.Field(
        "Metrics", adapter=rsd_lib_utils.get_resource_identity
    )
    """A reference to the Metrics associated with this Port"""


class OemField(base.CompositeField):

    intel_rackscale = IntelRackScaleField("Intel_RackScale")
    """Intel Rack Scale Design specific properties."""


class Port(port.Port):
    """Port resource class

       Port contains properties describing a port of a switch.
    """

    oem = OemField("Oem")
    """Oem specific properties."""

    @property
    @utils.cache_it
    def metrics(self):
        """Property to provide reference to `Metrics` instance

        It is calculated once the first time it is queried. On refresh,
        this property is reset.
        """
        return port_metrics.PortMetrics(
            self._conn,
            utils.get_sub_resource_path_by(
                self, ["Oem", "Intel_RackScale", "Metrics"]
            ),
            redfish_version=self.redfish_version,
        )


class PortCollection(rsd_lib_base.ResourceCollectionBase):
    @property
    def _resource_type(self):
        return Port
