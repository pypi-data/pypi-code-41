
from django.db import models
from django.conf import settings
from django.utils.translation import ugettext_lazy as _


class OrderUser(models.ForeignKey):

    def __init__(
            self,
            to=settings.AUTH_USER_MODEL,
            verbose_name=_('Customer'),
            related_name='orders',
            on_delete=models.SET_NULL,
            null=True,
            blank=True,
            *args, **kwargs):

        super(OrderUser, self).__init__(
            to,
            verbose_name=verbose_name,
            related_name=related_name,
            on_delete=on_delete,
            null=null,
            blank=blank,
            *args, **kwargs)


class OrderPaymentMethod(models.ForeignKey):

    def __init__(
            self,
            to='orders.PaymentMethod',
            verbose_name=_('Payment method'),
            related_name='orders',
            on_delete=models.CASCADE,
            *args, **kwargs):

        super(OrderPaymentMethod, self).__init__(
            to,
            verbose_name=verbose_name,
            related_name=related_name,
            on_delete=on_delete,
            *args, **kwargs)


class OrderStatus(models.ForeignKey):

    def __init__(
            self,
            to='orders.OrderStatus',
            verbose_name=_('Order status'),
            related_name='orders',
            on_delete=models.CASCADE,
            *args, **kwargs):

        super(OrderStatus, self).__init__(
            to,
            verbose_name=verbose_name,
            related_name=related_name,
            on_delete=on_delete,
            *args, **kwargs)


class OrderDeliveryMethod(models.ForeignKey):

    def __init__(
            self,
            to='orders.DeliveryMethod',
            verbose_name=_('Delivery method'),
            related_name='orders',
            on_delete=models.CASCADE,
            *args, **kwargs):

        super(OrderDeliveryMethod, self).__init__(
            to,
            verbose_name=verbose_name,
            related_name=related_name,
            on_delete=on_delete,
            *args, **kwargs)


class OrderFirstName(models.CharField):

    def __init__(
            self,
            verbose_name=_('First name'),
            max_length=255,
            *args, **kwargs):

        super(OrderFirstName, self).__init__(
            verbose_name=verbose_name,
            max_length=max_length,
            *args, **kwargs)


class OrderLastName(models.CharField):

    def __init__(
            self,
            verbose_name=_('Last name'),
            max_length=255,
            *args, **kwargs):

        super(OrderLastName, self).__init__(
            verbose_name=verbose_name,
            max_length=max_length,
            *args, **kwargs)


class OrderMiddleName(models.CharField):

    def __init__(
            self,
            verbose_name=_('Middle name'),
            max_length=255,
            blank=True,
            *args, **kwargs):

        super(OrderMiddleName, self).__init__(
            verbose_name=verbose_name,
            max_length=max_length,
            blank=blank,
            *args, **kwargs)


class OrderAddress(models.CharField):

    def __init__(
            self,
            verbose_name=_('Address'),
            max_length=255,
            blank=True,
            *args, **kwargs):

        super(OrderAddress, self).__init__(
            verbose_name=verbose_name,
            max_length=max_length,
            blank=blank,
            *args, **kwargs)


class OrderMobile(models.CharField):

    def __init__(
            self,
            verbose_name=_('Mobile number'),
            max_length=255,
            *args, **kwargs):

        super(OrderMobile, self).__init__(
            verbose_name=verbose_name,
            max_length=max_length,
            *args, **kwargs)


class OrderEmail(models.EmailField):

    def __init__(
            self,
            verbose_name=_('Email'),
            max_length=255,
            blank=True,
            *args, **kwargs):

        super(OrderEmail, self).__init__(
            verbose_name=verbose_name,
            max_length=max_length,
            blank=blank,
            *args, **kwargs)


class OrderCreationDate(models.DateTimeField):

    def __init__(
            self,
            verbose_name=_('Date created'),
            auto_now_add=True,
            editable=False,
            *args, **kwargs):

        super(OrderCreationDate, self).__init__(
            verbose_name=verbose_name,
            auto_now_add=auto_now_add,
            editable=editable,
            *args, **kwargs)


class OrderComment(models.TextField):

    def __init__(
            self,
            verbose_name=_('Comment'),
            max_length=1000,
            blank=True,
            *args, **kwargs):

        super(OrderComment, self).__init__(
            verbose_name=verbose_name,
            max_length=max_length,
            blank=blank,
            *args, **kwargs)
