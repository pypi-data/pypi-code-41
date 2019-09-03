import uuid

from django.contrib.postgres.fields import JSONField
from django.contrib.auth.models import User
from django.db import models
from django.utils.encoding import python_2_unicode_compatible


@python_2_unicode_compatible
class Service(models.Model):

    """
    Base service storage model
    """
    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    name = models.CharField(max_length=50, null=False, blank=False)
    url = models.CharField(max_length=255, null=False, blank=False)
    token = models.CharField(max_length=40, null=False, blank=False)
    up = models.BooleanField(default=False)
    metadata = JSONField(null=True, blank=True)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)
    created_by = models.ForeignKey(User, related_name='services_created',
                                   null=True, on_delete=models.SET_NULL)
    updated_by = models.ForeignKey(User, related_name='services_updated',
                                   null=True, on_delete=models.SET_NULL)
    user = property(lambda self: self.created_by)

    def __str__(self):  # __unicode__ on Python 2
        return str(self.name)

    def get_last_up_time(self):
        last_up = self.service_statuses.filter(up=True).\
            order_by('-created_at').first()
        if last_up:
            return last_up.created_at


@python_2_unicode_compatible
class Status(models.Model):

    """
    Base Status model, holds results of service pings
    """
    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    service = models.ForeignKey(
        Service, related_name='service_statuses', on_delete=models.CASCADE
    )
    up = models.BooleanField(default=False)
    result = JSONField(null=True, blank=True)
    created_at = models.DateTimeField(auto_now_add=True)

    def __str__(self):  # __unicode__ on Python 2
        return str("Up status is %s at %s" % (self.up, self.created_at))


@python_2_unicode_compatible
class UserServiceToken(models.Model):

    """
    User Service Token model
    Holds seed-auth-api user tokens from seed services for CLI to use
    user_id is consistent in auth-api, email might change
    """
    service = models.ForeignKey(
        Service, related_name='service_users', on_delete=models.CASCADE
    )
    user_id = models.IntegerField(null=False, blank=False)
    email = models.CharField(max_length=30, null=False, blank=False)
    token = models.CharField(max_length=40, null=False, blank=False)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    class meta:
        unique_together = ['service', 'user_id']

    def __str__(self):  # __unicode__ on Python 2
        return str("%s for %s at %s" % (
            self.token, self.user_id, self.service))
