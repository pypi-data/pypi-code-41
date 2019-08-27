import logging
from datetime import datetime
from datetime import timedelta

import pytest

from .factories import EventFactory
from pyoadr_ven import database
from pyoadr_ven import exceptions
from pyoadr_ven.enums import EventStatus
from pyoadr_ven.enums import OptType
from pyoadr_ven.enums import ReportStatus

_LOGGER = logging.getLogger(__name__)
pytestmark = pytest.mark.pony


class TestSetEventStatusTransition:
    def test_from_unresponded_to_completed(self, agent):
        event = EventFactory()
        assert event.status == EventStatus.UNRESPONDED.value
        assert agent.unresponded_events[0] == event
        assert agent.active_or_pending_events[0] == event
        assert database.EiEvent.get(status=EventStatus.UNRESPONDED.value) == event
        agent.set_event_status(event, EventStatus.COMPLETED)
        assert event.status == EventStatus.COMPLETED.value
        assert agent.active_or_pending_events == []
        assert database.EiEvent.get(status=EventStatus.COMPLETED.value) == event

    def test_from_unresponded_to_near(self, agent):
        event = EventFactory()
        agent.set_event_status(event, EventStatus.NEAR)
        assert event.status == EventStatus.NEAR.value
        assert agent.active_or_pending_events == [event]
        assert database.EiEvent.get(status=EventStatus.NEAR.value) == event

    def test_from_unresponded_to_far(self, agent):
        event = EventFactory()
        agent.set_event_status(event, EventStatus.FAR)
        assert event.status == EventStatus.FAR.value
        assert agent.active_or_pending_events == [event]
        assert database.EiEvent.get(status=EventStatus.FAR.value) == event

    def test_from_unresponded_to_active(self, agent):
        event = EventFactory()
        agent.set_event_status(event, EventStatus.ACTIVE)
        assert event.status == EventStatus.ACTIVE.value
        assert agent.active_or_pending_events == [event]
        assert database.EiEvent.get(status=EventStatus.ACTIVE.value) == event

    def test_from_active_to_completed(self, agent):
        event = EventFactory(status=EventStatus.ACTIVE.value)
        assert event.status == EventStatus.ACTIVE.value
        agent.set_event_status(event, EventStatus.COMPLETED)
        assert event.status == EventStatus.COMPLETED.value
        assert agent.active_or_pending_events == []
        assert database.EiEvent.get(status=EventStatus.COMPLETED.value) == event

    def test_invalid_status_string(self, agent):
        event = EventFactory()
        status_before = event.status
        with pytest.raises(exceptions.InvalidStatusException):
            agent.set_event_status(event, "invalid thing!")
            assert event.status == status_before

    def test_invalid_status_enum(self, agent):
        event = EventFactory()
        status_before = event.status
        with pytest.raises(exceptions.InvalidStatusException):
            agent.set_event_status(event, ReportStatus.ACTIVE)
            assert event.status == status_before


class TestProcessEvent:
    def test_event_is_active_happening_and_opted_in(self, agent):
        event = EventFactory(
            start_time=datetime.utcnow() - timedelta(minutes=5),
            end_time=datetime.utcnow() + timedelta(hours=1),
            status=EventStatus.ACTIVE.value,
        )
        agent.process_event(event)
        assert event.status == EventStatus.ACTIVE.value
        assert event in agent.active_events

    def test_event_completed_if_over(self, agent):
        event = EventFactory(
            start_time=datetime.utcnow() - timedelta(hours=1),
            end_time=datetime.utcnow() - timedelta(minutes=5),
            status=EventStatus.ACTIVE.value,
        )
        agent.process_event(event)
        assert event.status == EventStatus.COMPLETED.value
        assert event not in agent.active_events

    def test_unresponded_event_activated_if_started_and_opted_in(self, agent):
        event = EventFactory(
            start_time=datetime.utcnow() - timedelta(minutes=5),
            end_time=datetime.utcnow() + timedelta(hours=1),
            status=EventStatus.UNRESPONDED.value,
            opt_type=OptType.OPT_IN.value,
        )
        agent.process_event(event)
        assert event.status == EventStatus.ACTIVE.value
        assert event in agent.active_events

    def test_unresponded_event_not_activated_if_started_and_opted_out(self, agent):
        event = EventFactory(
            start_time=datetime.utcnow() - timedelta(minutes=5),
            end_time=datetime.utcnow() + timedelta(hours=1),
            status=EventStatus.UNRESPONDED.value,
            opt_type=OptType.OPT_OUT.value,
        )
        agent.process_event(event)
        assert event.status == EventStatus.UNRESPONDED.value
        assert event not in agent.active_events

    def test_unresponded_event_not_activated_if_started_and_no_opt_type(self, agent):
        event = EventFactory(
            start_time=datetime.utcnow() - timedelta(minutes=5),
            end_time=datetime.utcnow() + timedelta(hours=1),
            status=EventStatus.UNRESPONDED.value,
            opt_type=OptType.NONE.value,
        )
        agent.process_event(event)
        assert event.status == EventStatus.UNRESPONDED.value
        assert event not in agent.active_events
