from django.db import models
from .costcenter_queryset import CostCenterQuerySet


class CostCenter(models.Model):
    """
    Represents a Finance cost center in the system
    Example: CCU
    """
    name       = models.CharField('Name', max_length=200)  #: Name
    code       = models.CharField('Code', max_length=200)  #: Code
    start_date = models.DateField(null=True, blank=True)
    end_date   = models.DateField(null=True, blank=True)

    group      = models.ForeignKey('people.Group', verbose_name='Group', blank=False, null=False, on_delete=models.CASCADE)

    objects = CostCenterQuerySet.as_manager()

    class Meta:
        ordering            = ['code',]
        verbose_name        = "Finance Cost Center"
        verbose_name_plural = "Finance Cost Centers"

    def __str__(self):
        return "{0} - {1}".format(self.code, self.name)
