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
from rsd_lib import utils as rsd_lib_utils

LOG = logging.getLogger(__name__)


class LinksField(base.CompositeField):

    used_by = base.Field("UsedBy", adapter=utils.get_members_identities)


class PhysicalDrive(rsd_lib_base.ResourceBase):

    interface = base.Field("Interface")
    """Controller interface"""

    capacity_gi_b = base.Field(
        "CapacityGiB", adapter=rsd_lib_utils.num_or_none
    )
    """Drive capacity in GibiBytes."""

    type = base.Field("Type")
    """Type of drive"""

    rpm = base.Field("RPM", adapter=rsd_lib_utils.num_or_none)
    """For traditional drive, rotation per minute."""

    manufacturer = base.Field("Manufacturer")
    """Drive manufacturer name."""

    model = base.Field("Model")
    """Drive model"""

    serial_number = base.Field("SerialNumber")
    """Drive serial number"""

    status = rsd_lib_base.StatusField("Status")
    """This indicates the known state of the resource, such as if it is
       enabled.
    """

    links = LinksField("Links")


class PhysicalDriveCollection(rsd_lib_base.ResourceCollectionBase):
    @property
    def _resource_type(self):
        return PhysicalDrive
