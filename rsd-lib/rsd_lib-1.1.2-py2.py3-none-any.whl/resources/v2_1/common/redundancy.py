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
from rsd_lib import utils as rsd_lib_utils


class RedundancyCollectionField(rsd_lib_base.ReferenceableMemberField):
    """Redundancy field

       This is the redundancy definition to be used in other resource schemas.
    """

    name = base.Field("Name")
    """The name of the resource or array element."""

    mode = base.Field("Mode")
    """This is the redundancy mode of the group."""

    max_num_supported = base.Field(
        "MaxNumSupported", adapter=rsd_lib_utils.num_or_none
    )
    """This is the maximum number of members allowable for this particular
       redundancy group.
    """

    min_num_needed = base.Field(
        "MinNumNeeded", adapter=rsd_lib_utils.num_or_none
    )
    """This is the minumum number of members needed for this group to be
       redundant.
    """

    status = rsd_lib_base.StatusField("Status")
    """This indicates the known state of the resource, such as if it is
       enabled.
    """

    redundancy_set = base.Field(
        "RedundancySet", adapter=utils.get_members_identities
    )
    """Contains any ids that represent components of this redundancy set."""

    redundancy_enabled = base.Field("RedundancyEnabled", adapter=bool)
    """This indicates whether redundancy is enabled."""
