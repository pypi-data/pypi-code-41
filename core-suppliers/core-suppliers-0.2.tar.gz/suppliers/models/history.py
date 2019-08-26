from django.db import models


class Tophistory(models.Model):
    """
    Represents a historic time of payment of a finance in the system
    """

    top  = models.CharField('TOP', max_length=100)
    date = models.DateField('Date', blank=True, null=True)

    createdby = models.ForeignKey('auth.User', blank=True, null=True, on_delete=models.CASCADE)
    supplier  = models.ForeignKey('Supplier', blank=True, null=True, on_delete=models.CASCADE)

    class Meta:
        verbose_name = "TOP History"
        verbose_name_plural = "Top Histories"

    def __str__(self):
        return self.top
