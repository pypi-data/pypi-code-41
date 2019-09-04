from django.db import models

from .conf import settings
from .tasks import CampaignSubscribeTask


class Campaign(models.Model):

    campaign_id = models.CharField(max_length=255)
    status = models.CharField(
        max_length=1,
        default=settings.REFERRAL_CAMPAIGN_STATUS_DEFAULT,
        choices=settings.REFERRAL_CAMPAIGN_STATUS_CHOICES,
    )
    name = models.CharField(max_length=255)
    users = models.ManyToManyField(
        settings.AUTH_USER_MODEL,
        related_name='referrals',
        verbose_name='user',
        blank=True,
    )

    def __str__(self):
        return '{} [ {} ]'.format(self.name, self.campaign_id)

    @property
    def total_users(self):
        return self.users.count()

    def subscribe(self, user_from, rh, conversion):
        data = {
            'campaign_id': self.campaign_id,
            'firstName': user_from.first_name,
            'lastName': user_from.last_name,
            'email': user_from.email,
            'rh': rh,
        }

        if conversion:
            data['conversionName'] = settings.REFERRAL_CONVERSION_NAME

        CampaignSubscribeTask().s(**data).apply_async()
