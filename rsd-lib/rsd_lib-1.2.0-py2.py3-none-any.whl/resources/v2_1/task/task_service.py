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
from rsd_lib.resources.v2_1.task import task


class TaskService(rsd_lib_base.ResourceBase):
    """TaskService resource class

       This is the schema definition for the Task Service.  It represents the
       properties for the service itself and has links to the actual list of
       tasks.
    """

    completed_task_over_write_policy = base.Field(
        "CompletedTaskOverWritePolicy"
    )
    """Overwrite policy of completed tasks"""

    date_time = base.Field("DateTime")
    """The current DateTime (with offset) setting that the task service is
       using.
    """

    life_cycle_event_on_task_state_change = base.Field(
        "LifeCycleEventOnTaskStateChange", adapter=bool
    )
    """Send an Event upon Task State Change."""

    service_enabled = base.Field("ServiceEnabled", adapter=bool)
    """This indicates whether this service is enabled."""

    status = rsd_lib_base.StatusField("Status")
    """This indicates the known state of the resource, such as if it is
       enabled.
    """

    @property
    @utils.cache_it
    def tasks(self):
        """Property to provide reference to `TaskCollection` instance

           It is calculated once when it is queried for the first time. On
           refresh, this property is reset.
        """
        return task.TaskCollection(
            self._conn,
            utils.get_sub_resource_path_by(self, "Tasks"),
            redfish_version=self.redfish_version,
        )
