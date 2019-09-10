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

from sushy.resources import base
from sushy import utils

from rsd_lib import base as rsd_lib_base
from rsd_lib.resources.v2_1.ethernet_switch import ethernet_switch_acl
from rsd_lib.resources.v2_1.ethernet_switch import ethernet_switch_port
from rsd_lib import utils as rsd_lib_utils


LOG = logging.getLogger(__name__)


class LinksField(base.CompositeField):

    chassis = base.Field(
        "Chassis", default=(), adapter=rsd_lib_utils.get_resource_identity
    )
    """Link to chassis of this ethernet switch"""

    managed_by = base.Field(
        "ManagedBy", default=(), adapter=utils.get_members_identities
    )
    """Link to manager of this  ethernet switch"""


class EthernetSwitch(rsd_lib_base.ResourceBase):

    switch_id = base.Field("SwitchId")
    """Unique switch Id (within drawer) used to identify in switch hierarchy
       discovery.
    """

    manufacturer = base.Field("Manufacturer")
    """Switch manufacturer name"""

    model = base.Field("Model")
    """Switch model"""

    manufacturing_date = base.Field("ManufacturingDate")
    """Manufacturing date"""

    serial_number = base.Field("SerialNumber")
    """Switch serial numberSS"""

    part_number = base.Field("PartNumber")
    """Switch part number"""

    firmware_name = base.Field("FirmwareName")
    """Switch firmware name"""

    firmware_version = base.Field("FirmwareVersion")
    """Switch firmware version"""

    role = base.Field("Role")
    """"""

    max_acl_number = base.Field(
        "MaxACLNumber", adapter=rsd_lib_utils.num_or_none
    )
    """Role of switch"""

    status = rsd_lib_base.StatusField("Status")
    """This indicates the known state of the resource, such as if it is
       enabled.
    """

    links = LinksField("Links")

    @property
    @utils.cache_it
    def ports(self):
        """Property to provide reference to `EthernetSwitchPortCollection` instance

           It is calculated once when it is queried for the first time. On
           refresh, this property is reset.
        """
        return ethernet_switch_port.EthernetSwitchPortCollection(
            self._conn,
            utils.get_sub_resource_path_by(self, "Ports"),
            redfish_version=self.redfish_version,
        )

    @property
    @utils.cache_it
    def acls(self):
        """Property to provide reference to `EthernetSwitchACLCollection` instance

           It is calculated once when it is queried for the first time. On
           refresh, this property is reset.
        """
        return ethernet_switch_acl.EthernetSwitchACLCollection(
            self._conn,
            utils.get_sub_resource_path_by(self, "ACLs"),
            redfish_version=self.redfish_version,
        )


class EthernetSwitchCollection(rsd_lib_base.ResourceCollectionBase):
    @property
    def _resource_type(self):
        return EthernetSwitch
