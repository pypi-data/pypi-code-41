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
from rsd_lib import utils as rsd_lib_utils


class DeviceCollectionField(base.ListField):

    name = base.Field("Name")
    """The name of the resource or array element."""

    status = rsd_lib_base.StatusField("Status")
    """This indicates the known state of the resource, such as if it is
       enabled.
    """

    manufacturer = base.Field("Manufacturer")
    """The name of the manufacturer of this device"""

    model = base.Field("Model")
    """The product model number of this device"""

    capacity_bytes = base.Field(
        "CapacityBytes", adapter=rsd_lib_utils.num_or_none
    )
    """The size of the storage device."""


class SimpleStorage(rsd_lib_base.ResourceBase):
    """SimpleStorage resource class

       This is the schema definition for the Simple Storage resource.  It
       represents the properties of a storage controller and its
       directly-attached devices.
    """

    uefi_device_path = base.Field("UefiDevicePath")
    """The UEFI device path used to access this storage controller."""

    devices = DeviceCollectionField("Devices")
    """The storage devices associated with this resource"""

    status = rsd_lib_base.StatusField("Status")
    """This indicates the known state of the resource, such as if it is
       enabled.
    """


class SimpleStorageCollection(rsd_lib_base.ResourceCollectionBase):
    @property
    def _resource_type(self):
        return SimpleStorage
