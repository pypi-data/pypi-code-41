# -*- coding: utf-8 -*-

from __future__ import unicode_literals

import importlib
import warnings

try:
    from urlparse import urljoin
except ImportError:
    from urllib.parse import urljoin

from appconf import AppConf
from django.utils.translation import ugettext_lazy as _


class KnpayPluginConf(AppConf):
    # currency
    DEFAULT_CURRENCY = 'KWD'

    # gateway (override at your own choice)
    GATEWAY_CHOICES = (
        ('knet', _('Knet')),
        ('cybersource', _('Credit Card')),
        ('migs', _('Credit Card')),
        ('paypal', _('Paypal')),
        ('mpgs', _('Credit Card')),
    )

    # knpay url
    BASE_URL = 'https://dev.knpay.net/'

    def get_knpay_url(self, is_payment_request):
        path = '/pos/%scrt/' % ('d/' if is_payment_request else '')
        return urljoin(self.BASE_URL, path)

    # admin
    ADMIN_SHOW_OPTIONAL_FIELDS = False
    ADMIN_SHOW_EXTRA_FIELD = False

    # urls
    DISCLOSURE_VIEW_NAME = 'kp_disclosure'
    REDIRECTED_VIEW_NAME = 'kp_complete'
    PROTOCOL = 'https'
    COMPLETE_VIEWS_REGEX = '(?P<order_no>[0-9A-Za-z_\-]+)'

    # form
    MANDATORY_FORM_FIELDS = ('amount', 'currency_code')
    VISIBLE_FORM_FIELDS = []

    # define if the payment form shall be rendered on the page
    RENDER_FORM = False

    # order generator function
    # make sure the function returns url safe order
    # and it's unique for each request to knpay
    GENERATE_ORDER_FUNC = 'knpay_plugin.forms.uuid_url64'

    def generate_order_no(self, payment_transaction=None):
        mod_name, func_name = self.GENERATE_ORDER_FUNC.rsplit('.', 1)
        mod = importlib.import_module(mod_name)
        func = getattr(mod, func_name)
        return func(payment_transaction=payment_transaction)

    # if the automatic generated order number shall be displayed on the
    # confirmation page
    SHOW_ORDER_NO = False

    # template
    VAR_MAPPING = [
        # knet
        ('result', _("Result")),
        ('trackid', _("Track ID")),
        ('postdate', _("Post Date")),
        ('tranid', _("Transaction ID")),
        ('paymentid', _("Payment ID")),
        ('auth', _("Auth ID")),
        ('ref', _("Reference ID")),

        # CS
        ('decision', _("Decision")),
        ('transaction_id', _("Transaction ID")),

        # MiGS
        ('vpc_Message', _("Message")),
        ('vpc_ReceiptNo', _("Receipt No")),
        ('vpc_TransactionNo', _("Transaction No")),
    ]

    GATEWAY_NAMES = {
        'migs': _("MiGS"),
        'knet': _("Knet"),
        'mpgs': _("MPGS"),
        'paypal': _("PayPal"),
        'cybersource': _("CyberSource")
    }

    def __getattribute__(self, name):
        if name == 'GATEWAY_CHOICES':
            warnings.warn("Please use `from knpay_plugin.conf import config; config.get_gateway_choices()`",
                          FutureWarning)
            return self.get_gateway_choices(limit_to_2_item_tuple=True)
        return super(AppConf, self).__getattribute__(name)

    def get_gateway_choices(self, limit_to_2_item_tuple=True):
        """
        Return gateway choices
        :param limit_to_2_item_tuple: indicate weather to limit the output to two item tuple
        (like choices option on model) OR the original gateway choices will should contain 3 item tuple
        :return:
        """
        name = 'KNPAY_GATEWAY_CHOICES'
        choices = getattr(self._meta.holder, name)
        if limit_to_2_item_tuple:
            return [(x[0], x[1]) for x in choices]
        return choices

    class Meta:
        prefix = 'KNPAY'
        proxy = False
        required = [
            'GATEWAY_CHOICES',
            'BASE_URL'
        ]


config = KnpayPluginConf()
