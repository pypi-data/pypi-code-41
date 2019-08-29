from datetime import datetime
from datetime import timedelta
from ftw.builder import builder_registry
from ftw.builder.dexterity import DexterityBuilder
from ftw.simplelayout.tests import builders
from ftw.testing import IS_PLONE_5


class EventFolderBuilder(DexterityBuilder):
    portal_type = 'ftw.events.EventFolder'

builder_registry.register('event folder', EventFolderBuilder)


class EventPageBuilder(DexterityBuilder):
    portal_type = 'ftw.events.EventPage'

    def __init__(self, *args, **kwargs):
        super(EventPageBuilder, self).__init__(*args, **kwargs)
        # ftw.builders auto-discovery does not work for recurrence:
        self.having(recurrence='')
        # using greenwich, since the test-site / browser is set up with it:
        self.having(timezone='Etc/Greenwich')
        # Manually set start and end because an early import of IEventBasic
        # in the `test_staging.py` results to events having no start and end
        now = datetime.utcnow()
        self.starting(now)
        self.ending(now + timedelta(hours=1))

    def starting(self, date):
        if IS_PLONE_5:
            from plone.event.utils import pydt
            return self.having(start=pydt(date))
        else:
            return self.having(start=date)

    def ending(self, date):
        if IS_PLONE_5:
            from plone.event.utils import pydt
            return self.having(end=pydt(date))
        else:
            return self.having(end=date)

builder_registry.register('event page', EventPageBuilder)


class EventListingBlockBuilder(DexterityBuilder):
    portal_type = 'ftw.events.EventListingBlock'

builder_registry.register('event listing block', EventListingBlockBuilder)
