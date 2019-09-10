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

LOG = logging.getLogger(__name__)


class LinksField(base.CompositeField):

    endpoints = base.Field("Endpoints", adapter=utils.get_members_identities)
    """An array of references to the endpoints that are contained in this zone.
    """

    involved_switches = base.Field(
        "InvolvedSwitches", adapter=utils.get_members_identities
    )
    """An array of references to the switchs that are utilized in this zone."""


class Zone(rsd_lib_base.ResourceBase):
    """Zone resource class

       Switch contains properties describing a simple fabric zone.
    """

    status = rsd_lib_base.StatusField("Status")
    """This indicates the known state of the resource, such as if it is
       enabled.
    """

    links = LinksField("Links")
    """Contains references to other resources that are related to this
       resource.
    """

    def update(self, endpoints):
        """Add or remove Endpoints from a Zone

        User have to provide a full representation of Endpoints array. A
        partial update (single element update/append/detele) is not supported.
        :param endpoints: a full representation of Endpoints array
        """
        data = {"Endpoints": []}
        data["Endpoints"] = [{"@odata.id": endpoint} for endpoint in endpoints]

        self._conn.patch(self.path, data=data)


class ZoneCollection(rsd_lib_base.ResourceCollectionBase):
    @property
    def _resource_type(self):
        return Zone
