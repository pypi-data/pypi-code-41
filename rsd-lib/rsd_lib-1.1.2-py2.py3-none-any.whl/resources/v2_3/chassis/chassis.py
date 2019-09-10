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
from rsd_lib.resources.v2_1.chassis import chassis
from rsd_lib.resources.v2_1.chassis import log_service
from rsd_lib.resources.v2_2.chassis import power
from rsd_lib.resources.v2_2.chassis import thermal
from rsd_lib import utils as rsd_lib_utils


class LinksField(chassis.LinksField):

    pcie_devices = base.Field(
        "PCIeDevices", adapter=utils.get_members_identities
    )
    """An array of references to the PCIe Devices located in this Chassis."""


class Chassis(rsd_lib_base.ResourceBase):
    """Chassis resource class

       A Chassis represents the physical components for any system.  This
       resource represents the sheet-metal confined spaces and logical zones
       like racks, enclosures, chassis and all other containers. Subsystems
       (like sensors), which operate outside of a system's data plane (meaning
       the resources are not accessible to software running on the system) are
       linked either directly or indirectly through this resource.
    """

    chassis_type = base.Field("ChassisType")
    """This property indicates the type of physical form factor of this
       resource.
    """

    manufacturer = base.Field("Manufacturer")
    """This is the manufacturer of this chassis."""

    model = base.Field("Model")
    """This is the model number for the chassis."""

    sku = base.Field("SKU")
    """This is the SKU for this chassis."""

    serial_number = base.Field("SerialNumber")
    """The serial number for this chassis."""

    part_number = base.Field("PartNumber")
    """The part number for this chassis."""

    asset_tag = base.Field("AssetTag")
    """The user assigned asset tag for this chassis."""

    indicator_led = base.Field("IndicatorLED")
    """The state of the indicator LED, used to identify the chassis."""

    links = LinksField("Links")
    """Contains references to other resources that are related to this
       resource.
    """

    status = rsd_lib_base.StatusField("Status")
    """This indicates the known state of the resource, such as if it is
       enabled.
    """

    power_state = base.Field("PowerState")
    """This is the current power state of the chassis."""

    physical_security = chassis.PhysicalSecurityField("PhysicalSecurity")
    """The state of the physical security sensor."""

    location = rsd_lib_base.LocationField("Location")
    """Location of a resource"""

    height_mm = base.Field("HeightMm", adapter=rsd_lib_utils.num_or_none)
    """The height of the chassis."""

    width_mm = base.Field("WidthMm", adapter=rsd_lib_utils.num_or_none)
    """The width of the chassis."""

    depth_mm = base.Field("DepthMm", adapter=rsd_lib_utils.num_or_none)
    """The depth of the chassis."""

    weight_kg = base.Field("WeightKg", adapter=rsd_lib_utils.num_or_none)
    """The weight of the chassis."""

    oem = chassis.OemField("Oem")
    """Oem specific properties."""

    @property
    @utils.cache_it
    def log_services(self):
        """Property to provide reference to `LogServiceCollection` instance

           It is calculated once when it is queried for the first time. On
           refresh, this property is reset.
        """
        return log_service.LogServiceCollection(
            self._conn,
            utils.get_sub_resource_path_by(self, "LogServices"),
            redfish_version=self.redfish_version,
        )

    @property
    @utils.cache_it
    def thermal(self):
        """Property to provide reference to `Thermal` instance

           It is calculated once when it is queried for the first time. On
           refresh, this property is reset.
        """
        return thermal.Thermal(
            self._conn,
            utils.get_sub_resource_path_by(self, "Thermal"),
            redfish_version=self.redfish_version,
        )

    @property
    @utils.cache_it
    def power(self):
        """Property to provide reference to `Power` instance

           It is calculated once when it is queried for the first time. On
           refresh, this property is reset.
        """
        return power.Power(
            self._conn,
            utils.get_sub_resource_path_by(self, "Power"),
            redfish_version=self.redfish_version,
        )

    def update(self, asset_tag=None, location_id=None):
        """Update AssetTag and Location->Id properties

        :param asset_tag: The user assigned asset tag for this chassis
        :param location_id: The user assigned location id for this chassis.
                            It can be changed only for a Rack Chassis
        """

        data = {}

        if asset_tag is not None:
            data["AssetTag"] = asset_tag

        if location_id is not None:
            data["Oem"] = {
                "Intel_RackScale": {"Location": {"Id": location_id}}
            }

        self._conn.patch(self.path, data=data)


class ChassisCollection(rsd_lib_base.ResourceCollectionBase):
    @property
    def _resource_type(self):
        return Chassis
