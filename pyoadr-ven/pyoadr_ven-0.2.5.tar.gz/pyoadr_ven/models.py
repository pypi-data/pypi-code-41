# -*- coding: utf-8 -*- {{{
# vim: set fenc=utf-8 ft=python sw=4 ts=4 sts=4 et:
#
# Copyright 2017, Battelle Memorial Institute.
#
# Licensed under the Apache License, Version 2.0 (the "License");
# you may not use this file except in compliance with the License.
# You may obtain a copy of the License at
#
# http://www.apache.org/licenses/LICENSE-2.0
#
# Unless required by applicable law or agreed to in writing, software
# distributed under the License is distributed on an "AS IS" BASIS,
# WITHOUT WARRANTIES OR CONDITIONS OF ANY KIND, either express or implied.
# See the License for the specific language governing permissions and
# limitations under the License.
#
# This material was prepared as an account of work sponsored by an agency of
# the United States Government. Neither the United States Government nor the
# United States Department of Energy, nor Battelle, nor any of their
# employees, nor any jurisdiction or organization that has cooperated in the
# development of these materials, makes any warranty, express or
# implied, or assumes any legal liability or responsibility for the accuracy,
# completeness, or usefulness or any information, apparatus, product,
# software, or process disclosed, or represents that its use would not infringe
# privately owned rights. Reference herein to any specific commercial product,
# process, or service by trade name, trademark, manufacturer, or otherwise
# does not necessarily constitute or imply its endorsement, recommendation, or
# favoring by the United States Government or any agency thereof, or
# Battelle Memorial Institute. The views and opinions of authors expressed
# herein do not necessarily state or reflect those of the
# United States Government or any agency thereof.
#
# PACIFIC NORTHWEST NATIONAL LABORATORY operated by
# BATTELLE for the UNITED STATES DEPARTMENT OF ENERGY
# under Contract DE-AC05-76RL01830
# }}}
from datetime import datetime as dt
from typing import Type

from dateutil import parser

from .utils import format_timestamp
from .utils import get_aware_utc_now


# class EiEvent:
#     """
#         Model object for an event.

#         Note that the timestamps are stored as ISO8601 strings, by SQLite convention.
#         Timezone awareness is retained when they are persisted.
#         They're stored as strings -- iso_start_time, etc. -- but agent code uses property
#         methods -- start_time(), etc. -- to get and set them as datetime objects.
#     """

#     __tablename__ = "EiEvent"

#     STATUS_UNRESPONDED = u"unresponded"
#     STATUS_FAR = u"far"
#     STATUS_NEAR = u"near"
#     STATUS_ACTIVE = u"active"
#     STATUS_COMPLETED = u"completed"
#     STATUS_CANCELED = u"cancelled"
#     STATUS_VALUES = [
#         STATUS_UNRESPONDED,
#         STATUS_FAR,
#         STATUS_NEAR,
#         STATUS_ACTIVE,
#         STATUS_COMPLETED,
#         STATUS_CANCELED,
#     ]

#     OPT_TYPE_OPT_IN = u"optIn"
#     OPT_TYPE_OPT_OUT = u"optOut"
#     OPT_TYPE_NONE = u"none"

#     __slots__ = (
#         "iso_start_time",
#         "iso_end_time",
#         "iso_dtstart",
#         "duration",
#         "start_after",
#         "request_id",
#         "creation_time",
#         "event_id",
#         "signals",
#         "status",
#         "opt_type",
#         "priority",
#         "modification_number",
#         "test_event",
#     )

#     def __init__(self, request_id: str, event_id: str):

#         self.iso_start_time: str = ""  # ISO 8601 timestamp in UTC
#         self.iso_end_time: str = ""  # ISO 8601 timestamp in UTC
#         self.iso_dtstart: str = ""  # ISO 8601 timestamp in UTC
#         self.duration: str = ""  # ISO 8601 duration string
#         self.start_after: str = ""

#         self.request_id: str = request_id
#         self.creation_time: Type(dt) = get_aware_utc_now()
#         self.event_id: str = event_id
#         self.signals: str = ""
#         self.status: str = self.STATUS_UNRESPONDED
#         self.opt_type: str = self.OPT_TYPE_NONE
#         self.priority: int = 1
#         self.modification_number: int = 0  # Incremented by the VTN if/when the event changes
#         self.test_event: str = "false"

