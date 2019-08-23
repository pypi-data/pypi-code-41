from django.db import models

class FinancingAgency(models.Model):
    """
    Represents a Grant grantor in the system
    Example: Bial, FCT
    """

    name = models.CharField('Name', max_length=200)  #: Name

    class Meta:
        verbose_name = "Financing agency"
        verbose_name_plural = "Financing agencies"
        ordering = ['name']

    def __str__(self):
        return self.name