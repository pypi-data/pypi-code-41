from django.db import models


class AeMetaModelMixin(models.Model):
    class Meta:
        abstract = True
