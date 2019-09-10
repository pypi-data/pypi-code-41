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

from rsd_lib import base as rsd_lib_base
from rsd_lib.resources.v2_1.common import message


class Task(rsd_lib_base.ResourceBase):
    """Task resource class

       This resource contains information about a specific Task scheduled by
       or being executed by a Redfish service's Task Service.
    """

    task_state = base.Field("TaskState")
    """The state of the task."""

    start_time = base.Field("StartTime")
    """The date-time stamp that the task was last started."""

    end_time = base.Field("EndTime")
    """The date-time stamp that the task was last completed."""

    task_status = base.Field("TaskStatus")
    """This is the completion status of the task."""

    messages = message.MessageCollectionField("Messages")
    """This is an array of messages associated with the task."""

    def delete(self):
        """Delete this task"""
        self._conn.delete(self.path)


class TaskCollection(rsd_lib_base.ResourceCollectionBase):
    @property
    def _resource_type(self):
        return Task
