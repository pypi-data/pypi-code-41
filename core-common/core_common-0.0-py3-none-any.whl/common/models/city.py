from django.db import models


class City(models.Model):
    """
    Represents a Person's City in the system
    Example: Lisboa, Porto
    """
    name = models.CharField('Name', max_length=70)
    country = models.ForeignKey('Country', on_delete=models.CASCADE)

    class Meta:
        ordering = ['name',]
        verbose_name = "City"
        verbose_name_plural = "Cities"

    def __str__(self):
        return self.name
