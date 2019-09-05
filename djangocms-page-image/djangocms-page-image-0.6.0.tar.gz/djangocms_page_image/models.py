from django.db import models
from django.conf import settings

from filer.fields.image import FilerImageField

from django.utils.translation import ugettext_lazy as _

from cms.models import CMSPlugin
from cms.extensions import PageExtension
from cms.extensions.extension_pool import extension_pool

class ImageExtension(PageExtension):
    image = FilerImageField(
        verbose_name=_('image'),
        on_delete=models.SET_NULL,
        blank=True,
        null=True,
    )
    preview_image = FilerImageField(
        verbose_name=_('preview image'),
        on_delete=models.SET_NULL,
        blank=True,
        null=True,
        help_text=_('leave blank to use page image'),
        related_name='preview_image_extensions'
    )
    teaser = models.TextField(verbose_name=_('teaser'), blank=True)
    show_preview = models.BooleanField(
        verbose_name=_('show preview?'),
        default=True
    )
    extra_classes = models.CharField(verbose_name=_('extra classes'),
        max_length=512, blank=True)

    class Meta:
        verbose_name=_('Page Image and Teaser')

    def get_preview_image(self):
        return self.preview_image or self.image
extension_pool.register(ImageExtension)


class ChildPagePreviewPlugin(CMSPlugin):
    STYLE_CHOICES = getattr(
        settings,
        'DJANGOCMS_PAGE_IMAGE_CPP_STYLE_CHOICES',
        []
    )
    DEFAULT_STYLE = getattr(
        settings,
        'DJANGOCMS_PAGE_IMAGE_CPP_DEFAULT_STYLE',
        ''
    )
    style = models.CharField(
        _('style'),
        choices=STYLE_CHOICES,
        default=DEFAULT_STYLE,
        max_length=50,
        blank=True
    )

class SiblingPagePreviewPlugin(CMSPlugin):
    STYLE_CHOICES = getattr(
        settings,
        'DJANGOCMS_PAGE_IMAGE_SPP_STYLE_CHOICES',
        []
    )
    DEFAULT_STYLE = getattr(
        settings,
        'DJANGOCMS_PAGE_IMAGE_SPP_DEFAULT_STYLE',
        ''
    )
    style = models.CharField(
        _('style'),
        choices=STYLE_CHOICES,
        default=DEFAULT_STYLE,
        max_length=50,
        blank=True
    )
