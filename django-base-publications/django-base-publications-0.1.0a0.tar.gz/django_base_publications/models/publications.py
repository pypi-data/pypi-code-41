import uuid
from datetime import datetime

from django.db.models import (
    Model,
    BooleanField,
    CharField,
    TextField,
    DateTimeField,
    ForeignKey,
    UUIDField,
    CASCADE,
)
from django.utils.translation import gettext_lazy as _
from django.conf import settings
from autoslug.fields import AutoSlugField
from taggit.managers import TaggableManager


from ..utils import get_item_absolute_site_url
from .managers import BasePublicationManager
from .statuses import Statuses


class BasePublication(Model):
    title = CharField(
        max_length=512,
        verbose_name=_('Title'),
    )
    slug = AutoSlugField(
        db_index=True,
        blank=True,
        unique=True,
        verbose_name=_('Slug'),
    )
    description = TextField(
        verbose_name=_('Description'),
        blank=True,
        null=True,
    )
    status = CharField(
        max_length=255,
        choices=Statuses,
        default=Statuses.DRAFT.value,
        db_index=True,
        verbose_name=_('Status'),
    )
    owner = ForeignKey(
        settings.AUTH_USER_MODEL,
        on_delete=CASCADE,
        blank=True,
        verbose_name=_('Owner'),
    )
    publication_date = DateTimeField(
        default=datetime.now,
        db_index=True,
        verbose_name=_('Publication date'),
    )
    created_date = DateTimeField(
        auto_now_add=True,
        editable=False,
        verbose_name=_('Created date'),
    )
    last_modified_date = DateTimeField(
        auto_now=True,
        editable=False,
        verbose_name=_('Last modified date'),
    )
    is_hidden = BooleanField(
        default=False,
        db_index=True,
        verbose_name=_('Is hidden'),
    )
    token = UUIDField(
        default=uuid.uuid4,
        blank=True,
        editable=False,
        verbose_name='Токен'
    )

    tags = TaggableManager()
    objects = BasePublicationManager()

    @property
    def canonical_url(self):
        return get_item_absolute_site_url(self.get_absolute_url())

    @property
    def is_published(self):
        return self.status == Statuses.PUBLISHED.value

    def get_absolute_url(self):
        raise NotImplementedError('get_absolute_url not implemented')

    class Meta:
        abstract = True
        ordering = [
            '-publication_date',
        ]

