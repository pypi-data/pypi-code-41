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

import logging

from sushy.resources import base
from sushy import utils

from rsd_lib import common as rsd_lib_common
from rsd_lib.resources.v2_3.fabric import endpoint
from rsd_lib.resources.v2_3.fabric import zone

LOG = logging.getLogger(__name__)


class Fabric(base.ResourceBase):

    description = base.Field('Description')
    """The fabric description"""

    fabric_type = base.Field('FabricType')
    """The fabric type"""

    identity = base.Field('Id', required=True)
    """The fabric identity string"""

    max_zones = base.Field('MaxZones')
    """Maximum number of zones for the fabric"""

    name = base.Field('Name')
    """The fabric name"""

    status = rsd_lib_common.StatusField('Status')

    def _get_endpoint_collection_path(self):
        """Helper function to find the EndpointCollection path"""
        return utils.get_sub_resource_path_by(self, 'Endpoints')

    @property
    @utils.cache_it
    def endpoints(self):
        """Property to provide reference to `EndpointCollection` instance

        It is calculated once when it is queried for the first time. On
        refresh, this property is reset.
        """
        return endpoint.EndpointCollection(
            self._conn, self._get_endpoint_collection_path(),
            redfish_version=self.redfish_version)

    def _get_zone_collection_path(self):
        """Helper function to find the ZoneCollection path"""
        return utils.get_sub_resource_path_by(self, 'Zones')

    @property
    @utils.cache_it
    def zones(self):
        """Property to provide reference to `ZoneCollection` instance

        It is calculated once when it is queried for the first time. On
        refresh, this property is reset.
        """
        return zone.ZoneCollection(
            self._conn, self._get_zone_collection_path(),
            redfish_version=self.redfish_version)


class FabricCollection(base.ResourceCollectionBase):

    @property
    def _resource_type(self):
        return Fabric
