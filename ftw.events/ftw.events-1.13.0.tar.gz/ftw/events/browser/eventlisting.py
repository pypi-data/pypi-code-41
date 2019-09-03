from DateTime import DateTime
from Products.CMFPlone.PloneBatch import Batch
from Products.Five.browser import BrowserView
from ftw.events import _
from ftw.events.interfaces import IEventListingView
from plone import api
from plone.app.event.base import _prepare_range
from zope.component import getMultiAdapter
from zope.contentprovider.interfaces import IContentProvider
from zope.i18n import translate
from zope.interface import implements
import datetime


class EventListing(BrowserView):
    """
    EventListingBlock event listing

    This browser view renders a list of event pages based on the parameters
    defined on the event listing block which renders a link to this browser
    view.
    """
    implements(IEventListingView)

    def __init__(self, context, request):
        super(EventListing, self).__init__(context, request)
        self.batch_size = 10

    @property
    def batch(self):
        b_start = self.request.form.get('b_start', 0)
        return Batch(self.get_items(), self.batch_size, b_start)

    def get_query(self):
        block_view = api.content.get_view(
            name='block_view',
            context=self.context,
            request=self.request,
        )

        datestring = self.request.get('archive')
        if datestring:
            try:
                start = DateTime(datestring)
            except DateTime.interfaces.SyntaxError:
                raise
            end = DateTime('{0}/{1}/{2}'.format(
                start.year() + start.month() / 12,
                start.month() % 12 + 1,
                1)
            ) - 1

            start = start.earliestTime()
            end = end.latestTime()
        else:
            start, end = block_view.get_dates_for_query()
        block_query = block_view.get_query(start, end)

        return block_query

    def get_items(self):
        """
        Returns a list of event page brains.
        """
        catalog = api.portal.get_tool(name='portal_catalog')
        return catalog(self.get_query())

    def get_event_page_dict(self, brain):
        """
        Constructs a dict containing the data of the brain of an event page.
        """
        obj = brain.getObject()

        # Copied from "plone.app.event.portlets.portlet_events.Renderer#formatted_date".
        provider = getMultiAdapter(
            (self.context, self.request, self),
            IContentProvider, name='formatted_date'
        )
        date_snippet = provider(obj)

        item = {
            'title': brain.Title,
            'description': brain.Description,
            'url': brain.getURL(),
            'brain': brain,
            'date_snippet': date_snippet,
            'location': obj.location or '',
        }
        return item

    @property
    def title(self):
        """
        Returns the title defined on the event listing block or a
        fallback title.
        """
        fallback_title = translate(
            _('more_items_view_fallback_title', default=u'Events'),
            context=self.request
        )
        return self.context.more_items_view_title or fallback_title

    @property
    def description(self):
        return ''


class EventListingRss(EventListing):
    """
    RSS-Feed event listing

    This view is to be called on an EventListingBlock and does takes its
    parameters into account.
    """

    @property
    def description(self):
        return _(u'label_feed_desc',
                 default=u'${title} - Events Feed',
                 mapping={'title': self.context.Title().decode('utf-8')})

    @property
    def link(self):
        url = self.context.absolute_url() + '/' + self.__name__
        return '<link>{}</link>'.format(url)

    def get_item_link(self, url):
        return '<link>{}</link>'.format(url)


class EventListingFolder(EventListing):
    """
    EventFolder event listing

    This event listing view is a simpler stripped down version of the
    EventListingBlockEventListing. It is used on the EventFolder directly and
    it does not take any EventListingBlock's parameters into account.
    """

    @property
    def title(self):
        return self.context.Title()

    @property
    def description(self):
        return self.context.description

    def get_query(self):
        query = {
            'object_provides': 'ftw.events.interfaces.IEventPage',
            'sort_on': 'start',
            'path': '/'.join(self.context.getPhysicalPath())
        }

        if api.user.has_permission('ftw.events: Add Event Page', obj=self.context):
            query['show_inactive'] = True

        datestring = self.request.get('archive')
        if datestring:
            try:
                start = DateTime(datestring)
            except DateTime.interfaces.SyntaxError:
                raise
            end = DateTime('{0}/{1}/{2}'.format(
                start.year() + start.month() / 12,
                start.month() % 12 + 1,
                1)
            ) - 1

            start, end = start.earliestTime(), end.latestTime()
        else:
            start = datetime.datetime.now().replace(
                hour=0, minute=0, second=0, microsecond=0
            )

            start, end = _prepare_range(self.context, start, None)

        # All events from start date ongoing:
        # The minimum end date of events is the date from which we search.
        query['end'] = {'query': start, 'range': 'min'}
        # All events until end date:
        # The maximum start date must be the date until we search.
        query['start'] = {'query': end, 'range': 'max'}

        return query
