from django.db import models
from psu_base.classes.Log import Log

log = Log()


class Audit(models.Model):
    """Auditing of important events"""

    # Fields
    app_code = models.CharField(
        max_length=15,
        verbose_name='Application Code',
        help_text='Application that this audit belongs to.',
        blank=False, null=False
    )
    event_code = models.CharField(
        max_length=80,
        help_text='This string should uniquely identify the type of event',
        blank=False, null=False
    )
    username = models.CharField(
        max_length=128,
        help_text='This holds the username of the event performer, which could be a provisional email address',
        blank=False, null=False
    )
    impersonated_username = models.CharField(
        max_length=128,
        help_text='This holds the username of the impersonated user, if the user is impersonating',
        default=None, blank=True, null=True
    )
    proxied_username = models.CharField(
        max_length=128,
        help_text='This holds the username of the selected proxy, if the user is proxying',
        default=None, blank=True, null=True
    )
    previous_value = models.CharField(
        max_length=500,
        help_text='Value before change was made',
        default=None, blank=True, null=True
    )
    new_value = models.CharField(
        max_length=500,
        help_text='Value after change was made',
        default=None, blank=True, null=True
    )
    comments = models.CharField(
        max_length=500,
        help_text='Comments about the event',
        default=None, blank=True, null=True
    )
    date_created = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return f"<{self.event_code} Event: {self.username}>"
