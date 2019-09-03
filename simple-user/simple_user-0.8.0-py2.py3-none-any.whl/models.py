# -*- coding: utf-8 -*-
import uuid

from django.db import models
from django.utils import timezone
from django.contrib.auth.models import AbstractBaseUser, PermissionsMixin

from . import settings  # noqa
from .manager import SimpleUserManager


class UserUUID(
        PermissionsMixin,
        AbstractBaseUser):

    uuid = models.UUIDField(
        default=uuid.uuid4,
        editable=False,
        unique=True)
    is_active = models.BooleanField(default=True)
    is_staff = models.BooleanField(default=False)
    is_superuser = models.BooleanField(default=False)
    date_joined = models.DateTimeField(
        default=timezone.now)

    USERNAME_FIELD = 'uuid'
    REQUIRED_FIELDS = []

    objects = SimpleUserManager()

    def __str__(self):
        return str(self.uuid)
