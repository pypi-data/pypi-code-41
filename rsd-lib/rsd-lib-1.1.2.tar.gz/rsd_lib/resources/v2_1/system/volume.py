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


class LinksField(base.CompositeField):

    drives = base.Field("Drives", adapter=utils.get_members_identities)
    """An array of references to the drives which contain this volume. This
       will reference Drives that either wholly or only partly contain this
       volume.
    """


class OperationsCollectionField(base.ListField):

    operation_name = base.Field("OperationName")
    """The name of the operation."""

    percentage_complete = base.Field(
        "PercentageComplete", adapter=rsd_lib_utils.num_or_none
    )
    """The percentage of the operation that has been completed."""

    associated_task = base.Field(
        "AssociatedTask", adapter=rsd_lib_utils.get_resource_identity
    )
    """A reference to the task associated with the operation if any."""


class Volume(rsd_lib_base.ResourceBase):
    """Volume resource class

       Volume contains properties used to describe a volume, virtual disk,
       LUN, or other logical storage entity for any system.
    """

    status = rsd_lib_base.StatusField("Status")
    """This indicates the known state of the resource, such as if it is
       enabled.
    """

    capacity_bytes = base.Field(
        "CapacityBytes", adapter=rsd_lib_utils.num_or_none
    )
    """The size in bytes of this Volume"""

    volume_type = base.Field("VolumeType")
    """The type of this volume"""

    encrypted = base.Field("Encrypted", adapter=bool)
    """Is this Volume encrypted"""

    encryption_types = base.Field("EncryptionTypes")
    """The types of encryption used by this Volume"""

    identifiers = rsd_lib_base.IdentifierCollectionField("Identifiers")
    """The Durable names for the volume"""

    block_size_bytes = base.Field(
        "BlockSizeBytes", adapter=rsd_lib_utils.num_or_none
    )
    """The size of the smallest addressible unit (Block) of this volume in
       bytes
    """

    operations = OperationsCollectionField("Operations")
    """The operations currently running on the Volume"""

    optimum_io_size_bytes = base.Field(
        "OptimumIOSizeBytes", adapter=rsd_lib_utils.num_or_none
    )
    """The size in bytes of this Volume's optimum IO size."""

    links = LinksField("Links")
    """Contains references to other resources that are related to this
       resource.
    """

    # TODO(linyang): Add Action Field


class VolumeCollection(rsd_lib_base.ResourceCollectionBase):
    @property
    def _resource_type(self):
        return Volume
