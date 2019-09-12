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


class LocationCollectionField(base.ListField):

    language = base.Field("Language")
    """The language code for the file the schema is in."""

    uri = base.Field("Uri")
    """Link to locally available URI for schema."""

    archive_uri = base.Field("ArchiveUri")
    """If the schema is hosted on the service in an archive file, this is the
       link to the archive file.
    """

    publication_uri = base.Field("PublicationUri")
    """Link to publicly available (canonical) URI for schema."""

    archive_file = base.Field("ArchiveFile")
    """If the schema is hosted on the service in an archive file, this is the
       name of the file within the archive.
    """


class MessageRegistryFile(rsd_lib_base.ResourceBase):
    """MessageRegistryFile resource class

       This is the schema definition for the Schema File locator resource.
    """

    languages = base.Field("Languages")
    """Language codes for the schemas available."""

    registry = base.Field("Registry")
    """The Registry Name, Major and Minor version used in MessageID
       construction.
    """

    location = LocationCollectionField("Location")
    """Location information for this schema file."""


class MessageRegistryFileCollection(rsd_lib_base.ResourceCollectionBase):
    @property
    def _resource_type(self):
        return MessageRegistryFile
