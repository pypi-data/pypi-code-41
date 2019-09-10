# Copyright 2018 Intel, Inc.
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
from rsd_lib.resources.v2_1.system import network_device_function


class NetworkInterface(rsd_lib_base.ResourceBase):
    """NetworkInterface resource class

       A NetworkInterface contains references linking  NetworkDeviceFunction
       resources and represents the functionality available to the containing
       system.
    """

    status = rsd_lib_base.StatusField("Status")
    """This indicates the known state of the resource, such as if it is
       enabled.
    """

    @property
    @utils.cache_it
    def network_device_functions(self):
        """Property to provide reference to `NetworkDeviceFunctionCollection` instance

           It is calculated once when it is queried for the first time. On
           refresh, this property is reset.
        """
        return network_device_function.NetworkDeviceFunctionCollection(
            self._conn,
            utils.get_sub_resource_path_by(self, "NetworkDeviceFunctions"),
            redfish_version=self.redfish_version,
        )


class NetworkInterfaceCollection(rsd_lib_base.ResourceCollectionBase):
    @property
    def _resource_type(self):
        return NetworkInterface
