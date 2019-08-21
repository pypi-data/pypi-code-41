from django.db import models
from django.utils.translation import gettext as _
from django.utils.text import slugify

from modelcluster.fields import ParentalKey

from wagtail.core.models import Page, Orderable
from wagtail.core.fields import RichTextField, StreamField
from wagtail.snippets.models import register_snippet
from wagtail.admin.edit_handlers import (
    FieldPanel,
    InlinePanel,
    StreamFieldPanel,
)
from wagtail.images.edit_handlers import ImageChooserPanel
from wagtail.core import blocks
from wagtail.images.blocks import ImageChooserBlock
from wagtail.documents.blocks import DocumentChooserBlock
from wagtail.embeds.blocks import EmbedBlock

from wagtailperson.blocks import (
    HeaderBlock,
    LinkBlock,
)


class PersonPage(Page):
    """A person"""
    picture = models.ForeignKey(
        'wagtailimages.Image',
        blank=True,
        null=True,
        on_delete=models.SET_NULL,
        related_name='+',
        verbose_name=_('Picture'),
    )
    name = models.CharField(
        verbose_name=_('Name'),
        max_length=250,
    )
    custom_titles = models.CharField(
        verbose_name=_('Custom titles'),
        max_length=250,
        blank=True,
        help_text=_('Some custom titles, separated by commas'),
    )
    intro = models.CharField(
        verbose_name=_('Introduction'),
        max_length=250,
        blank=True,
        help_text=_('Shown on the short descriptions'),
    )
    abstract = RichTextField(
        blank=True,
        verbose_name=_('Abstract'),
    )
    extra_infos = StreamField(
        [
            ('heading', HeaderBlock()),
            ('link', LinkBlock()),
            ('paragraph', blocks.RichTextBlock()),
            ('quote', blocks.BlockQuoteBlock()),
            ('image', ImageChooserBlock()),
            ('document', DocumentChooserBlock()),
            ('embed', EmbedBlock()),
        ],
        blank=True,
        verbose_name=_('Extra informations'),
    )

    # Editor panels configuration
    content_panels = [
        FieldPanel('name'),
        ImageChooserPanel('picture'),
        InlinePanel('titles', label=_('Titles')),
        FieldPanel('custom_titles'),
        FieldPanel('intro'),
        FieldPanel('abstract'),
        StreamFieldPanel('extra_infos'),
    ]

    class Meta:
        verbose_name = _('Person')
        verbose_name_plural = _('Persons')
        ordering = ['name']

    def __str__(self):
        return self.name

    def save(self, *args, **kwargs):
        """Override save to populate title and slug"""
        self.title = self.name
        if not self.slug:
            self.slug = slugify(self.name, allow_unicode=True)
        return super(PersonPage, self).save(*args, **kwargs)

    def custom_titles_list(self):
        """Get custom titles, in form of a list of strings"""
        if not self.custom_titles:
            return []
        return self.custom_titles.split(',')


@register_snippet
class PersonTitle(models.Model):
    """The title of a person"""
    title = models.CharField(
        verbose_name=_('Title'),
        max_length=250,
    )

    class Meta:
        verbose_name = _('Person title')
        verbose_name_plural = _('Person titles')
        ordering = ['title']

    def __str__(self):
        return self.title


class PersonTitlePage(Orderable):
    """A many-to-many retation between PensonPage and PersonTitle"""
    page = ParentalKey(
        PersonPage,
        related_name='titles',
    )
    title = models.ForeignKey(
        PersonTitle,
        on_delete=models.CASCADE,
        related_name='+',
    )

    panels = [
        FieldPanel('title'),
    ]

    class Meta:
        verbose_name = _('Person Title Page')
        verbose_name_plural = _('Person Title Pages')

    def __str__(self):
        return self.title.title


class PersonIndexPage(Page):
    """An index page of person children pages"""
    intro = RichTextField(
        blank=True,
        verbose_name=_('Intro'),
    )

    content_panels = Page.content_panels + [
        FieldPanel('intro', classname='full'),
    ]

    subpage_types = ['wagtailperson.PersonPage']

    class Meta:
        verbose_name = _('Person Index Page')
        verbose_name_plural = _('Person Index Pages')

    def __str__(self):
        return self.title

    def get_context(self, request):
        """Overloud the context with published person pages, ordered by
        name"""
        context = super(PersonIndexPage, self).get_context(request)
        person_pages = sorted(
            (
                page.specific
                for page
                in self.get_children().live()
            ),
            key=lambda person: person.name
        )
        context['person_pages'] = person_pages
        return context
