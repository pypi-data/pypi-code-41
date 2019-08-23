from django.db import models


class Degree(models.Model):
    """
    Academic degree: MSc, PhD, MD, ...
    """
    name = models.CharField('Degree', max_length=200)

    class Meta:
        ordering = ['name',]
        verbose_name = "Degree"
        verbose_name_plural = "Degrees"

    def __str__(self):
        return self.name
