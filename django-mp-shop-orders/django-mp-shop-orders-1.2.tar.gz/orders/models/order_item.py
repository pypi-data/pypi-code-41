
from django.db import models
from django.utils.translation import ugettext_lazy as _
from django.core.validators import MinValueValidator


class ItemOrder(models.ForeignKey):

    def __init__(
            self,
            to='orders.Order',
            verbose_name=_('Order'),
            related_name='items',
            on_delete=models.CASCADE,
            *args, **kwargs):

        super(ItemOrder, self).__init__(
            to,
            verbose_name=verbose_name,
            related_name=related_name,
            on_delete=on_delete,
            *args, **kwargs)


class OrderItemProduct(models.ForeignKey):

    def __init__(
            self,
            to='products.Product',
            verbose_name=_('Product'),
            related_name='order_items',
            on_delete=models.CASCADE,
            *args, **kwargs):

        super(OrderItemProduct, self).__init__(
            to,
            verbose_name=verbose_name,
            related_name=related_name,
            on_delete=on_delete,
            *args, **kwargs)


class OrderItemQty(models.PositiveIntegerField):

    def __init__(
            self,
            verbose_name=_('Quantity'),
            default=1,
            validators=[MinValueValidator(1)],
            *args, **kwargs):

        super(OrderItemQty, self).__init__(
            verbose_name=verbose_name,
            default=default,
            validators=validators,
            *args, **kwargs)


class OrderItemComment(models.TextField):

    def __init__(
            self,
            verbose_name=_('Comment'),
            max_length=1000,
            blank=True,
            *args, **kwargs):

        super(OrderItemComment, self).__init__(
            verbose_name=verbose_name,
            max_length=max_length,
            blank=blank,
            *args, **kwargs)


class AbstractOrderItem(models.Model):

    order = ItemOrder()

    product = OrderItemProduct()

    class Meta:
        abstract = True
        verbose_name = _('Ordered product')
        verbose_name_plural = _('Ordered products')
