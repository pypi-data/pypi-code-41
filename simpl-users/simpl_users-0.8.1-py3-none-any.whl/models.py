# -*- coding: utf-8 -*-
from __future__ import unicode_literals, absolute_import

from django.contrib.postgres.fields import JSONField
from django.urls import reverse
from django.db import models

from cuser.models import AbstractCUser


class User(AbstractCUser):
    external_id = models.CharField(max_length=50, blank=True, null=True)
    data = JSONField(blank=True, null=True)

    # for "GIST Python Django" Compatability
    subscriber_code = models.CharField('Subscriber Code', max_length=255, blank=True)

    # for django-courses compatibility
    faculty = models.BooleanField(default=False, db_index=True)

    def get_absolute_url(self):
        return reverse('simpl_users_api:user-detail', kwargs={'id': self.pk})

    def webhook_payload(self):
        return {
            'id': self.id,
            'email': self.email,
            'first_name': self.first_name,
            'last_name': self.last_name,
        }
