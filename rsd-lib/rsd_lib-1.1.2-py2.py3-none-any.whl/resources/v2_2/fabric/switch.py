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
from rsd_lib.resources.v2_1.fabric import switch
from rsd_lib.resources.v2_2.fabric import port


class Switch(switch.Switch):
    """Switch resource class

       Switch contains properties describing a simple fabric switch.
    """

    @property
    @utils.cache_it
    def ports(self):
        """Property to provide reference to `PortCollection` instance

           It is calculated once when it is queried for the first time. On
           refresh, this property is reset.
        """
        return port.PortCollection(
            self._conn,
            utils.get_sub_resource_path_by(self, "Ports"),
            redfish_version=self.redfish_version,
        )


class SwitchCollection(rsd_lib_base.ResourceCollectionBase):
    @property
    def _resource_type(self):
        return Switch
