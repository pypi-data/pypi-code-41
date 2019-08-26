from django.db import models


class Citizenship(models.Model):
    """
    Represents a Person's Citizenship in the system
    Example: American, British
    """
    name = models.CharField('Name', max_length=70)

    class Meta:
        ordering = ['name',]
        verbose_name = "Citizenship"
        verbose_name_plural = "Citizenships"

    def __str__(self):
        return self.name
