
from django.db import models
from django.utils.translation import ugettext_lazy as _


class OrderStatusName(models.CharField):

    def __init__(
            self,
            verbose_name=_('Name'),
            max_length=255,
            *args, **kwargs):

        super(OrderStatusName, self).__init__(
            verbose_name=verbose_name,
            max_length=max_length,
            *args,
            **kwargs)


class OrderStatusCode(models.CharField):

    def __init__(
            self,
            verbose_name=_('Code'),
            max_length=255,
            unique=True,
            *args, **kwargs):

        super(OrderStatusCode, self).__init__(
            verbose_name=verbose_name,
            max_length=max_length,
            unique=unique,
            *args, **kwargs)


class OrderStatusDescription(models.TextField):

    def __init__(
            self,
            verbose_name=_('Description'),
            max_length=1000,
            blank=True,
            *args, **kwargs):

        super(OrderStatusDescription, self).__init__(
            verbose_name=verbose_name,
            max_length=max_length,
            blank=blank,
            *args, **kwargs)


class OrderStatusDefault(models.BooleanField):

    def __init__(
            self,
            verbose_name=_('Is default'),
            blank=True,
            default=False,
            *args, **kwargs):

        super(OrderStatusDefault, self).__init__(
            verbose_name=verbose_name,
            default=default,
            blank=blank,
            *args, **kwargs)



class OrderStatusQueryset(models.QuerySet):

    def default(self):
        return self.get(is_default=True)


class OrderStatusManager(models.Manager):

    def get_queryset(self):
        return OrderStatusQueryset(self.model, using=self._db)

    def default(self):
        return self.get_queryset().default()


class AbstractOrderStatus(models.Model):

    name = OrderStatusName()

    is_default = OrderStatusDefault()

    objects = OrderStatusManager()

    def __str__(self):
        return self.name

    class Meta:
        abstract = True
        verbose_name = _('Order status')
        verbose_name_plural = _('Order statuses')
