from django.db import models
from django.core.exceptions import ValidationError

class OrderExpenseCode(models.Model):
    """
    Represents an Order Budget connection table in the system
    """
    orderexpensecode_id     = models.AutoField(primary_key=True)  #: Pk ID
    order                   = models.ForeignKey('Order', blank=True, null=True, on_delete=models.CASCADE)  #: Fk to Order model
    orderexpensecode_amount = models.DecimalField('Amount (EUR)', max_digits=11, decimal_places=2)
    purchase_order          = models.CharField('Purchase Order', max_length=14, blank=True)

    expensecode = models.ForeignKey('finance.ExpenseCode', blank=True, null=True,
                                    on_delete=models.CASCADE)  #: Fk to Budget model

    class Meta:
        verbose_name        = "Expense Code Information"
        verbose_name_plural = "Expense Codes Information"

    def __str__(self):
        if self.expensecode is not None:
            return str(self.expensecode.abbrv)
        else:
            return 'None'

    def clean_fields(self, exclude=None):
        """
        Purchase Order Field:
            formats allowed:
                XXXXX+
                ECXXXXX+
            if only the number is entered, the 'EC' code will be prepended
        """
        super().clean_fields(exclude=exclude)

        po_letter_code = 'EC'
        po_number = ''

        if self.purchase_order == '':
            # blank field
            return
        elif self.purchase_order.startswith(po_letter_code):
            po_number = self.purchase_order[2:]
        else:
            po_number = self.purchase_order
            self.purchase_order = po_letter_code + self.purchase_order

        if len(po_number) < 5 or not po_number.isdigit():
            raise ValidationError({'purchase_order': 'Invalid number'})