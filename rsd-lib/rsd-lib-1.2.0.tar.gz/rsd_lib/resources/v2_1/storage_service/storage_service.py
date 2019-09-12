# Copyright 2017 Intel, Inc.
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
from rsd_lib.resources.v2_1.storage_service import logical_drive
from rsd_lib.resources.v2_1.storage_service import physical_drive
from rsd_lib.resources.v2_1.storage_service import remote_target

LOG = logging.getLogger(__name__)


class LinksField(base.CompositeField):

    managed_by = base.Field("ManagedBy", adapter=utils.get_members_identities)


class StorageService(rsd_lib_base.ResourceBase):

    status = rsd_lib_base.StatusField("Status")
    """This indicates the known state of the resource, such as if it is
       enabled.
    """

    links = LinksField("Links")

    @property
    @utils.cache_it
    def remote_targets(self):
        """Property to provide reference to `RemoteTargetCollection` instance

           It is calculated once when it is queried for the first time. On
           refresh, this property is reset.
        """
        return remote_target.RemoteTargetCollection(
            self._conn,
            utils.get_sub_resource_path_by(self, "RemoteTargets"),
            redfish_version=self.redfish_version,
        )

    @property
    @utils.cache_it
    def logical_drives(self):
        """Property to provide reference to `LogicalDriveCollection` instance

           It is calculated once when it is queried for the first time. On
           refresh, this property is reset.
        """
        return logical_drive.LogicalDriveCollection(
            self._conn,
            utils.get_sub_resource_path_by(self, "LogicalDrives"),
            redfish_version=self.redfish_version,
        )

    @property
    @utils.cache_it
    def drives(self):
        """Property to provide reference to `PhysicalDriveCollection` instance

           It is calculated once when it is queried for the first time. On
           refresh, this property is reset.
        """
        return physical_drive.PhysicalDriveCollection(
            self._conn,
            utils.get_sub_resource_path_by(self, "Drives"),
            redfish_version=self.redfish_version,
        )


class StorageServiceCollection(rsd_lib_base.ResourceCollectionBase):
    @property
    def _resource_type(self):
        return StorageService
