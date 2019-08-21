from django.utils.translation import gettext as _
from django.core.validators import URLValidator

from wagtail.core import blocks
from wagtail.images.blocks import ImageChooserBlock
from wagtail.documents.blocks import DocumentChooserBlock
from wagtail.embeds.blocks import EmbedBlock


SWISSLINUX_COLOR = '#e31d35'


class HeaderBlock(blocks.StructBlock):
    """A HTML header"""
    header_level = blocks.ChoiceBlock(
        choices=(
            ('h1', 'H1'),
            ('h2', 'H2'),
            ('h3', 'H3'),
            ('h4', 'H4'),
            ('h5', 'H5'),
            ('h6', 'H6'),
        ),
        label=_('Header level'),
    )
    text = blocks.CharBlock(
        label=_('Text'),
    )

    class Meta:
        template = 'wagtailperson/blocks/header.html'
        icon = 'title'
        label = _('Header')


class LinkBlock(blocks.StructBlock):
    """An URL with its description"""
    description = blocks.CharBlock(
        label=_('Description'),
    )
    url = blocks.URLBlock(
        label=_('URL'),
        validators=[
            URLValidator(
                [
                    'http',
                    'https',
                    'ftp',
                    'ftps',
                    'mailto',
                    'xmpp',
                    'tel',
                ]
            )
        ]
    )

    class Meta:
        template = 'wagtailperson/blocks/link.html'
        icon = 'site'
        label = _('Link')


class PersonBlock(blocks.StructBlock):
    """A person block, linked to a person page"""
    person = blocks.PageChooserBlock(
        label=_('Person page'),
        target_model='wagtailperson.PersonPage',
    )

    class Meta:
        template = 'wagtailperson/blocks/person.html'
        icon = 'user'
        label = _('Person')
