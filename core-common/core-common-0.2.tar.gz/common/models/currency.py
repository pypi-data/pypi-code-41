from django.db import models


class Currency(models.Model):
    """
    Represents a Person's salry Currency in the system
    Example: Euro, Dolar
    """
    name = models.CharField('Name', max_length=70) #: Name
    symbol = models.CharField('Symbol', max_length=100, blank=True, null=True)

    class Meta:
        ordering = ['name',]
        verbose_name = "Currency"
        verbose_name_plural = "Currencies"

    def __str__(self):
        return self.name
