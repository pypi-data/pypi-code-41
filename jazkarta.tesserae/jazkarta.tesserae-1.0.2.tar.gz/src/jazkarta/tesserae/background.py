from plone.app.textfield import RichText
from plone.autoform.directives import widget
from plone.namedfile.field import NamedBlobImage
from plone.supermodel import model
from plone.tiles import PersistentTile
from Products.Five.browser.pagetemplatefile import ViewPageTemplateFile
from z3c.form.browser.radio import RadioFieldWidget
from zope import schema
from zope.component import queryMultiAdapter
from . import _


class IBackgroundImageTile(model.Schema):

    image = NamedBlobImage(
        title=_(u'Upload an image to use as background'),
        required=False,
    )

    background_color = schema.TextLine(
        title=_(u'Enter a CSS color value to use as a background'),
        description=_(u'This will be overlayed on top of the background '
                      u'image'),
        required=False,
    )

    widget(scale=RadioFieldWidget)
    scale = schema.Choice(
        title=_(u'Select maximum display size'),
        vocabulary='plone.app.vocabularies.ImagesScales',
        default='banner',
    )

    parallax = schema.Bool(
        title=_(u'Enable parallax scroll effect on background image'),
        default=False,
    )

    content = RichText(
        title=_(u'HTML'),
        required=True,
        allowed_mime_types=('text/html',),
        default_mime_type='text/html',
        output_mime_type='text/x-html-safe',
        default=u'',
    )


class BackgroundImageTile(PersistentTile):

    template = ViewPageTemplateFile('templates/background.pt')
    html = u''
    background_color = u''
    parallax = False

    def __call__(self):
        self.update()
        return self.template()

    def update(self):
        self.html = self.data.get('content', False)
        self.background_color = self.data.get('background_color', u'')
        self.parallax = self.data.get('parallax', False)

    def image_url(self):
        scale_name = self.data.get('scale', 'banner')
        images_view = queryMultiAdapter((self, self.context.REQUEST),
                                        name=u'images')
        if images_view is not None:
            try:
                scale = images_view.scale(fieldname='image', scale=scale_name)
            except AttributeError:
                return None
            if scale is not None:
                return scale.url
