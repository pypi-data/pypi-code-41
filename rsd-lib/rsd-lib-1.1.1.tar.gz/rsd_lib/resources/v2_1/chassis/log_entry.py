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


class LinksField(base.CompositeField):

    origin_of_condition = base.Field(
        "OriginOfCondition", adapter=rsd_lib_utils.get_resource_identity
    )
    """This is the URI of the resource that caused the log entry"""


class LogEntry(rsd_lib_base.ResourceBase):
    """LogEntry resource class

       This resource defines the record format for a log.  It is designed to
       be used for SEL logs (from IPMI) as well as Event Logs and OEM-specific
       log formats.  The EntryType field indicates the type of log and the
       resource includes several additional properties dependent on the
       EntryType.
    """

    severity = base.Field("Severity")
    """This is the severity of the log entry."""

    created = base.Field("Created")
    """The time the log entry was created."""

    entry_type = base.Field("EntryType")
    """his is the type of log entry."""

    oem_record_format = base.Field("OemRecordFormat")
    """If the entry type is Oem, this will contain more information about the
       record format from the Oem.
    """

    entry_code = base.Field("EntryCode")
    """If the EntryType is SEL, this will have the entry code for the log
       entry.
    """

    sensor_type = base.Field("SensorType")
    """If the EntryType is SEL, this will have the sensor type that the log
       entry pertains to.
    """

    sensor_number = base.Field(
        "SensorNumber", adapter=rsd_lib_utils.num_or_none
    )
    """This property decodes from EntryType:  If it is SEL, it is the sensor
       number; if Event then the count of events.  Otherwise, it is Oem
       specific.
    """

    message = base.Field("Message")
    """This property decodes from EntryType:  If it is Event then it is a
       message string.  Otherwise, it is SEL or Oem specific.  In most cases,
       this will be the actual Log Entry.
    """

    message_id = base.Field("MessageId")
    """This property decodes from EntryType:  If it is Event then it is a
       message id.  Otherwise, it is SEL or Oem specific.  This value is only
       used for registries - for more information, see the specification.
    """

    message_args = base.Field("MessageArgs")
    """The values of this property shall be any arguments for the message."""

    links = LinksField("Links")
    """Contains references to other resources that are related to this
       resource.
    """

    event_type = base.Field("EventType")
    """This indicates the type of an event recorded in this log."""

    event_id = base.Field("EventId")
    """This is a unique instance identifier of an event."""

    event_timestamp = base.Field("EventTimestamp")
    """This is time the event occurred."""


class LogEntryCollection(rsd_lib_base.ResourceCollectionBase):
    @property
    def _resource_type(self):
        return LogEntry
