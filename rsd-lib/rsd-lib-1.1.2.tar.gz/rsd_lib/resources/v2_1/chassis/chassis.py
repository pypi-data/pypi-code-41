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

from sushy.resources import base
from sushy import utils

from rsd_lib import base as rsd_lib_base
from rsd_lib.resources.v2_1.chassis import log_service
from rsd_lib.resources.v2_1.chassis import power
from rsd_lib.resources.v2_1.chassis import power_zone
from rsd_lib.resources.v2_1.chassis import thermal
from rsd_lib.resources.v2_1.chassis import thermal_zone
from rsd_lib import utils as rsd_lib_utils


class LocationField(base.CompositeField):

    identity = base.Field("Id")
    """The location ID of the chassis"""

    parent_id = base.Field("ParentId")
    """The location ID of parent chassis"""


class LinksIntelRackScaleField(base.CompositeField):

    switches = base.Field("Switches", adapter=utils.get_members_identities)
    """An array of references to the ethernet switches located in this Chassis.
    """


class LinksOemField(base.CompositeField):

    intel_rackscale = LinksIntelRackScaleField("Intel_RackScale")
    """Intel Rack Scale Design specific properties."""


class LinksField(base.CompositeField):

    computer_systems = base.Field(
        "ComputerSystems", adapter=utils.get_members_identities
    )
    """An array of references to the computer systems contained in this
       chassis.  This will only reference ComputerSystems that are directly
       and wholly contained in this chassis.
    """

    managed_by = base.Field("ManagedBy", adapter=utils.get_members_identities)
    """An array of references to the Managers responsible for managing this
       chassis.
    """

    contained_by = base.Field(
        "ContainedBy", adapter=rsd_lib_utils.get_resource_identity
    )
    """A reference to the chassis that this chassis is contained by."""

    contains = base.Field("Contains", adapter=utils.get_members_identities)
    """An array of references to any other chassis that this chassis has in it.
    """

    powered_by = base.Field("PoweredBy", adapter=utils.get_members_identities)
    """An array of ID[s] of resources that power this chassis. Normally the ID
       will be a chassis or a specific set of powerSupplies
    """

    cooled_by = base.Field("CooledBy", adapter=utils.get_members_identities)
    """An array of ID[s] of resources that cool this chassis. Normally the ID
       will be a chassis or a specific set of fans.
    """

    managers_in_chassis = base.Field(
        "ManagersInChassis", adapter=utils.get_members_identities
    )
    """An array of references to the managers located in this Chassis."""

    drives = base.Field("Drives", adapter=utils.get_members_identities)
    """An array of references to the disk drives located in this Chassis."""

    storage = base.Field("Storage", adapter=utils.get_members_identities)
    """An array of references to the storage subsystems connected to or inside
       this Chassis.
    """

    oem = LinksOemField("Oem")
    """Oem specific properties."""


class PhysicalSecurityField(base.CompositeField):

    intrusion_sensor_number = base.Field(
        "IntrusionSensorNumber", adapter=rsd_lib_utils.num_or_none
    )
    """A numerical identifier to represent the physical security sensor."""

    intrusion_sensor = base.Field("IntrusionSensor")
    """This indicates the known state of the physical security sensor, such as
       if it is hardware intrusion detected.
    """

    intrusion_sensor_re_arm = base.Field("IntrusionSensorReArm")
    """This indicates how the Normal state to be restored."""


class IntelRackScaleField(base.CompositeField):

    location = LocationField("Location")
    """Property that shows this chassis ID and its parent"""

    rmm_present = base.Field("RMMPresent", adapter=bool)
    """RMM presence in a rack"""

    rack_supports_disaggregated_power_cooling = base.Field(
        "RackSupportsDisaggregatedPowerCooling", adapter=bool
    )
    """Indicates if Rack support is disaggregated (shared) power and cooling
       capabilities
    """

    uuid = base.Field("UUID")
    """Chassis unique ID"""

    geo_tag = base.Field("GeoTag")
    """Provides info about the geographical location of this chassis"""


class OemField(base.CompositeField):

    intel_rackscale = IntelRackScaleField("Intel_RackScale")
    """Intel Rack Scale Design specific properties."""


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

    physical_security = PhysicalSecurityField("PhysicalSecurity")
    """The state of the physical security sensor."""

    location = rsd_lib_base.LocationField("Location")

    oem = OemField("Oem")
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
    def thermal_zones(self):
        """Property to provide reference to `ThermalZoneCollection` instance

           It is calculated once when it is queried for the first time. On
           refresh, this property is reset.
        """
        return thermal_zone.ThermalZoneCollection(
            self._conn,
            utils.get_sub_resource_path_by(self, "ThermalZones"),
            redfish_version=self.redfish_version,
        )

    @property
    @utils.cache_it
    def power_zones(self):
        """Property to provide reference to `PowerZoneCollection` instance

           It is calculated once when it is queried for the first time. On
           refresh, this property is reset.
        """
        return power_zone.PowerZoneCollection(
            self._conn,
            utils.get_sub_resource_path_by(self, "PowerZones"),
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
