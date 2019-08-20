# -*- coding: utf-8 -*-
from __future__ import unicode_literals

import six

from django.db import models
from django.utils.translation import ugettext_lazy as _
from django_fsm import FSMField, transition

from jsonfield import JSONField

from knpay_plugin.conf import config
from knpay_plugin.data import COUNTRIES
from knpay_plugin.fields import MonitorField


class PaymentTransactionQuerySet(models.QuerySet):
    def created(self):
        return self.filter(status=PaymentTransaction.CREATED)

    def completed(self):
        return self.filter(models.Q(status=PaymentTransaction.PAID) |
                           models.Q(status=PaymentTransaction.CANCELED)|
                           models.Q(status=PaymentTransaction.FAILED)
                           )


@six.python_2_unicode_compatible
class PaymentTransaction(models.Model):
    ENGLISH, ARABIC = 'en', 'ar'
    LANGUAGE_CHOICES = (
        (ENGLISH, _("English")),
        (ARABIC, _("Arabic"))
    )
    CREATED, CANCELED, PAID, FAILED, ERROR = 'created', 'canceled', 'paid', 'failed', 'error'
    STATUS_CHOICES = (
        (CREATED, _("Created")),
        (CANCELED, _("Canceled")),
        (PAID, _("Paid")),
        (FAILED, _("Failed")),
        (ERROR, _("Error")),
    )
    COUNTRY_CHOICES = [(code, name) for code, name in six.iteritems(COUNTRIES)]
    created = models.DateTimeField(_("Created"), auto_now=True)
    status = FSMField(_("Status"), default=CREATED, db_index=True,
                      choices=STATUS_CHOICES, protected=True)
    gateway_code = models.CharField(
        _("Gateway code"), max_length=16, db_index=True, default='', choices=config.GATEWAY_CHOICES)
    amount = models.CharField(
        _("Amount"), max_length=24)
    language = models.CharField(
        _("Language"), max_length=2, choices=LANGUAGE_CHOICES,
        default=ENGLISH)
    currency_code = models.CharField(
        _("Currency code"), max_length=3)
    order_no = models.CharField(
        _("Order no"), db_index=True,
        max_length=128, unique=True)
    customer_first_name = models.CharField(
        _("Customer first name"), max_length=64,
        default='', blank=True)
    customer_last_name = models.CharField(
        _("Customer last name"), max_length=64,
        default='', blank=True)
    customer_email = models.CharField(
        _("Customer email"), max_length=128,
        default='', blank=True)
    customer_phone = models.CharField(
        _("Customer phone"), max_length=16,
        default='', blank=True)
    customer_address_line1 = models.TextField(
        _("Customer address line 1"),
        default='', blank=True)
    customer_address_line2 = models.TextField(
        _("Customer address line 2"),
        default='', blank=True)
    customer_address_city = models.CharField(
        _("Customer address city"), default='',
        max_length=40, blank=True)
    customer_address_state = models.CharField(
        _("Customer address state"), default='',
        max_length=40, blank=True)
    customer_address_country = models.CharField(
        _("Customer address country"), default='',
        choices=COUNTRY_CHOICES,
        max_length=2, blank=True)
    customer_address_postal_code = models.CharField(
        _("Customer address postal code"),
        default='', blank=True, max_length=12)
    extra = JSONField(_("Extra"), default={}, blank=True, null=False)
    payment_url = models.URLField(_("Payment URL"), blank=True)
    knpay_response = JSONField(
        verbose_name=_("KNPay response"), default={}, blank=True)
    status_changed_at = MonitorField(monitor='status')
    # below field has to be marked as True when the object is queried
    # for the very first time, usually in completed view, when knpay
    # redirects the customer back. The purpose of is to be able
    # to place order send confirmation emails, etc. on GET and not on
    # POST, since POST is server2server and no sessions is available,
    # when in GET it is.

    is_consumed = models.BooleanField(
        _("Is consumed?"), default=False,
        help_text=_("Designates if knpay response was processed or not")
    )
    objects = PaymentTransactionQuerySet.as_manager()

    def __str__(self):
        return six.text_type(self.order_no)

    class Meta:
        verbose_name = _("Payment Transaction")
        verbose_name_plural = _("Payment Transactions")
        ordering = ('created',)
        get_latest_by = 'created'

    @transition(field='status', source=CREATED, target=CANCELED)
    def cancel(self, knpay_payload):
        self.knpay_response = knpay_payload

    @transition(field='status', source=CREATED, target=PAID)
    def acknowledge_payment(self, knpay_payload):
        self.knpay_response = knpay_payload

    @transition(field='status', source=CREATED, target=FAILED)
    def fail(self, knpay_payload):
        self.knpay_response = knpay_payload

    def is_paid(self):
        return self.status == PaymentTransaction.PAID

    def consume(self):
        self.is_consumed = True
        self.save()

    @property
    def gateway_response(self):
        try:
            return self.knpay_response['gateway_response']
        except KeyError:
            return {}

    def is_knet(self):
        return self.knpay_response.get('gateway_name') == 'knet'

    def is_migs(self):
        return self.knpay_response.get('gateway_name') == 'migs'

    def is_cybersource(self):
        return self.knpay_response.get('gateway_name') == 'cybersource'

    def is_paypal(self):
        return self.knpay_response.get('gateway_name') == 'paypal'

    def is_mpgs(self):
        return self.knpay_response.get('gateway_name') == 'mpgs'

    def is_kpay(self):
        return self.knpay_response.get('gateway_name') == 'kpay'

