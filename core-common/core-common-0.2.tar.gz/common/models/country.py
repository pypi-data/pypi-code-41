from django.db import models


class Country(models.Model):
    """
    Represents a Person's country in the system
    Example: Israel, Brazil
    """
    name = models.CharField('Name', max_length=70)  #: Name
    code = models.CharField('ISO Code', max_length=10, blank=True, null=True)  #: ISO Code

    class Meta:
        ordering = ['name',]
        verbose_name = "Country"
        verbose_name_plural = "Countries"

    def __str__(self):
        return self.name
