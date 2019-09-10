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

from sushy.resources import base
from sushy import utils

from rsd_lib import base as rsd_lib_base
from rsd_lib import utils as rsd_lib_utils


class LinksField(base.CompositeField):

    ethernet_interfaces = base.Field(
        "EthernetInterfaces", adapter=utils.get_members_identities
    )
    """An array of references to the ethernet interfaces which the PCIe device
       produces
    """

    drives = base.Field("Drives", adapter=utils.get_members_identities)
    """An array of references to the drives which the PCIe device produces"""

    storage_controllers = base.Field(
        "StorageControllers", adapter=utils.get_members_identities
    )
    """An array of references to the storage controllers which the PCIe device
       produces
    """

    pcie_device = base.Field(
        "PCIeDevice", adapter=rsd_lib_utils.get_resource_identity
    )
    """A reference to the PCIeDevice on which this function resides."""


class PCIeFunction(rsd_lib_base.ResourceBase):
    """PCIeFunction resource class

       This is the schema definition for the PCIeFunction resource.  It
       represents the properties of a PCIeFunction attached to a System.
    """

    function_id = base.Field("FunctionId", adapter=rsd_lib_utils.num_or_none)
    """The the PCIe Function identifier."""

    function_type = base.Field("FunctionType")
    """The type of the PCIe Function."""

    device_class = base.Field("DeviceClass")
    """The class for this PCIe Function."""

    device_id = base.Field("DeviceId")
    """The Device ID of this PCIe function."""

    vendor_id = base.Field("VendorId")
    """The Vendor ID of this PCIe function."""

    class_code = base.Field("ClassCode")
    """The Class Code of this PCIe function."""

    revision_id = base.Field("RevisionId")
    """The Revision ID of this PCIe function."""

    subsystem_id = base.Field("SubsystemId")
    """The Subsystem ID of this PCIe function."""

    subsystem_vendor_id = base.Field("SubsystemVendorId")
    """The Subsystem Vendor ID of this PCIe function."""

    status = rsd_lib_base.StatusField("Status")
    """This indicates the known state of the resource, such as if it is
       enabled.
    """

    links = LinksField("Links")
    """The links object contains the links to other resources that are related
       to this resource.
    """
