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

from sushy.resources import base
from sushy import utils

from rsd_lib import base as rsd_lib_base
from rsd_lib.resources.v2_2.update_service import action_info


class SimpleUpdateField(base.CompositeField):
    target = base.Field("target")
    """The simple update target"""


class ActionsField(base.CompositeField):
    simple_update = SimpleUpdateField("#UpdateService.SimpleUpdate")
    """The actions simple update"""

    oem = base.Field("Oem")
    """The actions oem"""


class UpdateService(rsd_lib_base.ResourceBase):
    """UpdateService resource class

       This is the schema definition for the Update Service. It represents the
       properties for the service itself and has links to collections of
       firmware and software inventory.
    """

    status = rsd_lib_base.StatusField("Status")
    """This indicates the known state of the resource, such as if it is
       enabled.
    """

    service_enabled = base.Field("ServiceEnabled", adapter=bool)
    """This indicates whether this service is enabled."""

    http_push_uri = base.Field("HttpPushUri")
    """The URI used to perform an HTTP or HTTPS push update to the Update
       Service.
    """

    actions = ActionsField("Actions")
    """The update service actions"""

    def _get_action_info_path(self):
        """Helper function to find the ActionInfo path"""
        return (
            self.json.get("Actions")
            .get("#UpdateService.SimpleUpdate")
            .get("@Redfish.ActionInfo")
        )

    @property
    @utils.cache_it
    def action_info(self):
        """Property to provide reference to `ActionInfo` instance

        It is calculated once when it is queried for the first time. On
        refresh, this property is reset.
        """
        return action_info.ActionInfo(
            self._conn,
            self._get_action_info_path(),
            redfish_version=self.redfish_version,
        )
