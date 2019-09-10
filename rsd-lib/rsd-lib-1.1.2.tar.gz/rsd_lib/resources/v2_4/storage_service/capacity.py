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
from rsd_lib.resources.v2_3.storage_service import drive
from rsd_lib.resources.v2_3.storage_service import storage_pool
from rsd_lib import utils as rsd_lib_utils


class CapacityInfoField(base.CompositeField):
    """CapacityInfo field

       The capacity of specific data type in a data store.
    """

    consumed_bytes = base.Field(
        "ConsumedBytes", adapter=rsd_lib_utils.num_or_none
    )
    """The number of bytes consumed in this data store for this data type."""

    allocated_bytes = base.Field(
        "AllocatedBytes", adapter=rsd_lib_utils.num_or_none
    )
    """The number of bytes currently allocated by the storage system in this
       data store for this data type.
    """

    guaranteed_bytes = base.Field(
        "GuaranteedBytes", adapter=rsd_lib_utils.num_or_none
    )
    """The number of bytes the storage system guarantees can be allocated in
       this data store for this data type.
    """

    provisioned_bytes = base.Field(
        "ProvisionedBytes", adapter=rsd_lib_utils.num_or_none
    )
    """The maximum number of bytes that can be allocated in this data store
       for this data type.
    """


class CapacityField(base.CompositeField):
    """Capacity field

       This is the schema definition for the Capacity of a device. It
       represents the properties for capacity for any data store.
    """

    data = CapacityInfoField("Data")
    """The capacity information relating to the user data."""

    metadata = CapacityInfoField("Metadata")
    """The capacity information relating to  metadata."""

    snapshot = CapacityInfoField("Snapshot")
    """The capacity information relating to snapshot or backup data."""

    is_thin_provisioned = base.Field("IsThinProvisioned", adapter=bool)
    """Marks that the capacity is not necessarily fully allocated."""


class CapacitySource(rsd_lib_base.ResourceBase):
    """CapacitySource resource class

       A description of the type and source of storage.
    """

    provided_capacity = CapacityField("ProvidedCapacity")
    """The amount of space that has been provided from the ProvidingDrives,
       ProvidingVolumes, ProvidingMemory or ProvidingPools.
    """

    # TODO(lin.yang): Add property for references in CapacitySource resource

    @property
    @utils.cache_it
    def providing_volumes(self):
        """Property to provide reference to `VolumeCollection` instance

           It is calculated once when it is queried for the first time. On
           refresh, this property is reset.
        """
        from rsd_lib.resources.v2_4.storage_service import volume

        return [
            volume.VolumeCollection(
                self._conn, path, redfish_version=self.redfish_version
            )
            for path in utils.get_sub_resource_path_by(
                self, "ProvidingVolumes", is_collection=True
            )
        ]

    @property
    @utils.cache_it
    def providing_pools(self):
        """Property to provide reference to `StoragePoolCollection` instance

           It is calculated once when it is queried for the first time. On
           refresh, this property is reset.
        """
        return [
            storage_pool.StoragePoolCollection(
                self._conn, path, redfish_version=self.redfish_version
            )
            for path in utils.get_sub_resource_path_by(
                self, "ProvidingPools", is_collection=True
            )
        ]

    @property
    @utils.cache_it
    def providing_drives(self):
        """Property to provide reference to `DriveCollection` instance

           It is calculated once when it is queried for the first time. On
           refresh, this property is reset.
        """
        return [
            drive.DriveCollection(
                self._conn, path, redfish_version=self.redfish_version
            )
            for path in utils.get_sub_resource_path_by(
                self, "ProvidingDrives", is_collection=True
            )
        ]
