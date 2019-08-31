from django.db import models
from hashlib import md5
from . import settings


class Tag(models.Model):
    recipient = models.EmailField(max_length=255)
    tag = models.CharField(max_length=36)
    hash = models.CharField(max_length=36)
    description = models.CharField(max_length=100, null=True, blank=True)
    unsubscribed = models.BooleanField(default=False)

    def __str__(self):
        return self.description or self.tag

    def save(self, *args, **kwargs):
        if not self.hash:
            self.hash = md5(
                (
                    '%s:%s' % (
                        self.tag,
                        self.recipient
                    )
                ).encode('utf-8')
            ).hexdigest()

        super().save(*args, **kwargs)

    def get_unsubscribe_url(self):
        return 'https://%s/email-tag/%s/unsubscribe/' % (
            settings.MANAGEMENT_DOMAIN,
            self.hash
        )

    class Meta:
        unique_together = ('tag', 'recipient')