#     def __str__(self):
#         """Format the instance as a string suitable for trace display."""
#         my_str = "{}: ".format(self.__class__.__name__)
#         my_str += "event_id:{}; ".format(self.event_id)
#         my_str += "start_time:{}; ".format(self.start_time)
#         my_str += "end_time:{}; ".format(self.end_time)
#         my_str += "opt_type:{}; ".format(self.opt_type)
#         my_str += "event_id:{}; ".format(self.event_id)
#         my_str += "status:{}; ".format(self.status)
#         my_str += "priority:{}; ".format(self.priority)
#         my_str += "modification_number:{}; ".format(self.modification_number)
#         my_str += "signals:{}; ".format(self.signals)
#         return my_str

#     @property
#     def start_time(self):
#         return parser.parse(self.iso_start_time) if self.iso_start_time else None

#     @property
#     def end_time(self):
#         return parser.parse(self.iso_end_time) if self.iso_end_time else None

#     @property
#     def dtstart(self):
#         return parser.parse(self.iso_dtstart) if self.iso_dtstart else None

#     @start_time.setter
#     def start_time(self, t):
#         self.iso_start_time = format_timestamp(t) if t else None

#     @end_time.setter
#     def end_time(self, t):
#         self.iso_end_time = format_timestamp(t) if t else None

#     @dtstart.setter
#     def dtstart(self, t):
#         self.iso_dtstart = format_timestamp(t) if t else None

#     def is_active_or_pending(self):
#         return self.status not in [self.STATUS_COMPLETED, self.STATUS_CANCELED]

#     def old_is_active(self):
#         return self.status not in [self.STATUS_COMPLETED, self.STATUS_CANCELED]

#     def as_json_compatible_object(self):
#         """Format the object as JSON that will be returned in response to an RPC, or sent in a pub/sub."""
#         return {attname: getattr(self, attname) for attname in self.__slots__}

#     def copy_from_event(self, another_event):
#         # Do not copy creation_time from another_event
#         self.event_id = another_event.event_id
#         self.request_id = another_event.request_id
#         self.start_time = another_event.start_time
#         self.end_time = another_event.end_time
#         self.priority = another_event.priority
#         self.signals = another_event.signals
#         # Do not copy status from another_event
#         # Do not copy opt_type from another_event
#         self.modification_number = another_event.modification_number
#         self.test_event = another_event.test_event
#         self.dtstart = another_event.dtstart
#         self.duration = another_event.duration
#         self.start_after = another_event.start_after


