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
import json
import logging
import random
from datetime import timedelta

import isodate

from . import enums
from . import exceptions
from . import response_codes

_LOGGER = logging.getLogger(__name__)


class OadrExtractor(object):
    """Extract oadr model objects received from the VTN as XML."""

    def __init__(self, request=None, **kwargs):
        self.request = request

    def extract_request_id(self):
        request_id = self.request.requestID
        if request_id is None:
            raise exceptions.OpenADRInterfaceException(
                "Missing requestID", response_codes.OADR_BAD_DATA
            )
        return request_id

    @staticmethod
    def extract_start_and_end_time(interval):
        """Extract a start_time and an end_time from a received interval."""
        try:
            start_time = interval.properties.dtstart.date_time
            assert start_time is not None
            assert start_time.tzinfo is not None
        except Exception as err:
            error_msg = "Missing/Invalid interval properties.dtstart.date_time: {} {}".format(
                start_time, err
            )
            raise exceptions.OpenADRInterfaceException(
                error_msg, response_codes.OADR_BAD_DATA
            )

        try:
            duration = interval.properties.duration.duration
            parsed_duration = isodate.parse_duration(duration)
        except Exception as err:
            error_msg = "Missing/Invalid interval properties.duration.duration: {} {}".format(
                duration, err
            )
            raise exceptions.OpenADRInterfaceException(
                error_msg, response_codes.OADR_BAD_DATA
            )

        # An interval with 0 duration has no defined endTime and remains active until canceled.
        end_time = (
            None
            if parsed_duration.total_seconds() == 0.0
            else start_time + parsed_duration
        )
        return start_time, end_time


class OadrResponseExtractor(OadrExtractor):
    def __init__(self, ei_response=None, **kwargs):
        super(OadrResponseExtractor, self).__init__(**kwargs)
        self.ei_response = ei_response

    def extract(self):
        """An eiResponse can appear in multiple kinds of VTN requests. Extract its code and description."""
        return self.ei_response.responseCode, self.ei_response.responseDescription


