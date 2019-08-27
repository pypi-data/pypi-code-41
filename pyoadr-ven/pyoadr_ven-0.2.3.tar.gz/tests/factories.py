import factory

from pyoadr_ven import database


class EventFactory(factory.Factory):
    class Meta:
        model = database.EiEvent

    request_id = factory.Sequence(lambda n: n)
    event_id = factory.Sequence(lambda n: n)
