from django.db import models

try:
    from django.urls import reverse
except ImportError:
    from django.core.urlresolvers import reverse


class Budget(models.Model):
    """
    Represents a Budgets in the system
    """

    amount = models.DecimalField('Amount (NET)', max_digits=11, decimal_places=2)
    year   = models.IntegerField('Year', blank=True, null=True)

    expensecode = models.ForeignKey('ExpenseCode', verbose_name='Expense Code', on_delete=models.CASCADE)

    class Meta:
        verbose_name = "Budget"
        verbose_name_plural = "Budgets"
        unique_together = ( ('year','expensecode'),)

    def __str__(self):
        return self.amount