class OadrEventExtractor(OadrExtractor):
    """Extract an event's properties from oadr model objects received from the VTN as XML."""

    def __init__(self, ei_event=None, **kwargs):
        super(OadrEventExtractor, self).__init__(**kwargs)
        self.ei_event = ei_event

    @property
    def event_id(self) -> int:
        event_descriptor = self.ei_event.eventDescriptor
        if event_descriptor is None:
            raise exceptions.OpenADRInterfaceException(
                "Missing eiEvent.eventDescriptor", response_codes.OADR_BAD_DATA
            )
        event_id = event_descriptor.eventID
        if event_id is None:
            raise exceptions.OpenADRInterfaceException(
                "Missing eiEvent.eventDescriptor.eventID", response_codes.OADR_BAD_DATA
            )
        return int(event_id)

    @property
    def event_status(self) -> enums.EventStatus:
        """ OADR rule 13: Status value must be a valid type,
            appropriate for the event's period.
        """
        event_descriptor = self.ei_event.eventDescriptor
        event_status = event_descriptor.eventStatus
        if event_status not in enums.EventStatus.list():
            raise exceptions.OpenADRInterfaceException(
                "Missing or invalid eventDescriptor.eventStatus",
                response_codes.OADR_BAD_DATA,
            )
        return enums.EventStatus(event_status)

    @property
    def event_modifcation_number(self):
        event_descriptor = self.ei_event.eventDescriptor
        modification_number = event_descriptor.modificationNumber
        if modification_number is None:
            raise exceptions.OpenADRInterfaceException(
                "Missing eventDescriptor.modificationNumber",
                response_codes.OADR_BAD_DATA,
            )
        return modification_number

    @property
    def event_modification_reason(self):
        return self.ei_event.eventDescriptor.modificationReason

    @property
    def event_priority(self):
        event_descriptor = self.ei_event.eventDescriptor
        if event_descriptor.priority:
            return event_descriptor.priority

    @property
    def market_context(self):
        return self.ei_event.eventDescriptor.eiMarketContext

    @property
    def created_datetime(self):
        return self.ei_event.eventDescriptor.createdDateTime

    @property
    def test_flag(self) -> bool:
        return bool(self.ei_event.eventDescriptor.testEvent)

    @property
    def vtn_comment(self) -> str:
        return self.ei_event.eventDescriptor.vtnComment

    @property
    def _active_period(self):
        active_period = self.ei_event.eiActivePeriod
        if active_period is None:
            raise exceptions.OpenADRInterfaceException(
                "Missing eiEvent.eiActivePeriod", response_codes.OADR_BAD_DATA
            )
        return active_period

    @property
    def _active_period_properties(self):
        properties = self._active_period.properties
        if properties is None:
            raise exceptions.OpenADRInterfaceException(
                "Missing eiEvent.eiActivePeriod.properties",
                response_codes.OADR_BAD_DATA,
            )
        return properties

    @property
    def event_dtstart(self):
        try:
            dtstart = self._active_period_properties.dtstart.date_time
            assert dtstart is not None
            assert dtstart.tzinfo is not None
        except Exception as err:
            error_msg = f"Missing/Invalid properties.dtstart.date_time: {dtstart} {err}"
            raise exceptions.OpenADRInterfaceException(
                error_msg, response_codes.OADR_BAD_DATA
            )
        return dtstart.replace(tzinfo=None)

    @property
    def event_duration(self) -> timedelta:
        try:
            duration = self._active_period_properties.duration.duration
        except Exception as err:
            error_msg = "Missing/Invalid properties.duration.duration: {} {}".format(
                self._active_period_properties.duration.duration, err
            )
            raise exceptions.OpenADRInterfaceException(
                error_msg, response_codes.OADR_BAD_DATA
            )
        return isodate.parse_duration(duration)

    @property
    def event_start_after(self):
        if not self._active_period_properties.tolerance:
            return None
        if not self._active_period_properties.tolerance.tolerate:
            return None
        return self._active_period_properties.tolerance.tolerate.startafter

    @property
    def event_start_time(self):
        if self.event_start_after:
            try:
                max_offset = isodate.parse_duration(self.event.start_after)
                # OADR rule 30: Randomize start_time and end_time if start_after is provided.
                start_time = self.event_dtstart + timedelta(
                    seconds=(max_offset.seconds * random.random())
                )
            except Exception as err:
                error_msg = "Invalid activePeriod tolerance.tolerate.startafter: {}".format(
                    err
                )
                raise exceptions.OpenADRInterfaceException(
                    error_msg, response_codes.OADR_BAD_DATA
                )
        else:
            start_time = self.event_dtstart

        return start_time.replace(tzinfo=None)

    @property
    def event_end_time(self):
        """
        An interval with 0 duration has no defined endTime
        and remains active until canceled.
        """
        if self.event_duration.total_seconds() <= 0.0:
            return None

        end_time = self.event_start_time + self.event_duration
        return end_time.replace(tzinfo=None)

    @property
    def notification_duration(self):
        notification = self._active_period_properties.x_eiNotification
        if notification is None:
            # OADR rule 105: eiNotification is required as an element of activePeriod.
            raise exceptions.OpenADRInterfaceException(
                "Missing eiActivePeriod.properties.eiNotification",
                response_codes.OADR_BAD_DATA,
            )
        return notification.duration

    @property
    def ramp_up_duration(self):
        return self._active_period_properties.x_eiRampUp.duration

    @property
    def recovery_duration(self):
        return self._active_period_properties.x_eiRecovery.duration

    @property
    def signals(self) -> str:
        """ Extract eiEventSignals from the received eiEvent
            @return A json string of signals
        """
        if not self.ei_event.eiEventSignals:
            raise exceptions.OpenADRInterfaceException(
                "At least one event signal is required.", response_codes.OADR_BAD_SIGNAL
            )
        if not self.ei_event.eiEventSignals.eiEventSignal:
            raise exceptions.OpenADRInterfaceException(
                "At least one event signal is required.", response_codes.OADR_BAD_SIGNAL
            )
        signals_dict = {
            s.signalID: self.extract_signal(s)
            for s in self.ei_event.eiEventSignals.eiEventSignal
        }
        assert self._signals_duration_equals_event_duration()
        return json.dumps(signals_dict)

    def _signals_duration_equals_event_duration(self) -> bool:
        """Sum of all signal interval durations must equal the event duration."""
        signals_duration = timedelta(seconds=0)
        for signal in self.ei_event.eiEventSignals.eiEventSignal:
            for interval in signal.intervals.interval:
                signals_duration += isodate.parse_duration(interval.duration.duration)
        if signals_duration == self.event_duration:
            return True
        else:
            err_msg = "Total signal interval durations {} != event duration {}".format(
                signals_duration, self.event_duration
            )
            raise exceptions.OpenADRException(err_msg, response_codes.OADR_BAD_SIGNAL)
            return False

    @staticmethod
    def extract_signal(signal):
        """Extract a signal from the received eiEvent."""
        if signal.signalName.lower() != "simple":
            raise exceptions.OpenADRInterfaceException(
                "Received a non-simple event signal; not supported by this VEN.",
                response_codes.OADR_BAD_SIGNAL,
            )
        if signal.signalType.lower() != "level":
            # OADR rule 116: If signalName = simple, signalType = level.
            # Disabling this validation since the EPRI VTN server sometimes sends type "delta" for simple signals.
            # error_msg = 'Simple signalType must be level; = {}'.format(signal.signalType)
            # raise exceptions.OpenADRInterfaceException(error_msg, response_codes.OADR_BAD_SIGNAL)
            pass
        return {
            "signalID": signal.signalID,
            "currentLevel": int(signal.currentValue.payloadFloat.value)
            if signal.currentValue
            else None,
            "intervals": {
                interval.uid
                if interval.uid and interval.uid.strip()
                else str(i): {
                    "uid": interval.uid
                    if interval.uid and interval.uid.strip()
                    else str(i),
                    "duration": interval.duration.duration,
                    "payloads": {
                        "level": int(payload.payloadBase.value)
                        for payload in interval.streamPayloadBase
                    },
                }
                for i, interval in enumerate(signal.intervals.interval)
            },
        }


