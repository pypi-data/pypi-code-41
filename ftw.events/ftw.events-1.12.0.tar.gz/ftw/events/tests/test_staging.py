from datetime import datetime
from ftw.builder import Builder
from ftw.builder import create
from ftw.events.tests import FunctionalTestCase
from ftw.simplelayout.staging.interfaces import IStaging
from ftw.testbrowser import browsing
from unittest2 import skipIf
from ftw.testing import IS_PLONE_5
from plone.event.utils import pydt
from plone.app.event.dx.behaviors import IEventBasic


@skipIf(IS_PLONE_5, 'Plone 5 has rewritten plone.app.events which makes this test obsolete')
class TestWorkingCopy(FunctionalTestCase):

    def setUp(self):
        self.portal = self.layer['portal']
        self.grant('Manager')

    @browsing
    def test_working_copy_apply_correct_event_dates(self, browser):
        start = pydt(datetime(2013, 10, 7, 9))
        end = pydt(datetime(2013, 10, 7, 16))
        new_end = pydt(datetime(2013, 10, 7, 19))

        folder = create(Builder('event folder'))
        baseline = create(Builder('event page')
                          .having(timezone='Europe/Zurich')
                          .within(folder))

        behaviour = IEventBasic(baseline)
        behaviour.start, behaviour.end = start, end

        self.assertEquals(start, behaviour.start)

        working_copy = IStaging(baseline).create_working_copy(folder)
        self.assertFalse(IStaging(baseline).is_working_copy())

        working_behaviour = IEventBasic(working_copy)
        working_behaviour.end = new_end
        IStaging(working_copy).apply_working_copy()

        self.assertEquals(new_end, behaviour.end)
