import copy

import django
from django.core.exceptions import ValidationError
from django.db import models
from django.db.models import Sum

from .order_expensecode import OrderExpenseCode
from .order_queryset import OrderQuerySet

try:
    # Django 2.0
    from django.urls import reverse
except ImportError:
    # Django 1.6
    from django.core.urlresolvers import reverse


class Order(models.Model):
    """
    Represents an Order in the system
    """

    PAYMENT_METHOD = { 'C':'Credit','CC':'Credit Card','R':'Reimbursement','PP':'Pre Payment','PD':'Per Diem' }

    order_id        = models.AutoField(primary_key=True)  #: Pk ID
    order_reqnum    = models.IntegerField('Requisition number', blank=True, null=True) #: Requisition number of an order
    order_reqdate   = models.DateField('Requisition date', blank=True, null=True) #: Requisition date of an order

    order_podate    = models.DateField('Purchase date', blank=True, null=True) #: Purchase order date of an order
    order_desc      = models.TextField('Description', blank=True, null=True, default='')  #: Description of the Order
    order_amount    = models.DecimalField('Amount (NET)', max_digits=11, decimal_places=2)    #: Amount for that order
    order_req       = models.CharField('Requester name', max_length=200) #: Name of the requester
    order_deldate   = models.DateField('Delivery date', blank=True, null=True) #: Delivery date for the order
    order_paymethod = models.CharField('Payment Method', blank=True, null=True, max_length=2, choices=PAYMENT_METHOD.items())
    order_notes     = models.TextField('Notes', blank=True, null=True)
    expected_date   = models.DateField('Expected arrival date', blank=True, null=True)

    supplier    = models.ForeignKey('suppliers.Supplier', blank=True, null=True, on_delete=models.CASCADE) #: Fk Supplier for this order
    responsible = models.ForeignKey('auth.User', blank=True, null=True, verbose_name='Responsible', on_delete=models.CASCADE) #: Fk The user that created that order
    expensecode = models.ManyToManyField('finance.ExpenseCode', through='OrderExpenseCode', blank=True)  #: Budget of the supplied product
    currency    = models.ForeignKey('common.Currency', verbose_name='Currency', on_delete=models.CASCADE)             #: Currency of a Person salary
    group       = models.ForeignKey('auth.Group', on_delete=models.CASCADE, limit_choices_to={'name__startswith': 'GROUP:'})

    objects = OrderQuerySet.as_manager()

    class Meta:
        verbose_name        = "Order"
        verbose_name_plural = "Orders"

        permissions = (
            ("view_personnel_orders", "View personnel Orders"),
            ("app_access_allorders",  "Access [All orders] app"),
            ("app_access_orders",  "Access [Orders] app"),
        )

    def __str__(self):
        return str(self.pk)

    def groups(self):
        return str(self.group)

    def order_ponum(self):
        """
        Returns a string concatenating all the PO numbers associated
        with this order.

        Note: In the future maybe it is best to return a list, and delegate
        the formatting to the end point.
        """
        try:
            vals = self.orderexpensecode_set.all().values_list('purchase_order', flat=True)
            if vals[0] is None:
                return ""
            else:
                return ' '.join( map( str, vals  ) )
        except:
            return ""
    order_ponum.short_description = 'Purchase orders'

    def expense_codes(self):
        return '\n'.join(
            [
                (
                    code.financeproject.costcenter.costcenter_code + '-' +
                    code.financeproject.financeproject_code + '-' +
                    code.expensecode_number + ': ' +
                    code.financeproject.financeproject_name
                )
                for code in self.expensecode.all()
            ]
        )

    def duplicate(self, user):

        o_copy = copy.copy(self)
        o_copy.pk = None
        o_copy.responsible  = user
        o_copy.order_reqnum = None
        o_copy.order_desc   = "********** Copied from order {parent_pk} ********* \n{description}".format(
            parent_pk=self.pk, description=self.order_desc)
        o_copy.save()

        o_copy.orderexpensecode_set.all().delete()
        # (4) copy M2M relationship: expensecode
        for ec in OrderExpenseCode.objects.filter(order=self):
            ec_copy = copy.copy(ec)
            ec_copy.pk = None
            ec_copy.order = o_copy
            ec_copy.save()

        return o_copy


    def total_amount(self):
        return self.expensecode.aggregate(Sum('orderexpensecode__orderexpensecode_amount'))['orderexpensecode__orderexpensecode_amount__sum']

    def clean(self):
        if self.payout_set.exists():
            payout = self.payout_set.first()
            print(payout.totalAmount(), self.order_amount)
            if float(payout.totalAmount())!=float(self.order_amount):
                raise ValidationError({
                    'order_amount': 'The order should have the same amount of the payout associated to it (<b>{0}</b>)'.format(payout.totalAmount()) })


    def save(self, expensecode_kwargs={}):
        super().save()

        # create the first Enpense Code inline if none exists
        if not self.orderexpensecode_set.exists():
            ec = OrderExpenseCode(
                order=self,
                orderexpensecode_amount=self.order_amount,
                **expensecode_kwargs,
            )
            ec.save()
        elif expensecode_kwargs:
            raise ValueError('expensecode_kwargs can only be used for '
                             'Orders without related Expense Codes')

    def get_absolute_url(self):
        # hack required to have both CORE versions working
        if django.VERSION > (2, 0):
            return '/app/orders/#/frontend.apps.apps.Order/?obj={order_id}'.format(order_id=self.pk)
        else:
            return reverse('admin:supplier_order_change', args=(self.pk, ))