class OadrReportExtractor(OadrExtractor):
    """Extract a report's properties from oadr model objects received from the VTN as XML."""

    def __init__(self, report=None, report_parameters=None, **kwargs):
        super(OadrReportExtractor, self).__init__(**kwargs)
        self.report = report
        self.report_parameters = report_parameters

    def extract_report_request_id(self):
        """Extract and return the report's reportRequestID."""
        report_request_id = self.request.reportRequestID
        if report_request_id is None:
            raise exceptions.OpenADRInterfaceException(
                "Missing oadrReportRequest.reportRequestID",
                response_codes.OADR_BAD_DATA,
            )
        return report_request_id

    def extract_specifier_id(self):
        """Extract and return the report's reportSpecifierID."""
        report_specifier = self.request.reportSpecifier
        if report_specifier is None:
            raise exceptions.OpenADRInterfaceException(
                "Missing oadrReportRequest.reportSpecifier",
                response_codes.OADR_BAD_DATA,
            )
        report_specifier_id = report_specifier.reportSpecifierID
        if report_specifier_id is None:
            error_msg = "Missing oadrReportRequest.reportSpecifier.reportSpecifierID"
            raise exceptions.OpenADRInterfaceException(
                error_msg, response_codes.OADR_BAD_DATA
            )
        return report_specifier_id

    def extract_report(self):
        """Validate various received report fields and add them to the report instance."""
        report_specifier = self.request.reportSpecifier
        report_interval = report_specifier.reportInterval
        if report_interval is None:
            raise exceptions.OpenADRInterfaceException(
                "Missing reportInterval", response_codes.OADR_BAD_DATA
            )

        try:
            start_time = report_interval.properties.dtstart.date_time
            assert start_time is not None
            assert start_time.tzinfo is not None
        except Exception as err:
            error_msg = "Missing/Invalid interval properties.dtstart.date_time: {} {}".format(
                start_time, err
            )
            raise exceptions.OpenADRInterfaceException(
                error_msg, response_codes.OADR_BAD_DATA
            )

        try:
            duration = report_interval.properties.duration.duration
            end_time = start_time + isodate.parse_duration(duration)
        except Exception as err:
            # To accommodate the Kisensum VTN server, a report interval with a missing/null duration
            # has a special meaning to the VEN: the report request continues indefinitely,
            # with no scheduled completion time.
            _LOGGER.debug(
                "Missing/null report interval duration: the report will remain active indefinitely: %s",
                err,
            )
            duration = None
            end_time = None

        self.report.start_time = start_time
        self.report.end_time = end_time
        self.report.duration = duration

        self.report.name = self.report_parameters.get("report_name", None)
        self.report.telemetry_parameters = json.dumps(
            self.report_parameters.get("telemetry_parameters", None)
        )

        default = self.report_parameters.get("report_interval_secs_default")
        iso_duration = report_specifier.reportBackDuration
        if iso_duration is not None:
            try:
                self.report.interval_secs = int(
                    isodate.parse_duration(iso_duration.duration).total_seconds()
                )
            except Exception as err:
                error_msg = "reportBackDuration {} has unparsable duration: {}".format(
                    iso_duration, err
                )
                raise exceptions.OpenADRInterfaceException(
                    error_msg, response_codes.OADR_BAD_DATA
                )
        elif default is not None:
            try:
                self.report.interval_secs = int(default)
            except ValueError:
                error_msg = "Default report interval {} is not an integer number of seconds".format(
                    default
                )
                raise exceptions.OpenADRInterfaceException(
                    error_msg, response_codes.OADR_BAD_DATA
                )
        else:
            self.report.interval_secs = None

        if report_specifier.granularity:
            try:
                granularity = isodate.parse_duration(
                    report_specifier.granularity.duration
                )
                self.report.granularity_secs = int(granularity.total_seconds())
            except Exception:
                error_msg = (
                    "Report granularity is missing or is not an ISO8601 duration"
                )
                raise exceptions.OpenADRInterfaceException(
                    error_msg, response_codes.OADR_BAD_DATA
                )


class OadrRegistrationExtractor(OadrExtractor):
    def __init__(self, **kwargs):
        super(OadrRegistrationExtractor, self).__init__(**kwargs)


class OadrCreatedPartyRegistrationExtractor(OadrRegistrationExtractor):
    def __init__(self, registration=None, **kwargs):
        super(OadrCreatedPartyRegistrationExtractor, self).__init__(**kwargs)
        self.registration = registration

    def extract_ven_id(self):
        return self.registration.venID

    def extract_poll_freq(self):
        return self.registration.oadrRequestedOadrPollFreq

    def extract_vtn_id(self):
        return self.registration.vtnID
