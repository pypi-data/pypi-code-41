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

from sushy import exceptions
from sushy.resources import base
from sushy.resources import common
from sushy import utils

from rsd_lib import base as rsd_lib_base
from rsd_lib.resources.v2_1.system import volume
from rsd_lib import utils as rsd_lib_utils


class IntelRackScaleField(base.CompositeField):

    erase_on_detach = base.Field("EraseOnDetach", adapter=bool)
    """This indicates if drive should be erased when detached from PCI switch.
    """

    drive_erased = base.Field("DriveErased", adapter=bool)
    """This indicates whether drive was cleared after assignment to composed
       node.
    """

    firmware_version = base.Field("FirmwareVersion")
    """This indicates drive firmware version."""

    storage = base.Field(
        "Storage", adapter=rsd_lib_utils.get_resource_identity
    )
    """A reference to the storage controller where this drive is connected."""

    pcie_function = base.Field(
        "PCIeFunction", adapter=rsd_lib_utils.get_resource_identity
    )
    """A reference to the PCIe function that provides this drive functionality.
    """


class LinksField(base.CompositeField):

    volumes = base.Field("Volumes", adapter=utils.get_members_identities)
    """An array of references to the volumes contained in this drive. This
       will reference Volumes that are either wholly or only partly contained
       by this drive.
    """

    endpoints = base.Field("Endpoints", adapter=utils.get_members_identities)
    """An array of references to the endpoints that connect to this drive."""


class OemField(base.CompositeField):

    intel_rackscale = IntelRackScaleField("Intel_RackScale")
    """Intel Rack Scale Design specific properties."""


class ActionsField(base.CompositeField):
    secure_erase = common.ActionField("#Drive.SecureErase")


class Drive(rsd_lib_base.ResourceBase):
    """Drive resource class

       Drive contains properties describing a single physical disk drive for
       any system, along with links to associated Volumes.
    """

    status_indicator = base.Field("StatusIndicator")
    """The state of the status indicator, used to communicate status
       information about this drive.
    """

    indicator_led = base.Field("IndicatorLED")
    """The state of the indicator LED, used to identify the drive."""

    model = base.Field("Model")
    """This is the model number for the drive."""

    revision = base.Field("Revision")
    """The revision of this Drive"""

    status = rsd_lib_base.StatusField("Status")
    """This indicates the known state of the resource, such as if it is
       enabled.
    """

    capacity_bytes = base.Field(
        "CapacityBytes", adapter=rsd_lib_utils.num_or_none
    )
    """The size in bytes of this Drive"""

    failure_predicted = base.Field("FailurePredicted", adapter=bool)
    """Is this drive currently predicting a failure in the near future"""

    protocol = base.Field("Protocol")
    """The protocol this drive is using to communicate to the storage
       controller
    """

    media_type = base.Field("MediaType")
    """The type of media contained in this drive"""

    manufacturer = base.Field("Manufacturer")
    """This is the manufacturer of this drive."""

    sku = base.Field("SKU")
    """This is the SKU for this drive."""

    serial_number = base.Field("SerialNumber")
    """The serial number for this drive."""

    part_number = base.Field("PartNumber")
    """The part number for this drive."""

    asset_tag = base.Field("AssetTag")
    """The user assigned asset tag for this drive."""

    identifiers = rsd_lib_base.IdentifierCollectionField("Identifiers")
    """The Durable names for the drive"""

    location = rsd_lib_base.LocationCollectionField("Location")
    """The Location of the drive"""

    hotspare_type = base.Field("HotspareType")
    """The type of hotspare this drive is currently serving as"""

    encryption_ability = base.Field("EncryptionAbility")
    """The encryption abilities of this drive"""

    encryption_status = base.Field("EncryptionStatus")
    """The status of the encryption of this drive"""

    rotation_speed_rpm = base.Field(
        "RotationSpeedRPM", adapter=rsd_lib_utils.num_or_none
    )
    """The rotation speed of this Drive in Revolutions per Minute (RPM)"""

    block_size_bytes = base.Field(
        "BlockSizeBytes", adapter=rsd_lib_utils.num_or_none
    )
    """The size of the smallest addressible unit (Block) of this drive in bytes
    """

    capable_speed_gbs = base.Field(
        "CapableSpeedGbs", adapter=rsd_lib_utils.num_or_none
    )
    """The speed which this drive can communicate to a storage controller in
       ideal conditions in Gigabits per second
    """

    negotiated_speed_gbs = base.Field(
        "NegotiatedSpeedGbs", adapter=rsd_lib_utils.num_or_none
    )
    """The speed which this drive is currently communicating to the storage
       controller in Gigabits per second
    """

    predicted_media_life_left_percent = base.Field(
        "PredictedMediaLifeLeftPercent", adapter=rsd_lib_utils.num_or_none
    )
    """The percentage of reads and writes that are predicted to still be
       available for the media
    """

    links = LinksField("Links")
    """Contains references to other resources that are related to this
       resource.
    """

    operations = volume.OperationsCollectionField("Operations")
    """The operations currently running on the Drive."""

    oem = OemField("Oem")
    """Oem specific properties."""

    _actions = ActionsField("Actions")

    def _get_secure_erase_action_element(self):
        secure_erase_action = self._actions.secure_erase

        if not secure_erase_action:
            raise exceptions.MissingActionError(
                action="#Drive.SecureErase", resource=self._path
            )
        return secure_erase_action

    def secure_erase(self):
        """Secure erase the drive.

        :raises: MissingActionError, if no secure erase action exists.
        """
        target_uri = self._get_secure_erase_action_element().target_uri

        self._conn.post(target_uri, data={})

    def update(self, asset_tag=None, erase_on_detach=None, erased=None):
        """Update drive properties

        :param asset_tag: The user assigned asset tag for this drive
        :param erase_on_detach: Indicates if drive should be erased when
                                detached from Composed Node.
        :param erased: Indicate whether drive was cleared after assignment to
                       composed node
        :raises: InvalidParameterValueError if one param is incorrect
        """

        data = {}

        if asset_tag is not None:
            data["AssetTag"] = asset_tag

        if erase_on_detach is not None or erased is not None:
            data["Oem"] = {"Intel_RackScale": {}}

            if erase_on_detach is not None:
                if not isinstance(erase_on_detach, bool):
                    raise exceptions.InvalidParameterValueError(
                        parameter="erase_on_detach",
                        value=erase_on_detach,
                        valid_values=[True, False],
                    )
                else:
                    data["Oem"]["Intel_RackScale"][
                        "EraseOnDetach"
                    ] = erase_on_detach

            if erased is not None:
                if not isinstance(erased, bool):
                    raise exceptions.InvalidParameterValueError(
                        parameter="erased",
                        value=erased,
                        valid_values=[True, False],
                    )
                else:
                    data["Oem"]["Intel_RackScale"]["DriveErased"] = erased

        self._conn.patch(self.path, data=data)
