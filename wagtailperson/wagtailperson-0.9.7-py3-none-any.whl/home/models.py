from django.db import models

from wagtail.core.models import Page
from wagtail.core.fields import StreamField
from wagtail.core.blocks import RichTextBlock
from wagtail.admin.edit_handlers import (
    StreamFieldPanel,
)

from wagtailperson.blocks import (
    HeaderBlock,
    LinkBlock,
    PersonBlock,
)


class HomePage(Page):
    """A simple home page, to test the blocks in a StreamField"""
    body = StreamField(
        [
            ('heading', HeaderBlock()),
            ('link', LinkBlock()),
            ('person', PersonBlock()),
            ('paragraph', RichTextBlock()),
        ],
        blank=True,
    )

    content_panels = Page.content_panels + [
        StreamFieldPanel('body')
    ]

