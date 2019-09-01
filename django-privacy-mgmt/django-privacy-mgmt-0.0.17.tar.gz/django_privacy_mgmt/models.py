# -*- coding: utf-8 -*-
from django.contrib.sites.models import Site
from django.db import models
from django.utils.translation import ugettext_lazy as _

from parler.models import TranslatableModel, TranslatedFields


TRACKING_ITEM_CHOICE_ESSENTIALS = 'ESSENTIAL'
TRACKING_ITEM_CHOICE_STATISTICS = 'STATISTICS'
TRACKING_ITEM_CHOICE_MARKETING = 'MARKETING'

TRACKING_ITEM_CHOICES = (
    (TRACKING_ITEM_CHOICE_ESSENTIALS, 'Essential'),
    (TRACKING_ITEM_CHOICE_STATISTICS, 'Statistics'),
    (TRACKING_ITEM_CHOICE_MARKETING, 'Marketing'),
)


class TrackingItem(TranslatableModel):
    translations = TranslatedFields(
        name=models.CharField(_('Name'), max_length=1024),
    )

    category = models.CharField(
        default=TRACKING_ITEM_CHOICE_ESSENTIALS,
        choices=TRACKING_ITEM_CHOICES,
        max_length=1024,
        null=False,
        blank=False,
    )

    ordering = models.IntegerField(_('Ordering'), default=0)
    # needs to be optional for x-site entries
    site = models.ManyToManyField(
        Site,
        blank=True,
    )

    def __unicode__(self):
        return self.name

    class Meta:
        ordering = ('ordering',)

