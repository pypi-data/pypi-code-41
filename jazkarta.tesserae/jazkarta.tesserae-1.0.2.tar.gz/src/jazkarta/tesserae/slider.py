try:
    from plone.app.contenttypes.interfaces import IImage
except ImportError:
    from zope.interface import Interface as IImage
try:
    from plone.app.z3cform.widget import RelatedItemsWidget
except ImportError:
    from plone.app.widgets.dx import RelatedItemsWidget
from plone.autoform import directives as form
from plone.autoform.interfaces import IFormFieldProvider
from plone.namedfile.field import NamedBlobImage
from plone.supermodel import model
from Products.CMFCore.interfaces import IFolderish
from zope import schema
from zope.component import adapter
from zope.interface import alsoProvides, invariant, Invalid, implementer
from .utils import PrefixedFieldProperty
from . import _


class ISliderImage(model.Schema, IImage):
    """Slider slide/image content type"""

    image = NamedBlobImage(
        title=_(u'Image'),
        required=True,
    )

    content = schema.TextLine(
        title=_(u'Internal Content Link'),
        description=_(u'Select content for this slide to link to or enter an '
                      u'external link below.'),
        required=False
    )
    form.widget(
        'content',
        RelatedItemsWidget,
        pattern_options={
            'placeholder': _(u'Begin typing a title'),
        }
    )

    link = schema.URI(
        title=_(u'External Link'),
        required=False
    )

    @invariant
    def validateReferenceOrLink(data):
        if not data.content and not data.link:
            raise Invalid(_(u'You must enter either a content item or '
                            u'an external link'))


alsoProvides(ISliderImage, IFormFieldProvider)


class ISliderConfig(model.Schema):
    """Configuration for a slider folder"""

    height = schema.Int(
        title=_(u'Slider height (in px)'),
        description=_(u'Optionally constrain slider height with center crop, '
                      u'leave blank to use image height (all slides must have '
                      u'the same aspect ratio if no height is set).'),
        required=False
    )

    interval = schema.Int(
        title=_(u'Carousel interval'),
        description=_(u'Delay in ms between changing slides. Leave blank to '
                      u'never auto-cycle.'),
        required=False,
        default=5000,
    )

    pause = schema.Bool(
        title=_(u'Pause on hover?'),
        description=_(u'Should the slider auto-cycle pause when the mouse is '
                      u'hovering over it?'),
        default=True,
    )

    wrap = schema.Bool(
        title=_(u'Wrap?'),
        description=_(u'Should the slider wrap from from the last side to the '
                      u'first?'),
        default=True,
    )

    scale = schema.Choice(
        title=_(u'Image Scale'),
        description=_(u'Which image scale should this slider use?'),
        vocabulary=u'plone.app.vocabularies.ImagesScales',
        default=u'banner',
        required=True,
    )


STORAGE_PREFIX = '_tesserae_slider_'


@adapter(IFolderish)
@implementer(ISliderConfig)
class SliderConfigAdapter(object):
    """Adapter for storing config values"""
    height = PrefixedFieldProperty(ISliderConfig['height'], STORAGE_PREFIX)
    interval = PrefixedFieldProperty(ISliderConfig['interval'], STORAGE_PREFIX)
    wrap = PrefixedFieldProperty(ISliderConfig['wrap'], STORAGE_PREFIX)
    pause = PrefixedFieldProperty(ISliderConfig['pause'], STORAGE_PREFIX)
    scale = PrefixedFieldProperty(ISliderConfig['scale'], STORAGE_PREFIX)

    def __init__(self, context):
        self.context = context
