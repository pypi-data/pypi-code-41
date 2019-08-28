from plone.app.vocabularies.catalog import CatalogSource
from Products.Five.browser.pagetemplatefile import ViewPageTemplateFile
try:
    from plone.app.widgets.dx import RelatedItemsWidget
    from plone.autoform import directives as form
except ImportError:
    RelatedItemsWidget = None
from zExceptions import Unauthorized
from zope import schema
from .summary import ContentSummaryTile
from .summary import IContentSummaryTile
from . import _


class ICollectionSummaryTile(IContentSummaryTile):

    content_uid = schema.Choice(
        title=_(u'Select an existing collection'),
        required=True,
        source=CatalogSource(
            object_provides=(
                'plone.app.contenttypes.behaviors.collection'
                '.ISyndicatableCollection',
                'plone.app.collection.interfaces.ICollection',
            )
        ),
    )
    if RelatedItemsWidget is not None:
        form.widget('content_uid', RelatedItemsWidget)

    show_title = schema.Bool(
        title=_(u'Show collection title'),
        default=True,
    )

    limit = schema.Int(
        title=_(u'Number of items to display'),
        default=3,
        min=1,
    )

    show_description = schema.Bool(
        title=_(u'Show description of result items'),
        default=True,
    )

    show_date = schema.Bool(
        title=_(u'Show publication date of result items'),
        description=_(u'Events will always include start date'),
        default=True,
    )


class CollectionSummaryTile(ContentSummaryTile):
    """Existing content tile
    """

    template = ViewPageTemplateFile('templates/collection.pt')
    summary_template = ViewPageTemplateFile('templates/summary.pt')
    show_description = False
    results = ()
    macro = None

    def update(self):
        super(CollectionSummaryTile, self).update()
        self.macro = self.summary_template.macros['summary']
        self.show_title = self.data.get('show_title', False)
        limit = self.data.get('limit', 3)
        self.results = []
        for b in self.content.results(batch=False, b_size=limit)[:limit]:
            try:
                obj = b.getObject()
                self.results.append(obj)
            except Unauthorized:
                continue
