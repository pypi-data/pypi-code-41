from plone.app.vocabularies.catalog import CatalogSource
try:
    from plone.app.widgets.dx import RelatedItemsWidget
    from plone.autoform import directives as form
except ImportError:
    RelatedItemsWidget = None
from plone.memoize.view import memoize
from plone.tiles import Tile
from plone.supermodel import model
from plone import api
from Products.Five.browser.pagetemplatefile import ViewPageTemplateFile
from zExceptions import Unauthorized
from zope import schema
from .config import IMAGE_NAMES
from .utils import uuidToObject
from . import _


class IContentSummaryTile(model.Schema):

    content_uid = schema.Choice(
        title=_(u'Select an existing content item'),
        required=True,
        source=CatalogSource(),
    )
    if RelatedItemsWidget is not None:
        form.widget('content_uid', RelatedItemsWidget)

    show_description = schema.Bool(
        title=_(u'Show content description'),
        default=False,
    )

    show_date = schema.Bool(
        title=_(u'Show publication date'),
        description=_(u'Include the publication date in the '
                      u'summary (events will always include the start date)'),
        default=False,
    )

    style = schema.Choice(
        title=_(u'Select the display orientation'),
        default=u'landscape',
        values=(u'landscape', u'portrait'),
    )


class ContentSummaryTile(Tile):
    """Existing content tile
    """

    template = ViewPageTemplateFile('templates/summary.pt')
    show_description = False

    def __call__(self):
        self.update()
        return self.template()

    def update(self):
        self.show_description = self.data.get('show_description', False)
        self.show_date = self.data.get('show_date', False)

    @property
    @memoize
    def content(self):
        uuid = self.data.get('content_uid')
        if uuid != api.content.get_uuid(self.context):
            try:
                item = uuidToObject(uuid)
            except Unauthorized:
                item = None
                if not self.request.get('PUBLISHED'):
                    raise  # Should raise while still traversing
            if item is not None:
                return item
        return None

    def image_url(self, obj=None, scale_name="preview"):
        content = obj or self.content
        if content is None:
            return

        images_view = content.unrestrictedTraverse('@@images')

        for field_name in IMAGE_NAMES:
            try:
                scale = images_view.scale(fieldname=field_name,
                                          scale=scale_name)
            except AttributeError:
                continue
            if scale is not None:
                return scale.url

    @property
    def orientation(self):
        return self.data.get('style', 'landscape')
