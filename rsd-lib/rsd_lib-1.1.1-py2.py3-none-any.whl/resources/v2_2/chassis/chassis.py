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

from sushy import utils

from rsd_lib import base as rsd_lib_base
from rsd_lib.resources.v2_1.chassis import chassis
from rsd_lib.resources.v2_2.chassis import power
from rsd_lib.resources.v2_2.chassis import thermal


class Chassis(chassis.Chassis):
    """Chassis resource class

       A Chassis represents the physical components for any system.  This
       resource represents the sheet-metal confined spaces and logical zones
       like racks, enclosures, chassis and all other containers. Subsystems
       (like sensors), which operate outside of a system's data plane (meaning
       the resources are not accessible to software running on the system) are
       linked either directly or indirectly through this resource.
    """

    @property
    @utils.cache_it
    def power(self):
        """Property to provide reference to `Power` instance

           It is calculated once when it is queried for the first time. On
           refresh, this property is reset.
        """
        return power.Power(
            self._conn,
            utils.get_sub_resource_path_by(self, "Power"),
            redfish_version=self.redfish_version,
        )

    @property
    @utils.cache_it
    def thermal(self):
        """Property to provide reference to `Thermal` instance

           It is calculated once when it is queried for the first time. On
           refresh, this property is reset.
        """
        return thermal.Thermal(
            self._conn,
            utils.get_sub_resource_path_by(self, "Thermal"),
            redfish_version=self.redfish_version,
        )


class ChassisCollection(rsd_lib_base.ResourceCollectionBase):
    @property
    def _resource_type(self):
        return Chassis
