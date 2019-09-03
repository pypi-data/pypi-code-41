from __future__ import unicode_literals

from django.db import models
from django.utils.encoding import python_2_unicode_compatible


@python_2_unicode_compatible
class AuditLog(models.Model):
    CREATE = 'c'
    UPDATE = 'u'
    DELETE = 'd'

    ACTION_CHOICES = (
        (CREATE, "Create"),
        (UPDATE, "Update"),
        (DELETE, "Delete")
    )

    action_at = models.DateTimeField(auto_now_add=True)
    action_by = models.IntegerField(null=False, blank=False)
    action = models.CharField(max_length=10, null=False, blank=False,
                              choices=ACTION_CHOICES)
    model = models.CharField(max_length=100, null=False, blank=False)
    identity_id = models.UUIDField()
    subscription_id = models.UUIDField(null=True)
    detail = models.TextField(null=True)

    def __str__(self):
        return '{}: {} - {}'.format(
            str(self.action_at), self.action.get_display_name(),
            self.action_by.username)
