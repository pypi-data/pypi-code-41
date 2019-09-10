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


class VirtualMedia(rsd_lib_base.ResourceBase):
    """VirtualMedia resource class

       This resource allows monitoring and control of an instance of virtual
       media (e.g. a remote CD, DVD, or USB device) functionality provided by
       a Manager for a system or device.
    """

    image_name = base.Field("ImageName")
    """The current image name"""

    image = base.Field("Image")
    """A URI providing the location of the selected image"""

    media_types = base.Field("MediaTypes")
    """This is the media types supported as virtual media."""

    connected_via = base.Field("ConnectedVia")
    """Current virtual media connection methods"""

    inserted = base.Field("Inserted", adapter=bool)
    """Indicates if virtual media is inserted in the virtual device."""

    write_protected = base.Field("WriteProtected", adapter=bool)
    """Indicates the media is write protected."""


class VirtualMediaCollection(rsd_lib_base.ResourceCollectionBase):
    @property
    def _resource_type(self):
        return VirtualMedia
