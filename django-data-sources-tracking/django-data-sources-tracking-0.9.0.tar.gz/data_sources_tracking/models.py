# -*- coding: utf-8 -*-
import hashlib
from django.contrib.contenttypes.fields import GenericRelation
from django.db import models
from django.utils.translation import ugettext_lazy as _

from model_utils.models import TimeStampedModel

from . import choices


class File(TimeStampedModel):
    """Model File that stores data relevant.

    Notes:
        - Trying to follow GA4GH data models
        (Specifically https://github.com/ga4gh/task-execution-schemas)
        - Following inputs model
    """
    content = models.FileField(upload_to='uploads/', max_length=255, blank=True)
    name = models.CharField(max_length=255)
    description = models.TextField(blank=True)
    url = models.CharField(max_length=255)
    path = models.CharField(max_length=255)
    type = models.SmallIntegerField(choices=choices.FILE_TYPES,)
    active = models.BooleanField(default=True)
    relative_path = models.BooleanField(default=True)
    comments = GenericRelation('user_activities.Comment')
    hash = models.CharField(max_length=255, unique=True, default='hash')

    class Meta:
        verbose_name = _('File')
        verbose_name_plural = _('Files')

    def __str__(self):
        return self.name

    def save(self, *args, **kwargs):
        self.hash = self.create_hash()
        super(File, self).save(*args, **kwargs)

    def create_hash(self):
        if self.content:
            md5 = hashlib.md5()
            for chunk in self.content.chunks():
                md5.update(chunk)
            return md5.hexdigest()
        else:
            return hashlib.md5(
                '|'.join(list(map(str, [self.name, self.path]))).encode('utf-8')
            ).hexdigest()

    @property
    def display_type(self):
        return self.get_type_display()
