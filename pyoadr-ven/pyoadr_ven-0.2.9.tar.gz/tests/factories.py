from datetime import datetime
from datetime import timedelta

import factory
from factory import fuzzy

from pyoadr_ven import database


class EventFactory(factory.Factory):
    class Meta:
        model = database.EiEvent

    request_id = factory.Sequence(lambda n: str(n))
    event_id = factory.Sequence(lambda n: str(n))

    official_start = fuzzy.FuzzyNaiveDateTime(
        datetime.now() + timedelta(days=+1), datetime.now() + timedelta(days=+14)
    )
    duration = timedelta(minutes=30)
    start_after = timedelta(seconds=0)
    start_offset = timedelta(seconds=0)
    start_time = factory.LazyAttribute(lambda e: e.official_start + e.start_offset)
    end_time = factory.LazyAttribute(lambda e: e.official_start + e.duration)
