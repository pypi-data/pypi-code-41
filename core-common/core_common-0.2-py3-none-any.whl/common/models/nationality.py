from django.db import models


class Nationality(models.Model):
    """
    Represents a Grant nationality in the system
    Example: USA, Portugal
    """
    name = models.CharField('Nationality', max_length=200)  #: Name

    class Meta:
        ordering = ('name',)
        verbose_name = "Nationality"
        verbose_name_plural = "Nationalities"

    def __str__(self):
        return self.name
