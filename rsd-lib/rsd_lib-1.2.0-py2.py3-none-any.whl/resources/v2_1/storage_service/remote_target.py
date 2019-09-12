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

from rsd_lib import base as rsd_lib_base
from rsd_lib import utils as rsd_lib_utils

LOG = logging.getLogger(__name__)


class iSCSIInitiatorField(base.CompositeField):

    initiator_iqn = base.Field("InitiatorIQN")
    """IQN of iSCSI target initiator"""


class ChapField(base.CompositeField):

    type = base.Field("Type")
    """CHAP parameters of iSCSI target."""

    username = base.Field("Username")
    """CHAP one way user name."""

    secret = base.Field("Secret")
    """CHAP one way secret."""

    mutual_username = base.Field("MutualUsername")
    """CHAP mutual user name."""

    mutual_secret = base.Field("MutualSecret")
    """CHAP mutual secret."""


class TargetLUNCollectionField(base.ListField):

    lun = base.Field("LUN", adapter=rsd_lib_utils.num_or_none)
    """Logical unit number"""

    logical_drive = base.Field(
        "LogicalDrive", adapter=rsd_lib_utils.get_resource_identity
    )
    """Logical drive URI"""


class ISCSIAddressField(base.CompositeField):

    target_lun = TargetLUNCollectionField("TargetLUN")
    """Target Logical Unit"""

    target_iqn = base.Field("TargetIQN")
    """Target IQN"""

    target_portal_ip = base.Field("TargetPortalIP")
    """iSCSI target portal IP address"""

    target_portal_port = base.Field(
        "TargetPortalPort", adapter=rsd_lib_utils.num_or_none
    )
    """iSCSI target port"""

    chap = ChapField("CHAP")
    """CHAP parameters of iSCSI target."""


class InitiatorCollectionField(base.ListField):

    iscsi = iSCSIInitiatorField("iSCSI")


class AddressCollectionField(base.ListField):

    iscsi = ISCSIAddressField("iSCSI")


class RemoteTarget(rsd_lib_base.ResourceBase):

    status = rsd_lib_base.StatusField("Status")
    """This indicates the known state of the resource, such as if it is
       enabled.
    """

    type = base.Field("Type")
    """Type of target"""

    addresses = AddressCollectionField("Addresses")

    initiator = InitiatorCollectionField("Initiator")


class RemoteTargetCollection(rsd_lib_base.ResourceCollectionBase):
    @property
    def _resource_type(self):
        return RemoteTarget
