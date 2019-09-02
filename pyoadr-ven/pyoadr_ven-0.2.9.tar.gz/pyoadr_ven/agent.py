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
import sys
from collections import namedtuple
from datetime import datetime
from datetime import timedelta
from io import StringIO
from typing import Any
from typing import Dict
from typing import Iterable
from typing import List
from typing import Optional
from typing import Tuple

import isodate
import lxml.etree as etree_
import pem
import requests
import signxml
from pony import orm
from requests.exceptions import ConnectionError

from . import builders
from . import database
from . import enums
from . import exceptions
from . import extractors
from . import models
from . import oadr_20b
from . import response_codes
from .utils import get_aware_utc_now

_LOGGER = logging.getLogger(__name__)

ENDPOINT_BASE = "/OpenADR2/Simple/2.0b/"
EIEVENT = ENDPOINT_BASE + "EiEvent"
EIREPORT = ENDPOINT_BASE + "EiReport"
EIREGISTERPARTY = ENDPOINT_BASE + "EiRegisterParty"
POLL = ENDPOINT_BASE + "OadrPoll"

Endpoint = namedtuple("Endpoint", ["url", "callback"])
OPENADR_ENDPOINTS = {
    "EiEvent": Endpoint(url=EIEVENT, callback="push_request"),
    "EiReport": Endpoint(url=EIREPORT, callback="push_request"),
    "EiRegisterParty": Endpoint(url=EIREGISTERPARTY, callback="push_request"),
}

VTN_REQUESTS = {
    "oadrDistributeEvent": "handle_oadr_distribute_event",
    "oadrRegisterReport": "handle_oadr_register_report",
    "oadrRegisteredReport": "handle_oadr_registered_report",
    "oadrCreateReport": "handle_oadr_create_report",
    "oadrUpdatedReport": "handle_oadr_updated_report",
    "oadrCancelReport": "handle_oadr_cancel_report",
    "oadrResponse": "handle_oadr_response",
    "oadrCreatedPartyRegistration": "handle_oadr_created_party_registration",
}

PROCESS_LOOP_FREQUENCY_SECS = 5
DEFAULT_REPORT_INTERVAL_SECS = 15
# If no optIn timeout was configured, use 30 minutes.
DEFAULT_OPT_TIMEOUT_SECS = 30 * 60


