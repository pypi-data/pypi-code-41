
from django.db import models
from django.utils.translation import ugettext_lazy as _


class DeliveryMethodName(models.CharField):

    def __init__(
            self,
            verbose_name=_('Name'),
            max_length=255,
            *args, **kwargs):

        super(DeliveryMethodName, self).__init__(
            verbose_name=verbose_name,
            max_length=max_length,
            *args,
            **kwargs)


class DeliveryMethodCode(models.CharField):

    def __init__(
            self,
            verbose_name=_('Code'),
            max_length=255,
            unique=True,
            *args, **kwargs):

        super(DeliveryMethodCode, self).__init__(
            verbose_name=verbose_name,
            max_length=max_length,
            unique=unique,
            *args, **kwargs)


class DeliveryMethodDescription(models.TextField):

    def __init__(
            self,
            verbose_name=_('Description'),
            max_length=1000,
            blank=True,
            *args, **kwargs):

        super(DeliveryMethodDescription, self).__init__(
            verbose_name=verbose_name,
            max_length=max_length,
            blank=blank,
            *args, **kwargs)


class AbstractDeliveryMethod(models.Model):

    name = DeliveryMethodName()

    def __str__(self):
        return self.name

    class Meta:
        abstract = True
        verbose_name = _('Delivery method')
        verbose_name_plural = _('Delivery methods')
