from datetime import datetime
from ftw.builder import Builder
from ftw.builder import create
from ftw.events.tests import FunctionalTestCase
from ftw.events.tests import RealFuncitionalTestCase
from ftw.testbrowser import browsing
from ftw.testbrowser.core import LIB_REQUESTS
from ftw.testbrowser.pages import editbar
import transaction
import urlparse


class TestIsICSView(RealFuncitionalTestCase):

    def setUp(self):
        self.portal = self.layer['portal']
        self.grant('Manager')
        self.folder = create(Builder('event folder').titled(u'Activities'))

        self.event = create(Builder('event page')
                            .titled(u"A Event")
                            .starting(datetime(2013, 10, 7, 9, 00))
                            .ending(datetime(2013, 10, 7, 16, 00))
                            .having(recurrence='RRULE:FREQ=DAILY;COUNT=4')
                            .within(self.folder))

    @browsing
    def test_ics_view_is_ics(self, browser):
        browser.request_library = LIB_REQUESTS
        browser.login().visit(self.event, view="ics_view")

        body = browser.contents
        self.assertIn('SUMMARY:A Event', body)
        self.assertIn('BEGIN:VCALENDAR', body)
        self.assertIn('BEGIN:VEVENT', body)
        self.assertIn('END:VCALENDAR', body)
        self.assertIn('END:VEVENT', body)

    @browsing
    def test_location_in_ics(self, browser):
        location = 'london baker street 221b'

        browser.request_library = LIB_REQUESTS
        browser.login().visit(self.event, view="ics_view")

        self.assertNotIn(location, browser.contents)

        self.event.location_title = location
        transaction.commit()
        browser.reload()
        self.assertIn(location, browser.contents)

    @browsing
    def test_ics_view_is_ics_on_eventfolder(self, browser):
        browser.request_library = LIB_REQUESTS

        # Create a second event within the event folder
        create(Builder('event page')
               .titled(u"Another Event")
               .starting(datetime(2017, 1, 7, 15, 00))
               .ending(datetime(2017, 1, 7, 20, 00))
               .having(recurrence='RRULE:FREQ=DAILY;COUNT=4')
               .within(self.folder))

        browser.login().visit(self.folder, view="ics_view")

        body = browser.contents

        self.assertIn('BEGIN:VCALENDAR', body)
        self.assertIn('END:VCALENDAR', body)

        # Both events are in the file.
        self.assertEqual(2, body.count("BEGIN:VEVENT"))
        self.assertIn('SUMMARY:A Event', body)
        self.assertIn('SUMMARY:Another Event', body)


class TestICSView(FunctionalTestCase):

    def setUp(self):
        super(TestICSView, self).setUp()
        self.grant('Manager')

    @browsing
    def test_export_action_on_eventfolder(self, browser):
        event_folder = create(Builder('event folder').titled(u'Activities'))
        browser.login().visit(event_folder)

        # in plone 5.1 we have additional get params of the _authenticator.
        # To test if the view is right we strip them off the url.
        ics_url = editbar.contentview('Ical export').attrib['href']
        stripped_ics_url = urlparse.urljoin(ics_url,
                                            urlparse.urlparse(ics_url).path)

        self.assertEqual(
            'http://nohost/plone/activities/ics_view',
            stripped_ics_url,
            'We expect that the action goes to '
            'PloneSite/EventFolder/ics_view.'
        )
