
from django.db import models
from django.utils.translation import ugettext_lazy as _


class PaymentMethodName(models.CharField):

    def __init__(
            self,
            verbose_name=_('Name'),
            max_length=255,
            *args, **kwargs):

        super(PaymentMethodName, self).__init__(
            verbose_name=verbose_name,
            max_length=max_length,
            *args,
            **kwargs)


class PaymentMethodCode(models.CharField):

    def __init__(
            self,
            verbose_name=_('Code'),
            max_length=255,
            unique=True,
            *args, **kwargs):

        super(PaymentMethodCode, self).__init__(
            verbose_name=verbose_name,
            max_length=max_length,
            unique=unique,
            *args, **kwargs)


class PaymentMethodDescription(models.TextField):

    def __init__(
            self,
            verbose_name=_('Description'),
            max_length=1000,
            blank=True,
            *args, **kwargs):

        super(PaymentMethodDescription, self).__init__(
            verbose_name=verbose_name,
            max_length=max_length,
            blank=blank,
            *args, **kwargs)


class AbstractPaymentMethod(models.Model):

    name = PaymentMethodName()

    def __str__(self):
        return self.name

    class Meta:
        abstract = True
        verbose_name = _('Payment method')
        verbose_name_plural = _('Payment methods')
