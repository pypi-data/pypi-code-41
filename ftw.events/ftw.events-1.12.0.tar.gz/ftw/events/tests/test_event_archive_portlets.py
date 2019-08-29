from datetime import datetime
from ftw.builder import Builder
from ftw.builder import create
from ftw.events.testing import FUNCTIONAL_TESTING
from ftw.events.tests import FunctionalTestCase
from ftw.events.tests.utils import LanguageSetter
from ftw.testbrowser import browsing
from zope.i18n.locales import locales

events_portlet_action = '/++contextportlets++plone.rightcolumn/+/eventsarchiveportlet'


class TestEventArchivePortlets(FunctionalTestCase, LanguageSetter):
    layer = FUNCTIONAL_TESTING

    def setUp(self):
        super(TestEventArchivePortlets, self).setUp()
        self.grant('Manager')

        default = 'en'
        supported = ['en', 'de']
        self.set_language_settings(default, supported)

    def _set_language_de(self):
        """This Function is used to set the language of the plone site.
        We need this, because we wan't to make sure that the language is
        inherited when there isn't one forced.
        """
        locale = locales.getLocale('de')
        target_language = locale.id.language

        # If we get a territory, we enable the combined language codes
        use_combined = False
        if locale.id.territory:
            use_combined = True
            target_language += '_' + locale.id.territory

        # As we have a sensible language code set now, we disable the
        # start neutral functionality (not available in plone 5.1 anymore).
        start_neutral = False

        self.set_language_settings(target_language, [target_language],
                                   use_combined, start_neutral)

    def _add_portlet(self, browser, context=None):
        """
        This helper method adds a events archive portlet on the given context.
        If no context is provided then the portlet will be added on the
        Plone site.
        """
        context = context or self.portal
        browser.login().visit(context, view='@@manage-portlets')
        browser.css('#portletmanager-plone-rightcolumn form')[0].fill(
            {':action': events_portlet_action}).submit()
        browser.css('#form').first.fill({'Title': 'Archive'}).submit()
        browser.open(context)

    @browsing
    def test_archive_portlet_available_when_there_are_events(self, browser):
        events_folder = create(Builder('event folder').titled(u'Event Folder')
                               .with_property('layout', 'event_listing'))
        create(Builder('event page').titled(u'Event Entry').within(events_folder)
               .with_property('layout', 'event_listing'))

        self._add_portlet(browser, events_folder)

        self.assertIn('Archive', browser.css('.event-archive-portlet header h2').text,
                      'Archive portlet is not here but it should be.')

    @browsing
    def test_archive_portlet_not_available_when_empty(self, browser):
        events_folder = create(Builder('event folder').titled(u'Event Folder')
                               .with_property('layout', 'event_listing'))

        self._add_portlet(browser, events_folder)

        self.assertNotIn('Archive', browser.css('dt.portletHeader').text,
                         'Archive portlet is here but it should not be.')

    @browsing
    def test_archive_portlet_summary(self, browser):
        """
        This test makes sure the summary is correct.
        """
        events_folder = create(Builder('event folder').titled(u'Event Folder')
                               .with_property('layout', 'event_listing'))
        create(Builder('event page').titled(u'Event Entry 1').within(events_folder)
               .having(start=datetime(2013, 1, 1), end=datetime(2013, 1, 1)))
        create(Builder('event page').titled(u'Event Entry 2').within(events_folder)
               .having(start=datetime(2013, 1, 11), end=datetime(2013, 1, 11)))
        create(Builder('event page').titled(u'Event Entry 3').within(events_folder)
               .having(start=datetime(2013, 2, 2), end=datetime(2013, 2, 2)))

        self._add_portlet(browser, events_folder)

        self.assertEqual(
            ['http://nohost/plone/event-folder/event_listing?archive=2013/02/01',
                'http://nohost/plone/event-folder/event_listing?archive=2013/01/01'],
            map(lambda month: month.attrib['href'], browser.css('.event-month')))

    @browsing
    def test_archive_portlet_not_available_on_plone_site(self, browser):
        """
        The events archive portlet is only rendered on events listing views.
        """
        events_folder = create(Builder('event folder').titled(u'Event Folder')
                               .with_property('layout', 'event_listing'))
        create(Builder('event page').titled(u'Event Entry 1').within(events_folder))

        self._add_portlet(browser)
        self.assertNotIn('Archive', browser.css('dt.portletHeader').text,
                         'Archive portlet is here but it should not be.')

    @browsing
    def test_archive_portlet_not_available_on_content_page(self, browser):
        """
        The events archive portlet is only rendered on events listing views.
        """
        page = create(Builder('sl content page').titled(u'Content Page'))
        events_folder = create(Builder('event folder').titled(u'Event Folder')
                               .with_property('layout', 'event_listing'))
        create(Builder('event page').titled(u'Event Entry 1').within(events_folder))

        self._add_portlet(browser, page)
        self.assertNotIn('Archive', browser.css('dt.portletHeader').text,
                         'Archive portlet is here but it should not be.')

    @browsing
    def test_archive_portlet_link(self, browser):
        """
        This test makes sure the summary is correct.
        """
        events_folder = create(Builder('event folder').titled(u'Event Folder')
                               .with_property('layout', 'event_listing'))
        create(Builder('event page').titled(u'Event Entry 1').within(events_folder)
               .having(start=datetime(2013, 1, 1), end=datetime(2013, 1, 1)))
        create(Builder('event page').titled(u'Event Entry 2').within(events_folder)
               .having(start=datetime(2013, 1, 11), end=datetime(2013, 1, 11)))

        self._add_portlet(browser, events_folder)

        browser.css('.event-month').first.click()
        self.assertEqual(2, len(browser.css('.event-item')))

    @browsing
    def test_month_with_umlaut(self, browser):
        self._set_language_de()

        events_folder = create(Builder('event folder').titled(u'Event Folder')
                               .with_property('layout', 'event_listing'))
        create(Builder('event page').titled(u'Event Entry 1').within(events_folder)
               .having(start=datetime(2013, 3, 1), end=datetime(2013, 3, 1)))

        # Helper method sets the title in english and not in german
        browser.login().visit(events_folder, view='@@manage-portlets')
        browser.css('#portletmanager-plone-rightcolumn form')[0].fill(
            {':action': events_portlet_action}).submit()
        browser.css('#form').first.fill({'Titel': 'Archiv'}).submit()
        browser.open(events_folder)

        browser.css('.event-month').first.click()
        self.assertEqual(1, len(browser.css('.event-item')))
