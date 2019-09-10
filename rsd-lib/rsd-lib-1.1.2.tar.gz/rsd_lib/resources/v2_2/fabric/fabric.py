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
from rsd_lib.resources.v2_1.fabric import fabric
from rsd_lib.resources.v2_2.fabric import switch


class Fabric(fabric.Fabric):
    """Fabric resource class

       Fabric contains properties describing a simple fabric consisting of one
       or more switches, zero or more endpoints, and zero or more zones.
    """

    @property
    @utils.cache_it
    def switches(self):
        """Property to provide reference to `SwitchCollection` instance

           It is calculated once when it is queried for the first time. On
           refresh, this property is reset.
        """
        return switch.SwitchCollection(
            self._conn,
            utils.get_sub_resource_path_by(self, "Switches"),
            redfish_version=self.redfish_version,
        )


class FabricCollection(rsd_lib_base.ResourceCollectionBase):
    @property
    def _resource_type(self):
        return Fabric