class EiReport:
    """Model object for a report."""

    __tablename__ = "EiReport"

    STATUS_INACTIVE = u"inactive"
    STATUS_ACTIVE = u"active"
    STATUS_COMPLETED = u"completed"
    STATUS_CANCELED = u"cancelled"

    __slots__ = (
        "iso_start_time",
        "iso_end_time",
        "duration",
        "iso_last_report",
        "name",
        "interval_secs",
        "granularity_secs",
        "telemetry_parameters",
        "created_on",
        "request_id",
        "report_request_id",
        "report_specifier_id",
        "status",
    )

    def __init__(self, request_id, report_request_id, report_specifier_id):

        self.iso_start_time: str = ""  # ISO 8601 timestamp in UTC
        self.iso_end_time: str = ""  # ISO 8601 timestamp in UTC
        self.duration: str = ""  # ISO 8601 duration
        self.iso_last_report: str = ""  # ISO 8601 timestamp in UTC
        self.name: str = ""
        self.interval_secs: int = 0
        self.granularity_secs: str = ""
        self.telemetry_parameters: str = ""
        self.created_on: Type(dt) = get_aware_utc_now()
        self.request_id: str = request_id
        self.report_request_id: str = report_request_id
        self.report_specifier_id: str = report_specifier_id
        self.status: str = "inactive"
        self.last_report: Type(dt) = get_aware_utc_now()

    def __str__(self):
        """Format the instance as a string suitable for trace display."""
        my_str = "{}: ".format(self.__class__.__name__)
        my_str += "report_request_id:{}; ".format(self.report_request_id)
        my_str += "report_specifier_id:{}; ".format(self.report_specifier_id)
        my_str += "start_time:{}; ".format(self.start_time)
        my_str += "end_time:{}; ".format(self.end_time)
        my_str += "status:{}; ".format(self.status)
        return my_str

    @property
    def start_time(self):
        return parser.parse(self.iso_start_time) if self.iso_start_time else None

    @property
    def end_time(self):
        return parser.parse(self.iso_end_time) if self.iso_end_time else None

    @property
    def last_report(self):
        return parser.parse(self.iso_last_report) if self.iso_last_report else None

    @start_time.setter
    def start_time(self, t):
        self.iso_start_time = format_timestamp(t) if t else None

    @end_time.setter
    def end_time(self, t):
        self.iso_end_time = format_timestamp(t) if t else None

    @last_report.setter
    def last_report(self, t):
        self.iso_last_report = format_timestamp(t) if t else None

    def is_active_or_pending(self):
        return self.status not in [self.STATUS_COMPLETED, self.STATUS_CANCELED]

    def as_json_compatible_object(self):
        """Format the object as JSON that will be returned in response to an RPC, or sent in a pub/sub."""
        return {attname: getattr(self, attname) for attname in self.__slots__}

    def copy_from_report(self, another_report):
        """(Selectively) Copy the contents of another_report to this one."""
        self.request_id = another_report.request_id
        self.report_request_id = another_report.report_request_id
        self.report_specifier_id = another_report.report_specifier_id
        self.start_time = another_report.start_time
        self.end_time = another_report.end_time
        self.duration = another_report.duration
        self.granularity_secs = another_report.granularity_secs
        # Do not copy created_on from another_report
        # Do not copy status from another_report
        # Do not copy last_report from another_report
        self.name = another_report.name
        self.interval_secs = another_report.interval_secs
        self.telemetry_parameters = another_report.telemetry_parameters


class EiTelemetryValues:
    """Model object for telemetry values."""

    __tablename__ = "EiTelemetryValues"

    __slots__ = (
        "created_on",
        "report_request_id",
        "baseline_power_kw",
        "current_power_kw",
    )

    def __init__(
        self,
        report_request_id=None,
        baseline_power_kw=None,
        current_power_kw=None,
        start_time=None,
        end_time=None,
    ):

        self.created_on: Type(dt) = get_aware_utc_now()
        self.report_request_id: str = report_request_id
        self.baseline_power_kw: float = baseline_power_kw
        self.current_power_kw: float = current_power_kw
        self.start_time: str = start_time
        self.end_time: str = end_time

    def __str__(self):
        """Format the instance as a string suitable for trace display."""
        my_str = "{}: ".format(self.__class__.__name__)
        my_str += "created_on:{}; ".format(self.created_on)
        my_str += "report_request_id:{}; ".format(self.report_request_id)
        my_str += "baseline_power_kw:{}; ".format(self.baseline_power_kw)
        my_str += "current_power_kw:{} ".format(self.current_power_kw)
        my_str += "start_time:{} ".format(self.start_time)
        my_str += "end_time:{} ".format(self.end_time)
        return my_str

    @property
    def start_time(self):
        return parser.parse(self.iso_start_time) if self.iso_start_time else None

    @property
    def end_time(self):
        return parser.parse(self.iso_end_time) if self.iso_end_time else None

    @start_time.setter
    def start_time(self, t):
        self.iso_start_time = format_timestamp(t) if t else None

    @end_time.setter
    def end_time(self, t):
        self.iso_end_time = format_timestamp(t) if t else None

    @classmethod
    def sample_values(cls):
        """Return a sample set of telemetry values for debugging purposes."""
        telemetry_values = cls()
        telemetry_values.report_request_id = "123"
        telemetry_values.baseline_power_kw = 37.1
        telemetry_values.current_power_kw = 272.3
        return telemetry_values

    def as_json_compatible_object(self):
        """Format the object as JSON that will be returned in response to an RPC, or sent in a pub/sub."""
        return {attname: getattr(self, attname) for attname in self.attribute_names}

    def get_baseline_power(self):
        return self.baseline_power_kw

    def get_current_power(self):
        return self.current_power_kw

    def get_duration(self):
        return self.end_time - self.start_time