class OpenADRVenAgent:
    """
        OpenADR (Automated Demand Response) is a standard for alerting and responding
        to the need to adjust electric power consumption in response to fluctuations
        in grid demand.

        OpenADR communications are conducted between Virtual Top Nodes (VTNs) and Virtual End Nodes (VENs).
        In this implementation, a this agent is a VEN, implementing EiEvent and EiReport services
        in conformance with a subset of the OpenADR 2.0b specification.

        The VEN receives VTN requests via the web service.

        The VTN can 'call an event', indicating that a load-shed event should occur.
        The VEN responds with an 'optIn' acknowledgment.

        Events:
            The VEN agent maintains a persistent record of DR events.
            These events are stored in a sqlite database

        Reporting:
            The VEN agent configuration defines telemetry values (data points) to be reported to the VTN.
            The VEN agent maintains a persistent record of reportable/reported telemetry values over time.

        Supported requests/responses in the OpenADR VTN interface:
            VTN:
                oadrDistributeEvent (needed for event cancellation)
                oadrResponse
                oadrRegisteredReport
                oadrCreateReport
                oadrUpdatedReport
                oadrCancelReport
                oadrCreatedPartyRegistration
            VEN:
                oadrPoll
                oadrRequestEvent
                oadrCreatedEvent
                oadrResponse
                oadrRegisterReport
                oadrCreatedReport
                oadrUpdateReport
                oadrCanceledReport
                oadrCreatePartyRegistration
                oadrQueryRegistration
    """

    EiReports: List[models.EiReport] = []
    EiTelemetryValuess: List[models.EiTelemetryValues] = []

    _last_poll: Optional[datetime] = None
    _active_reports: Dict[int, models.EiReport] = {}

    oadr_current_service: Optional[str] = None
    oadr_current_request_id: Optional[str] = None

    def __init__(
        self,
        ven_id: str,
        vtn_id: str,
        vtn_address: str,
        client_pem_bundle,
        vtn_ca_cert,
        opt_default_decision,
        report_parameters={},
        ven_name="",
        opt_timeout_secs: int = DEFAULT_OPT_TIMEOUT_SECS,
        poll_interval_secs: int = 15,
        send_registration: bool = False,
        request_events_on_startup: bool = True,
        security_level="standard",
        log_xml: bool = False,
        db_filepath: str = None,
        **kwargs,
    ):

        self.default_config = {
            "ven_id": ven_id,
            "vtn_id": vtn_id,
            "vtn_address": vtn_address,
            "poll_interval_secs": poll_interval_secs,
            "opt_timeout_secs": opt_timeout_secs,
            "request_events_on_startup": request_events_on_startup,
            "client_pem_bundle": client_pem_bundle,
            "vtn_ca_cert": vtn_ca_cert,
            "report_parameters": report_parameters,
            "ven_name": ven_name,
            "send_registration": send_registration,
            "security_level": security_level,
            "log_xml": log_xml,
            "opt_default_decision": opt_default_decision,
        }
        self.initialize_config(self.default_config)
        if "pytest" not in sys.modules:
            database.setup_db(db_filepath)

        # State variables for VTN request/response processing
        self.ven_online = "false"
        self.ven_manual_override = "false"

    def initialize_config(self, config):
        """
            Initialize the agent's configuration.

            Configuration parameters (see openadrven.config for a sample config file):

                ven_id:                 (string) OpenADR ID of this virtual end node. Identifies this VEN to the VTN.
                ven_name:               Name of this virtual end node. Identifies this VEN during registration,
                                        before its ID is known.
                vtn_id:                 (string) OpenADR ID of the VTN with which this VEN communicates.
                vtn_address:            URL and port number of the VTN.
                send_registration:      ('True' or 'False') If 'True', send a one-time registration request to the VTN,
                                        obtaining the VEN ID. The agent should be run in this mode initially,
                                        then shut down and run with this parameter set to 'False' thereafter.
                security_level:         If 'high', the VTN and VEN use a third-party signing authority to sign
                                        and authenticate each request.
                                        Default is 'standard' (XML payloads do not contain Signature elements).
                poll_interval_secs:     (integer) How often the VEN should send an OadrPoll to the VTN.
                log_xml:                ('True' or 'False') Whether to write inbound/outbound XML to the agent's log.
                opt_timeout_secs:       (integer) How long to wait before making a default optIn/optOut decision.
                opt_default_decision:   ('optIn' or 'optOut') What optIn/optOut choice to make by default.
                request_events_on_startup: ('True' or 'False') Whether to send oadrRequestEvent to the VTN on startup.
                report_parameters:      A dictionary of definitions of reporting/telemetry parameters.
                client_pem_bundle:      The pem bundle for the user that has been generated on the vtn.
                                        Pem bundle (private key + certificate concatenated)
                vtn_ca_cert:            The path of the certificate from the CA that the
                                        client certs have been signed with.
        """
        _LOGGER.debug("Configuring agent")
        self.ven_id = config.get("ven_id")
        self.ven_name = config.get("ven_name")
        self.vtn_id = config.get("vtn_id")
        self.vtn_address = config.get("vtn_address")
        self.send_registration = config.get("send_registration")
        self.security_level = config.get("security_level")
        self.log_xml = config.get("log_xml")
        self.opt_default_decision = config.get("opt_default_decision")
        loop_frequency = config.get("poll_interval_secs")
        self.poll_interval_secs = int(
            loop_frequency if loop_frequency else PROCESS_LOOP_FREQUENCY_SECS
        )
        self.request_events_on_startup = config.get("request_events_on_startup")
        self.report_parameters = config.get("report_parameters")
        self.client_pem_bundle = config.get("client_pem_bundle")
        self.vtn_ca_cert = config.get("vtn_ca_cert")

        self.opt_timeout_secs = config.get("opt_timeout_secs")
        try:
            self.opt_timeout_secs = int(self.opt_timeout_secs)
        except ValueError:
            self.opt_timeout_secs = DEFAULT_OPT_TIMEOUT_SECS

        if self.poll_interval_secs < PROCESS_LOOP_FREQUENCY_SECS:
            _LOGGER.warning(
                "Poll interval is too frequent: resetting it to {}".format(
                    PROCESS_LOOP_FREQUENCY_SECS
                )
            )
            self.poll_interval_secs = PROCESS_LOOP_FREQUENCY_SECS

        _LOGGER.info("Configuration parameters:")
        _LOGGER.info("\tVEN ID = {}".format(self.ven_id))
        _LOGGER.info("\tVEN name = {}".format(self.ven_name))
        _LOGGER.info("\tVTN ID = {}".format(self.vtn_id))
        _LOGGER.info("\tVTN address = {}".format(self.vtn_address))
        _LOGGER.info("\tSend registration = {}".format(self.send_registration))
        _LOGGER.info("\tSecurity level = {}".format(self.security_level))
        _LOGGER.info("\tPoll interval = {} seconds".format(self.poll_interval_secs))
        _LOGGER.info("\tLog XML = {}".format(self.log_xml))
        _LOGGER.info("\toptIn timeout (secs) = {}".format(self.opt_timeout_secs))
        _LOGGER.info("\toptIn default decision = {}".format(self.opt_default_decision))
        _LOGGER.info(
            "\tRequest events on startup = {}".format(self.request_events_on_startup)
        )
        _LOGGER.info("\treport parameters = {}".format(self.report_parameters))

    def onstart_method(self):
        """The agent has started. Perform initialization and spawn the main process loop."""
        _LOGGER.debug("Starting agent")

        if self.send_registration:
            # VEN registration with the VTN server.
            # Register the VEN, obtaining the VEN ID. This is a one-time action.
            self.send_oadr_create_party_registration()
        try:
            if self.request_events_on_startup:
                # After a restart, the VEN asks the VTN for the status of all current events.
                # When this is sent to the EPRI VTN server, it returns a 500 and logs a "method missing" traceback.
                self.send_oadr_request_event()

            # Send an initial report-registration request to the VTN.
            self.send_oadr_register_report()
        except Exception as err:
            _LOGGER.error("Error in agent startup: {}".format(err), exc_info=True)

        self.run_main_processes()

    def run_main_processes(self):
        """
        Perform periodic tasks, executing them serially.

            Periodic tasks include:
                Poll the VTN server.
                Perform event-management tasks:
                    Force an optIn/optOut decision if too much time has elapsed.
                    Transition event state when appropriate.
                    Expire events that have become completed or canceled.
                Perform report-management tasks:
                    Send telemetry to the VTN for any active report.
                    Transition report state when appropriate.
                    Expire reports that have become completed or canceled.

        This method should be called by your update method every clock tick
        """
        try:
            # If it's been poll_interval_secs since the last poll request, issue a new one.
            if self._last_poll is None or (
                (get_aware_utc_now() - self._last_poll).total_seconds()
                > self.poll_interval_secs
            ):
                self.send_oadr_poll()

            for event in self.active_or_pending_events:
                self.process_event(event)

            for report in self.active_reports:
                self.process_report(report)

        except Exception as err:
            _LOGGER.error("Error in main process loop: {}".format(err), exc_info=True)

    @orm.db_session
    def process_event(self, event: database.EiEvent):
        """
        Perform periodic maintenance for an event.

        Transition its state when appropriate.
        """

        _LOGGER.debug(f"Processing event::: {event.event_id}")
        if event.is_active_or_pending:
            _LOGGER.debug(f"Event {event.event_id} is {event.status}")
            _LOGGER.debug(f"{event}")
            self._complete_event_if_over(event.event_id)
            self._force_opt_type(event.event_id)
            if event.status != enums.EventStatus.ACTIVE.value:
                self._activate_event_if_starts_now(event)

    @orm.db_session
    def _force_opt_type(self, event_id):
        _LOGGER.debug("Forcing Opt Type")
        _LOGGER.debug(f"opt types ")
        event = self.get_event_for_id(event_id)
        if event.opt_type != enums.OptType.NONE.value:
            _LOGGER.debug(f"opt type is not none {event.opt_type}")
            return
        if self.opt_default_decision not in enums.OptType.list():
            _LOGGER.debug("not in opt type list")
            return
        if event.status == enums.EventStatus.ACTIVE.value:
            event.opt_type = self.opt_default_decision
        _LOGGER.debug(f"opt timeout secs {self.opt_timeout_secs}")
        if not bool(self.opt_timeout_secs):
            event.opt_type = self.opt_default_decision
        if datetime.utcnow() >= event.created + timedelta(
            seconds=self.opt_timeout_secs
        ):
            event.opt_type = self.opt_default_decision

    @orm.db_session
    def _complete_event_if_over(self, event_id):
        event = self.get_event_for_id(event_id)
        now = datetime.utcnow()
        if not event.is_active_or_pending:
            return
        if event.end_time is None:
            return
        if now > event.end_time:
            _LOGGER.debug(
                "Setting event %s to status %s",
                event.event_id,
                enums.EventStatus.COMPLETED.value,
            )
            self._set_event_status(event.event_id, enums.EventStatus.COMPLETED)

    @orm.db_session
    def _activate_event_if_starts_now(self, event):
        now = datetime.utcnow()
        if now < event.start_time:
            return
        if event.opt_type != enums.OptType.OPT_IN.value:
            return
        _LOGGER.debug(
            "Setting event {} to status {}".format(
                event.event_id, enums.EventStatus.ACTIVE.value
            )
        )
        self._set_event_status(event.event_id, enums.EventStatus.ACTIVE)

    def process_report(self, rpt: models.EiReport):
        """
        Perform periodic maintenance for a report.

        Send telemetry to the VTN if the report is active.
        Transition its state when appropriate.
        Expire it from the cache if it has become completed or canceled.
        """
        if rpt.is_active_or_pending():
            now = get_aware_utc_now()
            if rpt.status == rpt.STATUS_ACTIVE:
                if rpt.end_time is None or rpt.end_time > now:
                    rpt_interval = (
                        rpt.interval_secs
                        if rpt.interval_secs is not None
                        else DEFAULT_REPORT_INTERVAL_SECS
                    )
                    next_report_time = rpt.last_report + timedelta(seconds=rpt_interval)
                    if get_aware_utc_now() > next_report_time:
                        # Possible enhancement: Use a periodic gevent instead of a timeout?
                        self.send_oadr_update_report(rpt)
                        if rpt_interval == 0:
                            # OADR rule 324: If rpt_interval == 0 it's a one-time report, so set status to COMPLETED.
                            rpt.status = rpt.STATUS_COMPLETED
                            self.commit()
                else:
                    _LOGGER.debug(
                        "Setting report {} to status {}".format(
                            rpt.report_request_id, rpt.STATUS_COMPLETED
                        )
                    )
                    self.set_report_status(rpt, rpt.STATUS_COMPLETED)
            else:
                if rpt.start_time < now and (
                    rpt.end_time is None or now < rpt.end_time
                ):
                    _LOGGER.debug(
                        "Setting report {} to status {}".format(
                            rpt.report_request_id, rpt.STATUS_ACTIVE
                        )
                    )
                    self.set_report_status(rpt, rpt.STATUS_ACTIVE)
        else:
            # Expire reports from the cache if they're completed or canceled.
            _LOGGER.debug("Expiring report {} from cache".format(rpt.report_request_id))
            self.expire_report(rpt)

    # TODO: Check that everything done here is done in the refactored version. PA 2/9/19
    # def force_opt_type_decision(self, event_id: str):
    #     """
    #     Force an opt-in/opt-out default decision if lots of time has elapsed with
    #     no decision from the control agent.

    #     The default choice comes from "opt_default_decision" in the agent config.
    #     """
    #     event = self.get_event_for_id(event_id)
    #     if (
    #         event
    #         and event.is_active_or_pending
    #         and event.opt_type not in [enums.OptType.OPT_IN, enums.OptType.OPT_OUT]
    #     ):
    #         event.opt_type = self.opt_default_decision
    #         self.commit()
    #         _LOGGER.info(
    #             "Forcing an {} decision for event {}".format(
    #                 event.opt_type, event.event_id
    #             )
    #         )
    #         if event.status == enums.EventStatus.ACTIVE.value:
    #             # Odd exception scenario: If the event was already active, roll its status back to STATUS_FAR.
    #             self._set_event_status(event.event_id, enums.EventStatus.FAR)
    #         self.send_oadr_created_event(event)  # Tell the VTN.

    # ***************** Methods for Servicing VTN Requests ********************

    def push_request(self, env, request):
        """Callback. The VTN pushed an http request. Service it."""
        _LOGGER.debug("Servicing a VTN push request")
        # self.core.spawn(self.service_vtn_request, request)    # **HA**
        self.service_vtn_request(request)
        # Return an empty response.
        return [response_codes.HTTP_STATUS_CODES[204], "", [("Content-Length", "0")]]

    def service_vtn_request(self, request: str):
        """
        An HTTP request/response was received. Handle it.

        :param request: The request's XML payload.


            Event workflow (see OpenADR Profile Specification section 8.1)...

            Event poll / creation:
                (VEN) oadrPoll
                (VTN) oadrDistributeEvent (all events are included; one oadrEvent element per event)
                (VEN) oadrCreatedEvent with optIn/optOut (if events had oadrResponseRequired)
                        If "always", an oadrCreatedEvent must be sent for each event.
                        If "never", it was a "broadcast" event -- never create an event in response.
                        Otherwise, respond if event state (eventID, modificationNumber) has changed.
                (VTN) oadrResponse

            Event change:
                (VEN) oadrCreatedEvent (sent if the optIn/optOut status has changed)
                (VTN) oadrResponse

            Sample oadrDistributeEvent use case from the OpenADR Program Guide:

                Event:
                    Notification: Day before event
                    Start Time: midnight
                    Duration: 24 hours
                    Randomization: None
                    Ramp Up: None
                    Recovery: None
                    Number of signals: 2
                    Signal Name: simple
                        Signal Type: level
                        Units: LevN/A
                        Number of intervals: equal TOU Tier change in 24 hours (2 - 6)
                        Interval Duration(s): TOU tier active time frame (i.e. 6 hours)
                        Typical Interval Value(s): 0 - 4 mapped to TOU Tiers (0 - Cheapest Tier)
                        Signal Target: None
                    Signal Name: ELECTRICITY_PRICE
                        Signal Type: price
                        Units: USD per Kwh
                        Number of intervals: equal TOU Tier changes in 24 hours (2 - 6)
                        Interval Duration(s): TOU tier active time frame (i.e. 6 hours)
                        Typical Interval Value(s): $0.10 to $1.00 (current tier rate)
                        Signal Target: None
                    Event Targets: venID_1234
                    Priority: 1
                    VEN Response Required: always
                    VEN Expected Response: optIn
                Reports:
                    None

            Report workflow (see OpenADR Profile Specification section 8.3)...

            Report registration interaction:
                (VEN) oadrRegisterReport (METADATA report)
                    VEN sends its reporting capabilities to VTN.
                    Each report, identified by a reportSpecifierID, is described as elements and attributes.
                (VTN) oadrRegisteredReport (with optional oadrReportRequests)
                    VTN acknowledges that capabilities have been registered.
                    VTN optionally requests one or more reports by reportSpecifierID.
                    Even if reports were previously requested, they should be requested again at this point.
                (VEN) oadrCreatedReport (if report requested)
                    VEN acknowledges that it has received the report request and is generating the report.
                    If any reports were pending delivery, they are included in the payload.
                (VTN) oadrResponse
                    Why??

            Report creation interaction:
                (VTN) oadrCreateReport
                    See above - this is like the "request" portion of oadrRegisteredReport
                (VEN) oadrCreatedReport
                    See above.

            Report update interaction - this is the actual report:
                (VEN) oadrUpdateReport (report with reportRequestID and reportSpecifierID)
                    Send a report update containing actual data values
                (VTN) oadrUpdatedReport (optional oadrCancelReport)
                    Acknowledge report receipt, and optionally cancel the report

            Report cancellation:
                (VTN) oadrCancelReport (reportRequestID)
                    This can be sent to cancel a report that is in progress.
                    It should also be sent if the VEN keeps sending oadrUpdateReport
                        after an oadrUpdatedReport cancellation.
                    If reportToFollow = True, the VEN is expected to send one final additional report.
                (VEN) oadrCanceledReport
                    Acknowledge the cancellation.
                    If any reports were pending delivery, they are included in the payload.

            Key elements in the METADATA payload:
                reportSpecifierID: Report identifier, used by subsequent oadrCreateReport requests
                rid: Data point identifier
                    This VEN reports only two data points: baselinePower, actualPower
                Duration: the amount of time that data can be collected
                SamplingRate.oadrMinPeriod: maximum sampling frequency
                SamplingRate.oadrMaxPeriod: minimum sampling frequency
                SamplingRate.onChange: whether or not data is sampled as it changes

            For an oadrCreateReport example from the OpenADR Program Guide, see test/xml/sample_oadrCreateReport.xml.

        """
        try:
            if self.log_xml:
                _LOGGER.debug("VTN PAYLOAD:")
                _LOGGER.debug(
                    "\n{}".format(
                        etree_.tostring(etree_.fromstring(request), pretty_print=True)
                    )
                )
            payload = oadr_20b.parseString(request, silence=True)
            signed_object = payload.oadrSignedObject
            if signed_object is None:
                raise exceptions.OpenADRInterfaceException(
                    "No SignedObject in payload", response_codes.OADR_BAD_DATA
                )

            if self.security_level == "high":
                # At high security, the request is accompanied by a Signature.
                # (not implemented) The VEN should use a certificate authority to validate and decode the request.
                pass

            # Call an appropriate method to handle the VTN request.
            element_name = self.vtn_request_element_name(signed_object)
            _LOGGER.debug("VTN: {}".format(element_name))
            request_object = getattr(signed_object, element_name)
            request_method = getattr(self, VTN_REQUESTS[element_name])
            request_method(request_object)

            if request_object.__class__.__name__ != "oadrResponseType":
                # A non-default response was received from the VTN. Issue a followup poll request.
                self.send_oadr_poll()

        except exceptions.OpenADRInternalException as err:
            if err.error_code == response_codes.OADR_EMPTY_DISTRIBUTE_EVENT:
                _LOGGER.warning(
                    "Error handling VTN request: {}".format(err)
                )  # No need for a stack trace
            else:
                _LOGGER.warning(
                    "Error handling VTN request: {}".format(err), exc_info=True
                )
        except exceptions.OpenADRInterfaceException as err:
            _LOGGER.warning("Error handling VTN request: {}".format(err), exc_info=True)
            # OADR rule 48: Log the validation failure, send an oadrResponse.eiResponse with an error code.
            self.send_oadr_response(
                err.message, err.error_code or response_codes.OADR_BAD_DATA
            )
        except Exception as err:
            _LOGGER.error("Error handling VTN request: {}".format(err), exc_info=True)
            self.send_oadr_response(str(err), response_codes.OADR_BAD_DATA)

    @staticmethod
    def vtn_request_element_name(signed_object):
        """Given a SignedObject from the VTN, return the element name of the request that it wraps."""
        non_null_elements = [
            name for name in VTN_REQUESTS.keys() if getattr(signed_object, name)
        ]
        element_count = len(non_null_elements)
        if element_count == 1:
            return non_null_elements[0]
        else:
            if element_count == 0:
                error_msg = "Bad request {}, supported types are {}".format(
                    signed_object, VTN_REQUESTS.keys()
                )
            else:
                error_msg = "Bad request {}, too many signedObject elements".format(
                    signed_object
                )
            raise exceptions.OpenADRInterfaceException(error_msg, None)

    # ***************** Handle Requests from the VTN to the VEN ********************

    def handle_oadr_created_party_registration(
        self, oadr_created_party_registration: etree_.Element
    ):
        """
        The VTN has responded to oadrCreatePartyRegistration
        by sending oadrCreatedPartyRegistration.
        """
        self.oadr_current_service = EIREGISTERPARTY
        self.check_ei_response(oadr_created_party_registration.eiResponse)

        registration = extractors.decode_oadr_created_party_registration(
            oadr_created_party_registration
        )

        _LOGGER.info(f"The VTN supplied {registration.vtn_id} as the vtn_id")
        if registration.ven_id:
            _LOGGER.info(f"The VTN supplied {registration.ven_id} as the ven_id")
        if registration.poll_interval_secs:
            _LOGGER.info(
                f"The VTN requested a poll frequency of {registration.poll_interval_secs} (poll_interval_secs)"
            )

        _LOGGER.info(
            "Please set these values in the VEN agent config, set send_registration to False in the VEN config and restart the agent."
        )

    def handle_oadr_distribute_event(self, oadr_distribute_event: etree_.Element):
        """
        The VTN has responded to an oadrPoll by sending an oadrDistributeEvent.

        Create or update an event, then respond with oadrCreatedEvent.

        For sample XML, see test/xml/sample_oadrDistributeEvent.xml.
        """
        self.oadr_current_service = EIEVENT
        self.oadr_current_request_id = None
        if getattr(oadr_distribute_event, "eiResponse"):
            self.check_ei_response(oadr_distribute_event.eiResponse)

        # OADR rule 41: requestID does not need to be unique.
        self.oadr_current_request_id = oadr_distribute_event.requestID

        vtn_id = oadr_distribute_event.vtnID
        if vtn_id is not None and vtn_id != self.vtn_id:
            raise exceptions.OpenADRInterfaceException(
                "vtnID failed to match agent config: {}".format(vtn_id),
                response_codes.OADR_BAD_DATA,
            )

        oadr_event_list = oadr_distribute_event.oadrEvent
        if len(oadr_event_list) == 0:
            raise exceptions.OpenADRInternalException(
                "oadrDistributeEvent received with no events",
                response_codes.OADR_EMPTY_DISTRIBUTE_EVENT,
            )

        oadr_event_ids = []
        for oadr_event in oadr_event_list:
            try:
                event = self.handle_oadr_event(oadr_event)
                if event:
                    oadr_event_ids.append(event.event_id)
            except exceptions.OpenADRInterfaceException as err:
                # OADR rule 19: If a VTN message contains a mix of valid and invalid events,
                # respond to the valid ones. Don't reject the entire message due to invalid events.
                # OADR rule 48: Log the validation failure and send the error code in oadrCreatedEvent.eventResponse.
                # (The oadrCreatedEvent's eiResponse should contain a 200 -- normal -- status code.)
                _LOGGER.warning("Event error: {}".format(err), exc_info=True)

                # Construct a temporary EIEvent to hold data that will be reported in the error return.
                if oadr_event.eiEvent and oadr_event.eiEvent.eventDescriptor:
                    event_id = oadr_event.eiEvent.eventDescriptor.eventID
                    modification_number = (
                        oadr_event.eiEvent.eventDescriptor.modificationNumber
                    )
                else:
                    event_id = None
                    modification_number = None
                with orm.db_session:
                    error_event = database.EiEvent(
                        event_id=event_id,
                        request_id=self.oadr_current_request_id,
                        modification_number=modification_number,
                    )
                self.send_oadr_created_event(
                    error_event,
                    error_code=err.error_code or response_codes.OADR_BAD_DATA,
                    error_message=err.message,
                )

            except Exception as err:
                _LOGGER.warning(
                    "Unanticipated error during event processing: {}".format(err),
                    exc_info=True,
                )
                self.send_oadr_response(str(err), response_codes.OADR_BAD_DATA)

        self._cancel_events_not_in_recent_event_list(oadr_event_ids)

    @orm.db_session
    def _cancel_events_not_in_recent_event_list(self, oadr_event_ids):
        """
        Implied cancel:

        OADR rule 61: If the VTN request omitted an active event, cancel it.

        Also, think about whether to alert the VTN about this cancellation by sending it an oadrCreatedEvent.
        """
        stored_events = database.EiEvent.select()[:]
        for event in stored_events:
            if event.event_id not in oadr_event_ids:
                _LOGGER.debug(
                    "Event ID {} not in distributeEvent: canceling it.".format(
                        event.event_id
                    )
                )
                self.handle_event_cancellation(event, "never")

    @orm.db_session
    def handle_oadr_event(
        self, oadr_event: etree_.Element
    ) -> Optional[database.EiEvent]:
        """
        An oadrEvent was received, usually as part of an oadrDistributeEvent.
        Handle the event creation/update.

        Respond with oadrCreatedEvent.

        For sample XML, see test/xml/sample_oadrDistributeEvent.xml.

        :return: the event that was created or updated
        """

        def _calculate_start_offset(event_data):
            # OADR rule 30: Randomize start_time and end_time if start_after is provided.
            if event_data.start_after:
                seconds = event_data.start_after.seconds * random.random()
                return timedelta(seconds=seconds)
            else:
                return timedelta(seconds=0)

        def _calculate_times(event_data, offset) -> Tuple[datetime, datetime]:
            start_time = event_data.official_start + offset

            # An interval with 0 duration has no defined endTime and remains active
            # until canceled.
            if event_data.duration.total_seconds() <= 0.0:
                end_time = None
            else:
                end_time = start_time + event_data.duration

            return start_time, end_time

        @orm.db_session
        def _create_pony_event(event_data: extractors.EiEventData):
            """Create an EiEvent in the databse."""

            start_offset = _calculate_start_offset(event_data)
            start_time, end_time = _calculate_times(event_data, start_offset)

            pony_event = database.EiEvent(
                event_id=event_data.event_id,
                request_id=self.oadr_current_request_id,
                status=event_data.status.value,
                modification_number=event_data.modification_number,
                priority=event_data.priority,
                official_start=event_data.official_start,
                duration=event_data.duration,
                start_after=event_data.start_after,
                start_offset=start_offset,
                start_time=start_time,
                end_time=end_time,
                signals=event_data.signals,
                test_event=event_data.test_event,
            )

            return pony_event

        @orm.db_session
        def _update_pony_event(
            new_event_data: extractors.EiEventData, existing_event_id
        ):
            event = database.EiEvent.get(id=existing_event_id)
            assert _check_modification_number(
                existing_event_mod_number=event.modification_number,
                updated_event_mod_number=new_event_data.modification_number,
            )
            if event.opt_type == enums.OptType.OPT_OUT:
                # TODO: refactor
                # Do nothing if we have opted out of this event
                return
            if new_event_data.status is enums.EventStatus.CANCELED.value:
                if event.status is not enums.EventStatus.CANCELED.value:
                    # OADR rule 59: The event was just canceled. Process an event cancellation.
                    self.handle_event_cancellation(event, response_required)
                    return

            # Only recalculate date-related values if the VTN has changed them.
            #
            # This is because otherwise, every time we re-recieve an event with a
            # start_after (randomisation) value we would re-randomise the start and end
            # times.  Maybe that would be finebut new_event_dataems edge-casey so we avoid it.

            if (
                event.official_start != new_event_data.official_start
                or event.duration != new_event_data.duration
                or event.start_after != new_event_data.start_after
            ):
                event.start_offset = _calculate_start_offset(new_event_data)
                event.start_time, event.end_time = _calculate_times(
                    new_event_data, event.start_offset
                )

            event.event_id = new_event_data.event_id
            event.request_id = self.oadr_current_request_id
            event.priority = new_event_data.priority
            event.signals = new_event_data.signals
            event.modification_number = new_event_data.modification_number
            event.test_event = new_event_data.test_event
            event.official_start = new_event_data.official_start
            event.duration = new_event_data.duration
            event.start_after = new_event_data.start_after

            # XXX Is there a reason we don't set event.status to the VTN's provided status?

            return event

        def _check_modification_number(
            existing_event_mod_number, updated_event_mod_number
        ):
            if updated_event_mod_number > existing_event_mod_number:
                return True
            if updated_event_mod_number < existing_event_mod_number:
                _LOGGER.debug(
                    f"Out-of-order modification number: {updated_event_mod_number}"
                )
                # OADR rule 58: Respond with error code 450.
                raise exceptions.OpenADRInterfaceException(
                    "Invalid modification number (too low)",
                    response_codes.OADR_MOD_NUMBER_OUT_OF_ORDER,
                )
                return False
            else:
                _LOGGER.debug("No modification number change, taking no action")
                return True

        # Create a temporary EiEvent, constructed from the OadrDistributeEventType.
        ei_event = oadr_event.eiEvent
        response_required = oadr_event.oadrResponseRequired

        if (
            ei_event.eiTarget
            and ei_event.eiTarget.venID
            and self.ven_id not in ei_event.eiTarget.venID
        ):
            # Rule 22: If an eiTarget is furnished, handle the event only if this venID
            # is in the target list.
            return None
        else:
            event_data = extractors.decode_ei_event(ei_event)

            existing_event = database.EiEvent.get(event_id=event_data.event_id)
            if existing_event:

                # if event exists already, check that the modification number has been incremented
                # if it has, update the event
                event = _update_pony_event(event_data, existing_event.id)
            else:
                # create a new event
                event = _create_pony_event(event_data)

            if response_required == "always":
                # OADR rule 12, 62: Send an oadrCreatedEvent if response_required == 'always'.
                # OADR rule 12, 62: If response_required == 'never', do not send an oadrCreatedEvent.
                self.send_oadr_created_event(event)

            return event

    @orm.db_session
    def handle_event_cancellation(
        self, event: database.EiEvent, response_required: str
    ):
        """
        An event was canceled by the VTN. Update local state and publish the news.

        :param event: The event that was cancelled.
        :param response_required: Does the VTN expect a response?  Can be "always" or "never".
        """
        if event.start_after:
            raise NotImplementedError(
                "Event cancellation with start_after not supported"
            )
            # OADR rule 65: If the event has a startAfter value,
            # schedule cancellation for a random future time between now and (now + startAfter).
            max_delay = isodate.parse_duration(event.start_after)  # noqa
            cancel_time = get_aware_utc_now() + timedelta(
                seconds=(max_delay.seconds * random.random())
            )
            cancel_time
            # self.core.schedule(
            #    cancel_time, self._handle_event_cancellation, event, response_required
            # )
        else:
            event.status = enums.EventStatus.CANCELED.value
            if response_required != "never":
                # OADR rule 36: If response_required != never, confirm cancellation with optType = optIn.
                event.optType = event.OPT_TYPE_OPT_IN.value
            self.commit()

    def handle_oadr_register_report(self, request: Any):
        """
        The VTN is sending METADATA, registering the reports that it can send to the VEN.

        Send no response -- the VEN doesn't want any of the VTN's crumby reports.

        :param request: The VTN's request (unused)
        """
        self.oadr_current_service = EIREPORT
        self.oadr_current_request_id = None
        # OADR rule 301: Sent when the VTN wakes up.
        pass

    def handle_oadr_registered_report(self, oadr_registered_report):
        """
        The VTN acknowledged receipt of the METADATA in oadrRegisterReport.

        If the VTN requested any reports (by specifier ID), create them.
        Send an oadrCreatedReport acknowledgment for each request.

        :param oadr_registered_report: the oadrRegisteredReportType element
        """
        self.oadr_current_service = EIREPORT
        self.check_ei_response(oadr_registered_report.eiResponse)
        self.create_or_update_reports(oadr_registered_report.oadrReportRequest)

    def handle_oadr_create_report(self, oadr_create_report):
        """
        Handle an oadrCreateReport request from the VTN.

        The request could have arrived in response to a poll,
        or it could have been part of an oadrRegisteredReport response.

        Create a report for each oadrReportRequest in the list, sending an oadrCreatedReport in response.

        :param oadr_create_report: the oadrCreateReport element
        """
        self.oadr_current_service = EIREPORT
        self.oadr_current_request_id = None
        self.create_or_update_reports(oadr_create_report.oadrReportRequest)

    def handle_oadr_updated_report(self, oadr_updated_report):
        """
        The VTN acknowledged receipt of an oadrUpdatedReport, and may have sent
        a report cancellation.

        Check for report cancellation, and cancel the report if necessary. No need to
        send a response to the VTN.

        :param oadr_updated_report: the oadrUpdatedReport element
        """
        self.oadr_current_service = EIREPORT
        self.check_ei_response(oadr_updated_report.eiResponse)
        oadr_cancel_report = oadr_updated_report.oadrCancelReport
        if oadr_cancel_report:
            self.cancel_report(oadr_cancel_report.reportRequestID, acknowledge=False)

    def handle_oadr_cancel_report(self, oadr_cancel_report):
        """
        The VTN responded to an oadrPoll by requesting a report cancellation.

        Respond by canceling the report, then send oadrCanceledReport to the VTN.

        :param oadr_cancel_report: the oadrCancelReportType element
        """
        self.oadr_current_service = EIREPORT
        self.oadr_current_request_id = oadr_cancel_report.requestID
        self.cancel_report(oadr_cancel_report.reportRequestID, acknowledge=True)

    def handle_oadr_response(self, oadr_response):
        """
        The VTN has acknowledged a VEN request such as oadrCreatedReport.

        No response is needed.

        :param oadr_response: The VTN's request.
        """
        self.check_ei_response(oadr_response.eiResponse)

    def check_ei_response(self, tree):
        """
        An eiResponse can appear in multiple kinds of VTN requests.

        If an eiResponse has been received, check for a '200' (OK) response code.
        If any other code is received, the VTN is reporting an error -- log it and raise an exception.

        :param tree: (eiResponseType) The VTN's eiResponse.
        """
        response = extractors.decode_ei_response(tree)

        self.oadr_current_request_id = response.request_id
        if response.code != response_codes.OADR_VALID_RESPONSE:
            error_text = f"Error response from VTN, code={response.code}, description={response.description}"
            _LOGGER.error(error_text)
            raise exceptions.OpenADRInternalException(error_text, response.code)

    def create_or_update_reports(self, report_list):
        """
        Process report creation/update requests from the VTN (which could have arrived in different payloads).

        The requests could have arrived in response to a poll,
        or they could have been part of an oadrRegisteredReport response.

        Create/Update reports, and publish info about them on the volttron message bus.
        Send an oadrCreatedReport response to the VTN for each report.

        :param report_list: A iterable of oadrReportRequest. Can be None.
        """

        def get_default_interval(report_specifier, report_params):
            if "report_interval_secs_default" in report_params:
                try:
                    return int(report_params["report_interval_secs_default"])
                except ValueError:
                    raise ValueError(
                        f"Default report interval {report_params['report_interval_secs_default']}"
                        f" for report {report_specifier} is not an integer number of seconds"
                    )
            else:
                return None

        def create_temp_rpt(report_request) -> models.EiReport:
            """Validate the report request, creating a temporary EiReport instance in the process."""

            specifier_id = extractors.report_extract_specifier_id(report_request)
            if specifier_id not in self.report_parameters:
                raise exceptions.BadDataError(
                    f"No parameters found for report with specifier ID {specifier_id}"
                )
            report_params = self.report_parameters[specifier_id]

            report = extractors.extract_report(
                request=report_request,
                default_interval=get_default_interval(specifier_id, report_params),
            )
            report.name = report_params.get("report_name", None)
            report.telemetry_parameters = json.dumps(
                report_params.get("telemetry_parameters", None)
            )
            return report

        def update_rpt(tmp_rpt, rpt):
            """If the report changed, update its parameters in the database, and publish them on the message bus."""
            if (
                rpt.report_specifier_id != tmp_rpt.report_specifier_id
                or rpt.start_time != tmp_rpt.start_time
                or rpt.end_time != tmp_rpt.end_time
                or rpt.interval_secs != tmp_rpt.interval_secs
            ):
                rpt.copy_from_report(tmp_rpt)
                self.commit()

        def create_rpt(tmp_rpt):
            """Store the new report request in the database, and publish it on the message bus."""
            self.add_report(tmp_rpt)

        def cancel_rpt(rpt):
            """A report cancellation was received. Process it and notify interested parties."""
            rpt.status = rpt.STATUS_CANCELED
            self.commit()

        oadr_report_request_ids = []

        try:
            if report_list:
                for oadr_report_request in report_list:
                    temp_report = create_temp_rpt(oadr_report_request)
                    existing_report = self.get_report_for_report_request_id(
                        temp_report.report_request_id
                    )
                    if temp_report.status == temp_report.STATUS_CANCELED:
                        if existing_report:
                            oadr_report_request_ids.append(
                                temp_report.report_request_id
                            )
                            cancel_rpt(existing_report)
                            self.send_oadr_created_report(oadr_report_request)
                        else:
                            # Received notification of a new report, but it's already canceled. Take no action.
                            pass
                    else:
                        oadr_report_request_ids.append(temp_report.report_request_id)
                        if temp_report.report_specifier_id == "METADATA":
                            # Rule 301/327: If the request's specifierID is 'METADATA', send an oadrRegisterReport.
                            self.send_oadr_created_report(oadr_report_request)
                            self.send_oadr_register_report()
                        elif existing_report:
                            update_rpt(temp_report, existing_report)
                            self.send_oadr_created_report(oadr_report_request)
                        else:
                            create_rpt(temp_report)
                            self.send_oadr_created_report(oadr_report_request)
        except exceptions.OpenADRInterfaceException as err:
            # If a VTN message contains a mix of valid and invalid reports, respond to the valid ones.
            # Don't reject the entire message due to an invalid report.
            _LOGGER.warning("Report error: {}".format(err), exc_info=True)
            self.send_oadr_response(
                err.message, err.error_code or response_codes.OADR_BAD_DATA
            )
        except Exception as err:
            _LOGGER.warning(
                "Unanticipated error during report processing: {}".format(err),
                exc_info=True,
            )
            self.send_oadr_response(str(err), response_codes.OADR_BAD_DATA)

        all_active_reports = self._get_reports()
        for agent_report in all_active_reports:
            if agent_report.report_request_id not in oadr_report_request_ids:
                # If the VTN's request omitted an active report, treat it as an implied cancellation.
                report_request_id = agent_report.report_request_id
                _LOGGER.debug(
                    "Report request ID {} not sent by VTN, canceling the report.".format(
                        report_request_id
                    )
                )
                self.cancel_report(report_request_id, acknowledge=True)

    def cancel_report(self, report_request_id: str, acknowledge: bool = False):
        """
        The VTN asked to cancel a report, in response to either report telemetry or an oadrPoll. Cancel it.

        :param report_request_id: The report_request_id of the report to be canceled.
        :param acknowledge: If True, send an oadrCanceledReport acknowledgment to the VTN.
        """
        if report_request_id is None:
            raise exceptions.OpenADRInterfaceException(
                "Missing oadrCancelReport.reportRequestID", response_codes.OADR_BAD_DATA
            )
        report = self.get_report_for_report_request_id(report_request_id)
        if report:
            report.status = report.STATUS_CANCELED
            self.commit()
            if acknowledge:
                self.send_oadr_canceled_report(report_request_id)
        else:
            # The VEN got asked to cancel a report that it doesn't have. Do nothing.
            pass

    # ***************** Send Requests from the VEN to the VTN ********************

    def send_oadr_poll(self):
        """Send oadrPoll to the VTN."""
        _LOGGER.debug("VEN: oadrPoll")
        self.oadr_current_service = POLL
        # OADR rule 37: The VEN must support the PULL implementation.
        self._last_poll = get_aware_utc_now()
        self.send_vtn_request(
            "oadrPoll", builders.OadrPollBuilder(ven_id=self.ven_id).build()
        )

    def send_oadr_query_registration(self):
        """Send oadrQueryRegistration to the VTN."""
        _LOGGER.debug("VEN: oadrQueryRegistration")
        self.oadr_current_service = EIREGISTERPARTY
        self.send_vtn_request(
            "oadrQueryRegistration", builders.OadrQueryRegistrationBuilder().build()
        )

    def send_oadr_create_party_registration(self):
        """Send oadrCreatePartyRegistration to the VTN."""
        _LOGGER.debug("VEN: oadrCreatePartyRegistration")
        if self.ven_name == "":
            raise exceptions.OpenADRException("You need a ven_name to register")
        self.oadr_current_service = EIREGISTERPARTY
        send_signature = self.security_level == "high"
        # OADR rule 404: If the VEN hasn't registered before, venID and registrationID should be empty.
        builder = builders.OadrCreatePartyRegistrationBuilder(
            ven_id=None, xml_signature=send_signature, ven_name=self.ven_name
        )
        self.send_vtn_request("oadrCreatePartyRegistration", builder.build())

    def send_oadr_request_event(self):
        """Send oadrRequestEvent to the VTN."""
        _LOGGER.debug("VEN: oadrRequestEvent")
        self.oadr_current_service = EIEVENT
        self.send_vtn_request(
            "oadrRequestEvent",
            builders.OadrRequestEventBuilder(ven_id=self.ven_id).build(),
        )

    def send_oadr_created_event(
        self, event: database.EiEvent, error_code: str = None, error_message: str = None
    ):
        """
        Send oadrCreatedEvent to the VTN.

        :param event: The event that is the subject of the request.
        :param error_code: eventResponse error code. Used when reporting event protocol errors.
        :param error_message: eventResponse error message. Used when reporting event protocol errors.
        """
        _LOGGER.debug("VEN: oadrCreatedEvent")
        self.oadr_current_service = EIEVENT
        builder = builders.OadrCreatedEventBuilder(
            event=event,
            ven_id=self.ven_id,
            error_code=error_code,
            error_message=error_message,
        )
        self.send_vtn_request("oadrCreatedEvent", builder.build())

    def send_oadr_register_report(self):
        """
        Send oadrRegisterReport (METADATA) to the VTN.

        Sample oadrRegisterReport from the OpenADR Program Guide:

            <oadr:oadrRegisterReport ei:schemaVersion="2.0b">
                <pyld:requestID>RegReq120615_122508_975</pyld:requestID>
                <oadr:oadrReport>
                    --- See oadr_report() ---
                </oadr:oadrReport>
                <ei:venID>ec27de207837e1048fd3</ei:venID>
            </oadr:oadrRegisterReport>
        """
        _LOGGER.debug("VEN: oadrRegisterReport")
        self.oadr_current_service = EIREPORT
        # The VEN is currently hard-coded to support the 'telemetry' report, which sends baseline and measured power,
        # and the 'telemetry_status' report, which sends online and manual_override status.
        # In order to support additional reports and telemetry types, the VEN would need to store other data elements
        # as additional columns in its SQLite database.
        builder = builders.OadrRegisterReportBuilder(
            reports=self.metadata_reports(), ven_id=self.ven_id
        )
        # The EPRI VTN server responds to this request with "452: Invalid ID". Why?
        self.send_vtn_request("oadrRegisterReport", builder.build())

    def send_oadr_update_report(self, report: models.EiReport):
        """
        Send telemetry for a given report to the VTN using oadrUpdateReport.

        Sample oadrUpdateReport from the OpenADR Program Guide:

            <oadr:oadrUpdateReport ei:schemaVersion="2.0b">
                <pyld:requestID>ReportUpdReqID130615_192730_445</pyld:requestID>
                <oadr:oadrReport>
                    --- See OadrUpdateReportBuilder ---
                </oadr:oadrReport>
                <ei:venID>VEN130615_192312_582</ei:venID>
            </oadr:oadrUpdateReport>
        """
        _LOGGER.debug(
            "VEN: oadrUpdateReport (report {})".format(report.report_request_id)
        )
        self.oadr_current_service = EIREPORT
        telemetry = (
            self.get_new_telemetry_for_report(report)
            if report.report_specifier_id == "telemetry"
            else []
        )
        builder = builders.OadrUpdateReportBuilder(
            report=report,
            telemetry=telemetry,
            online=self.ven_online,
            manual_override=self.ven_manual_override,
            ven_id=self.ven_id,
        )
        self.send_vtn_request("oadrUpdateReport", builder.build())
        report.last_report = get_aware_utc_now()
        self.commit()

    def send_oadr_created_report(self, report_request):
        """
            Send oadrCreatedReport to the VTN.

        @param report_request: (oadrReportRequestType) The VTN's report request.
        """
        _LOGGER.debug("VEN: oadrCreatedReport")
        self.oadr_current_service = EIREPORT
        builder = builders.OadrCreatedReportBuilder(
            report_request_id=report_request.reportRequestID,
            ven_id=self.ven_id,
            pending_report_request_ids=self.get_pending_report_request_ids(),
        )
        self.send_vtn_request("oadrCreatedReport", builder.build())

    def send_oadr_canceled_report(self, report_request_id):
        """
            Send oadrCanceledReport to the VTN.

        @param report_request_id: (string) The reportRequestID of the report that has been canceled.
        """
        _LOGGER.debug("VEN: oadrCanceledReport")
        self.oadr_current_service = EIREPORT
        builder = builders.OadrCanceledReportBuilder(
            request_id=self.oadr_current_request_id,
            report_request_id=report_request_id,
            ven_id=self.ven_id,
            pending_report_request_ids=self.get_pending_report_request_ids(),
        )
        self.send_vtn_request("oadrCanceledReport", builder.build())

    def send_oadr_response(self, description: str, code: str):
        """
        Send an oadrResponse to the VTN.
        """
        _LOGGER.debug("VEN: oadrResponse")
        builder = builders.OadrResponseBuilder(
            response_code=code,
            response_description=description,
            request_id=self.oadr_current_request_id or "0",
            ven_id=self.ven_id,
        )
        self.send_vtn_request("oadrResponse", builder.build())

    def send_vtn_request(self, request_name, request_object):
        """
            Send a request to the VTN. If the VTN returns a non-empty response, service that request.

            Wrap the request in a SignedObject and then in Payload XML, and post it to the VTN via HTTP.
            If using high security, calculate a digital signature and include it in the request payload.

        @param request_name: (string) The name of the SignedObject attribute where the request is attached.
        @param request_object: (various oadr object types) The request to send.
        """
        signed_object = oadr_20b.oadrSignedObject(**{request_name: request_object})
        try:
            # Export the SignedObject as an XML string.
            buff = StringIO()
            signed_object.export(buff, 1, pretty_print=True)
            signed_object_serialised_xml = buff.getvalue()
        except Exception as err:
            raise exceptions.OpenADRInterfaceException(
                "Error exporting the SignedObject: {}".format(err), None
            )

        if self.security_level == "high":
            try:
                signature_lxml, signed_object_lxml = self.calculate_signature(
                    signed_object_serialised_xml
                )
            except Exception as err:
                raise exceptions.OpenADRInterfaceException(
                    "Error signing the SignedObject: {}".format(err), None
                )
            payload_lxml = self.payload_element(signature_lxml, signed_object_lxml)
            try:
                # Verify that the payload, with signature, is well-formed and can be validated.
                signxml.XMLVerifier().verify(payload_lxml, ca_pem_file=self.vtn_ca_cert)
            except Exception as err:
                raise exceptions.OpenADRInterfaceException(
                    "Error verifying the SignedObject: {}".format(err), None
                )
        else:
            signed_object_lxml = etree_.fromstring(signed_object_serialised_xml)
            payload_lxml = self.payload_element(None, signed_object_lxml)

        if self.log_xml:
            _LOGGER.debug("VEN PAYLOAD:")
            _LOGGER.debug(
                "\n{}".format(etree_.tostring(payload_lxml, pretty_print=True))
            )

        # Post payload XML to the VTN as an HTTP request. Return the VTN's response, if any.
        endpoint = self.vtn_address + (self.oadr_current_service or POLL)
        try:
            payload_xml = etree_.tostring(payload_lxml)
            # OADR rule 53: If simple HTTP mode is used, send the following headers: Host, Content-Length, Content-Type.
            # The EPRI VTN server responds with a 400 "bad request" if a "Host" header is sent.
            _LOGGER.debug("Posting VEN request to {}".format(endpoint))
            response = requests.post(
                endpoint,
                cert=self.client_pem_bundle,
                data=payload_xml,
                headers={
                    # "Host": endpoint,
                    "Content-Length": str(len(payload_xml)),
                    "Content-Type": "application/xml",
                },
            )
            http_code = response.status_code
            if http_code == 200:
                if len(response.content) > 0:
                    self.service_vtn_request(response.content)
                else:
                    _LOGGER.warning("Received zero-length request from VTN")
            elif http_code == 204:
                # Empty response received. Take no action.
                _LOGGER.debug("Empty response received from {}".format(endpoint))
            else:
                _LOGGER.error(
                    "Error in http request to {}: response={}".format(
                        endpoint, http_code
                    ),
                    exc_info=True,
                )
                raise exceptions.OpenADRInterfaceException(
                    "Error in VTN request: {}".format(http_code)
                    + ":"
                    + str(response.content),
                    None,
                )
        except ConnectionError:
            _LOGGER.warning(
                "ConnectionError in http request to {} (is the VTN offline?)".format(
                    endpoint
                )
            )
            return None
        except Exception as err:
            raise exceptions.OpenADRInterfaceException(
                "Error posting OADR XML: {}".format(err), None
            )

    # ***************** Event database Requests ********************
    @property
    @orm.db_session
    def unresponded_events(self) -> List[database.EiEvent]:
        return orm.select(
            e
            for e in database.EiEvent
            if e.status == enums.EventStatus.UNRESPONDED.value
        )[:]

    @property
    @orm.db_session
    def near_events(self) -> List[database.EiEvent]:
        return orm.select(
            e for e in database.EiEvent if e.status == enums.EventStatus.NEAR.value
        )[:]

    @property
    @orm.db_session
    def far_events(self) -> List[database.EiEvent]:
        return orm.select(
            e for e in database.EiEvent if e.status == enums.EventStatus.FAR.value
        )[:]

    @property
    @orm.db_session
    def active_events(self) -> List[database.EiEvent]:
        """Return a list of events that are currently in progress
           status is active.
        """
        query = orm.select(
            e for e in database.EiEvent if e.status == enums.EventStatus.ACTIVE.value
        )
        query = query.filter(
            lambda event: event.opt_type != enums.OptType.OPT_OUT.value
        )
        return query[:]

    @property
    def active_or_pending_events(self) -> List[database.EiEvent]:
        """ Returns active or pending events, in the sequence
        active, near, far, unresponded"""
        events: List[database.EiEvent] = []
        if self.active_events:
            events += self.active_events
        if self.near_events:
            events += self.near_events
        if self.far_events:
            events += self.far_events
        if self.unresponded_events:
            events += self.unresponded_events
        return events

    @property
    def is_event_in_progress(self) -> bool:
        """ Is an event in progress? """
        return len(self.active_events) > 0

    @orm.db_session
    def get_event_for_id(self, event_id: str) -> Optional[database.EiEvent]:
        """ Query the DB for the event with the given ID """
        return database.EiEvent.get(event_id=event_id)

    @orm.db_session
    def _set_event_status(self, event_id, status_enum: enums.EventStatus):

        """
        Transition an event from its existing status to a new one.

        :raises exceptions.InvalidStatusException:
        """
        event = self.get_event_for_id(event_id)
        if not isinstance(status_enum, enums.EventStatus):
            raise exceptions.InvalidStatusException(
                "status provided is not a valid EventStatus"
            )
        if status_enum == enums.EventStatus.ACTIVE:
            if event.opt_type != enums.OptType.OPT_IN.value:
                raise exceptions.InvalidStatusException(
                    "can't transition status to ACTIVE if event not opted in"
                )
        _LOGGER.debug(
            f"Transitioning status to {status_enum} for event ID {event.event_id}"
        )
        event.status = status_enum.value

    @property
    def active_reports(self) -> list:
        """Return a list of reports that are neither COMPLETED nor CANCELED."""
        return self._get_reports()

    def add_report(self, report):
        """A new report has been created. Add it to the report cache, and also to the database."""
        self._active_reports[report.report_request_id] = report
        self.EiReports.append(report)
        self.commit()

    def set_report_status(self, report, status):
        _LOGGER.debug(
            "Transitioning status to {} for report request ID {}".format(
                status, report.report_request_id
            )
        )
        report.status = status
        self.commit()

    def expire_report(self, report):
        """Remove the report from the report cache. (It remains in the SQLite database.)"""
        self._active_reports.pop(report.report_request_id)

    def get_report_for_report_request_id(self, report_request_id):
        """Return the EiReport with request ID report_request_id, or None if not found."""
        report_list = self._get_reports(
            report_request_id=report_request_id, active_only=False
        )
        return report_list[0] if len(report_list) == 1 else None

    def get_reports_for_report_specifier_id(self, report_specifier_id):
        """Return the EiReport with request ID report_request_id, or None if not found."""
        return self._get_reports(
            report_specifier_id=report_specifier_id, active_only=True
        )

    def get_pending_report_request_ids(self):
        """Return a list of reportRequestIDs for each active report."""
        # OpenADR rule 329: Include all current report request IDs in the oadrPendingReports list.
        return [r.report_request_id for r in self._get_reports()]

    def _get_reports(
        self,
        report_request_id: str = None,
        report_specifier_id: str = None,
        active_only: bool = True,
        started_after: datetime = None,
        end_time_before: datetime = None,
    ) -> List[models.EiReport]:
        """
        Return a list of reports in our in-agent database, filtered in various ways.

        By default, return only report requests with status=active.
        """
        # For requests by report ID, query the cache first before querying the database.
        if report_request_id:
            report = self._active_reports.get(report_request_id, None)
            if report:
                return [report]

        reports: Iterable[models.EiReport] = self.EiReports
        if report_request_id is not None:
            reports = filter(
                lambda x: x.report_request_id == report_request_id, reports
            )
        if report_specifier_id is not None:
            reports = filter(
                lambda x: x.report_specifier_id == report_specifier_id, reports
            )
        if active_only:
            reports = filter(
                lambda x: x.status
                not in [enums.ReportStatus.COMPLETED, enums.ReportStatus.CANCELED],
                reports,
            )
        if started_after:
            reports = filter(lambda x: x.start_time > started_after, reports)
        if end_time_before:
            # A report's end_time can be None, indicating that it doesn't expire until Canceled.
            # If the report's end_time is None, don't apply this filter to it.
            reports = filter(
                lambda x: x.end_time < end_time_before if x.end_time else True, reports
            )
        return list(reports)

    def metadata_reports(self):
        """Return an EiReport instance containing telemetry metadata for each report definition in agent config."""
        return [
            self.metadata_report(rpt_name) for rpt_name in self.report_parameters.keys()
        ]

    def metadata_report(self, specifier_id):
        """Return an EiReport instance for the indicated specifier_id, or None if its' not in agent config."""
        params = self.report_parameters.get(specifier_id, None)
        # No requestID, no reportRequestID
        report = models.EiReport("", "", specifier_id)
        report.name = params.get("report_name_metadata", None)
        try:
            interval_secs = int(params.get("report_interval_secs_default", None))
        except ValueError:
            error_msg = "Default report interval {} is not an integer number of seconds".format(
                params.get("report_interval_secs_default")
            )
            raise exceptions.OpenADRInternalException(
                error_msg, response_codes.OADR_BAD_DATA
            )
        report.interval_secs = interval_secs
        report.telemetry_parameters = json.dumps(
            params.get("telemetry_parameters", None)
        )
        report.report_specifier_id = specifier_id
        report.status = report.STATUS_INACTIVE
        return report

    def get_new_telemetry_for_report(self, report):
        """Query for relevant telemetry that's arrived since the report was last sent to the VTN."""
        telemetry = self.EiTelemetryValuess
        telemetry = filter(
            lambda x: x.report_request_id == report.report_request_id, telemetry
        )
        telemetry = filter(lambda x: x.created_on > report.last_report, telemetry)
        return list(telemetry)

    def add_telemetry(self, telemetry):
        """New telemetry has been received. Add it to the database."""
        self.EiTelemetryValuess.append(telemetry)
        self.commit()

    def telemetry_cleanup(self):
        """gevent thread for periodically deleting week-old telemetry from the database."""
        telemetry = self.EiTelemetryValuess
        total_rows = len(telemetry)
        self.EiTelemetryValuess = list(
            filter(
                lambda x: x.created_on > get_aware_utc_now() - timedelta(days=7),
                telemetry,
            )
        )
        deleted_row_count = total_rows - len(self.EiTelemetryValuess)
        if deleted_row_count:
            _LOGGER.debug(
                "Deleting {} outdated of {} total telemetry rows in db".format(
                    deleted_row_count, total_rows
                )
            )
        self.commit()

    def commit(self):
        # State now handled by HA
        # ...need to pass handle to hass.data etc. and then serialize
        pass

    # ***************** Utility Methods ********************

    @staticmethod
    def payload_element(
        signature_lxml: Optional[etree_.Element], signed_object_lxml: etree_.Element
    ) -> etree_.Element:
        """
            Construct and return an XML element for Payload.

            Append a child Signature element if one is provided.
            Append a child SignedObject element.

        :param signature_lxml: Signature element.
        :param signed_object_lxml: SignedObject element.
        :return: Payload element.
        """
        payload = etree_.Element(
            "{http://openadr.org/oadr-2.0b/2012/07}oadrPayload",
            nsmap=signed_object_lxml.nsmap,
        )
        if signature_lxml:
            payload.append(signature_lxml)
        payload.append(signed_object_lxml)
        return payload

    @staticmethod
    def calculate_signature(
        self, serialised_xml: str
    ) -> Tuple[etree_.Element, etree_.Element]:
        """
        Calculate a digital signature for the SignedObject to be sent to the VTN.

        Returns a tuple of
            1. An object representing the root of the XML tree containing the signature and the payload data.
            2. The XML tree parsed from serialised_xml
        """

        private_key, certificate = pem.parse_file(self.client_pem_bundle)
        xml_tree = etree_.fromstring(serialised_xml)
        xml_tree.set("Id", "signedObject")
        # Use XMLSigner to create a Signature.
        # Use "detached method": the signature lives alonside the signed object in the XML element tree.
        # Use c14n "exclusive canonicalization": the signature is independent of namespace inclusion/exclusion.
        signer = signxml.XMLSigner(
            method=signxml.methods.detached,
            c14n_algorithm="http://www.w3.org/2001/10/xml-exc-c14n#",
        )
        signature_root = signer.sign(
            xml_tree,
            key=private_key.as_bytes(),
            cert=certificate.as_bytes(),
            key_name="123",
        )
        # This generated Signature lacks the ReplayProtect property described in
        # OpenADR profile spec section 10.6.3.
        return signature_root, xml_tree

    def json_object(self, obj):
        """Ensure that an object is valid JSON by dumping it with json_converter and then reloading it."""
        obj_string = json.dumps(obj, default=self.json_converter)
        obj_json = json.loads(obj_string)
        return obj_json

    @staticmethod
    def json_converter(object_to_dump):
        """When calling json.dumps, convert datetime instances to strings."""
        if isinstance(object_to_dump, datetime):
            return object_to_dump.__str__()
