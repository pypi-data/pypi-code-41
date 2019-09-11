import random

from django.conf import settings
from django.db import models, IntegrityError


from ...models import CreatedAtModel
from ..devices.models import Device
from .settings import (
  CODE_LENGTH,
  CODE_CHARS,
)


class PassepartoutManager(models.Manager):
    def create_passepartout(self, device, jwt):
        passepartout = self.create(
            device=device,
            jwt=jwt,
            token=Passepartout.generate_token()
        )
        try:
            passepartout.save()
        except IntegrityError:
            # Try again with other code
            passepartout = Passepartout.objects.create_passepartout(device, jwt)
        return passepartout


class Passepartout(CreatedAtModel):
    objects = PassepartoutManager()

    deleted = models.BooleanField(default=False)

    token = models.CharField(unique=True, db_index=True, max_length=36)
    jwt = models.TextField()
    device = models.ForeignKey(Device, verbose_name="device", on_delete=models.CASCADE)
    bumps = models.PositiveIntegerField(default=len(settings.DJANGO_SSO_DOMAINS)-1)

    @classmethod
    def generate_token(cls):
        return "".join(random.choice(CODE_CHARS) for i in range(CODE_LENGTH))

    class Meta:
        unique_together = ('token', 'deleted')

    def __str__(self):
        return '{0}:{1}'.format(self.id, self.device.fingerprint)
