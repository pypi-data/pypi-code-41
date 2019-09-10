import logging

from django.conf import settings
from django.db import models
from django.db.models.signals import pre_delete
from django.dispatch import receiver

from ..api_gateway.functions import delete_consumer_jwt
from ...models import CreatedAtModel


logger = logging.getLogger('devices')


class Device(CreatedAtModel):
    # deleting deletes jwt by delete_device_jwt signal!

    user = models.ForeignKey(
        'users.User',
        on_delete=models.CASCADE,
        related_name="devices"
    )

    fingerprint = models.CharField(max_length=32)
    user_agent = models.CharField(max_length=32, null=True, blank=True)

    apigw_jwt_id = models.CharField(max_length=36, null=True, blank=True)
    apigw_jwt_key = models.CharField(max_length=32, null=True, blank=True)
    apigw_jwt_secret = models.CharField(max_length=32, null=True, blank=True)

    def __str__(self):
      return '{}:{}'.format(self.id, self.fingerprint)


# signals

@receiver(pre_delete, sender=Device)
def delete_device_jwt(sender, instance, **kwargs):
    logger.info('Deleting apigw JWT for Device {0}, jwt_id: {1}'.format(instance, instance.apigw_jwt_id))
    if not settings.TESTING_MODE:
        status_code, r1 = delete_consumer_jwt(instance.user, instance.apigw_jwt_id)
        logger.info('Kong JWT deleted ({0}), {1}'.format(status_code, r1))
        if status_code >= 300:
            if status_code != 404:
                # delete_apigw_consumer(username)
                logger.error('Error ({0}) Deleting apigw JWT for Device {1}, {2}'.format(status_code, instance, r1))
                raise Exception(
                    "Error deleting apigw consumer jwt, {}".format(status_code))
