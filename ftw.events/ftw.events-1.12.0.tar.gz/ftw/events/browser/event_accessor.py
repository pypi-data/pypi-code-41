from ftw.events.contents.eventpage import IEventPageSchema
from ftw.events.interfaces import IEventPage
from plone.app.event.dx.behaviors import EventAccessor
from plone.event.interfaces import IEventAccessor
from zope.component import adapter
from zope.interface import implementer


@adapter(IEventPageSchema)
@implementer(IEventAccessor)
class FtwEventAccessor(EventAccessor):
    def __init__(self, context):
        super(FtwEventAccessor, self).__init__(context)
        self._behavior_map['location'] = IEventPage
