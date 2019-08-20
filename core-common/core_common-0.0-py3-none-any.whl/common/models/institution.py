from django.db import models


class Institution(models.Model):
    name  = models.CharField(max_length=200, unique=True)
    short = models.CharField(max_length=10, blank=True)

    class Meta:
        ordering = ('name', )

    def __str__(self):
        return self.name

