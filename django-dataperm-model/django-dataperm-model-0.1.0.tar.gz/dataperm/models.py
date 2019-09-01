from django.db import models

class WithOwnerMixin(models.Model):
    owner = models.CharField(max_length=64, blank=True, verbose_name="所有人", editable=False)

    class Meta:
        abstract = True

