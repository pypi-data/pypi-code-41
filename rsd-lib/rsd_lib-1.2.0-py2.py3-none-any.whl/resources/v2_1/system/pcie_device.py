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


class LinksField(base.CompositeField):

    chassis = base.Field("Chassis", adapter=utils.get_members_identities)
    """An array of references to the chassis in which the PCIe device is
       contained
    """

    pcie_functions = base.Field(
        "PCIeFunctions", adapter=utils.get_members_identities
    )
    """An array of references to PCIeFunctions exposed by this device."""


class PCIeDevice(rsd_lib_base.ResourceBase):
    """PCIeDevice resource class

       This is the schema definition for the PCIeDevice resource.  It
       represents the properties of a PCIeDevice attached to a System.
    """

    manufacturer = base.Field("Manufacturer")
    """This is the manufacturer of this PCIe device."""

    model = base.Field("Model")
    """This is the model number for the PCIe device."""

    sku = base.Field("SKU")
    """This is the SKU for this PCIe device."""

    serial_number = base.Field("SerialNumber")
    """The serial number for this PCIe device."""

    part_number = base.Field("PartNumber")
    """The part number for this PCIe device."""

    asset_tag = base.Field("AssetTag")
    """The user assigned asset tag for this PCIe device."""

    device_type = base.Field("DeviceType")
    """The device type for this PCIe device."""

    firmware_version = base.Field("FirmwareVersion")
    """The version of firmware for this PCIe device."""

    status = rsd_lib_base.StatusField("Status")
    """This indicates the known state of the resource, such as if it is
       enabled.
    """

    links = LinksField("Links")
    """The links object contains the links to other resources that are related
       to this resource.
    """

    def update(self, asset_tag):
        """Update AssetTag properties

        :param asset_tag: The user assigned asset tag for this PCIe device
        """
        data = {"AssetTag": asset_tag}
        self._conn.patch(self.path, data=data)
