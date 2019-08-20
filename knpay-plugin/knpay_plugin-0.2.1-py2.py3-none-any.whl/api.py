# -*- coding: utf-8 -*-
# noinspection PyUnresolvedReferences
from __future__ import unicode_literals

from collections import OrderedDict
# noinspection PyUnresolvedReferences
from decimal import Decimal

from django.utils.translation import ugettext as _

from knpay_plugin.forms import PaymentForm
from knpay_plugin.conf import config


def create_payment_url(amount, gateway_code=None, request=None, extra=None,
                       is_payment_request=False, custom_fields=None, **data):
    """
    A wrapper around create_payment that return ONLY the url of the transaction

    :param amount: str, float or Decimal
    :param gateway_code: str
    :param request: HttpRequest instance
    :param extra: dict with keys required to be sent extra to knpay and
                  saved in extra field of PaymentTransaction {'basket_id': '12', 'food': 'chinese'}
    :param is_payment_request: Boolean. If True, will create Payment Request url
    :param custom_fields: dict with custom fields defined in knpay dashboard
    :param data: dict with fields existing on PaymentTransaction {'currency_code': 'KWD', 'language': 'en',}
    :return: bool, dict OR PaymentTransaction instance
    """
    instance, result = create_payment_transaction(
        amount=amount, gateway_code=gateway_code, request=request,
        extra=extra, is_payment_request=is_payment_request, custom_fields=custom_fields, **data)
    if result:
        return instance.payment_url, result
    return instance, result


def prepare_payload(payment_transaction):
    payload = OrderedDict()
    knpay_payload = payment_transaction.knpay_response
    gateway_payload = payment_transaction.gateway_response

    payload[_("Amount")] = '%s %s' % (payment_transaction.amount, payment_transaction.currency_code)
    if config.SHOW_ORDER_NO:
        payload[_("Order No")] = payment_transaction.order_no
    payload[_("Reference No")] = knpay_payload['reference_number']
    payload[_("Status")] = knpay_payload['result'].upper()
    payload[_("Gateway")] = config.GATEWAY_NAMES[knpay_payload['gateway_name'].lower()]

    for item in config.VAR_MAPPING:
        val = gateway_payload.get(item[0])
        if val:
            payload[item[1]] = val
    return payload


def create_payment_transaction(amount, gateway_code=None, request=None,
                               extra=None, is_payment_request=False, custom_fields=None, **data):
    """
    creates a new payment
    :param amount: str, float or Decimal
    :param gateway_code: str
    :param request: HttpRequest instance
    :param extra: dict with keys required to be sent extra to knpay and
                  saved in extra field of PaymentTransaction {'basket_id': '12', 'food': 'chinese'}
                  Note: dict values should NOT contain `None`
    :param is_payment_request: Boolean. If True, will create Payment Request transaction type
    :param custom_fields: dict with custom fields defined in knpay dashboard
    :param data: dict with fields existing on PaymentTransaction {'currency_code': 'KWD', 'language': 'en',}
    :return: A tuple: ( (instance or errors dict) , result as bool)
    """
    if isinstance(amount, Decimal):
        amount = str(amount)

    data.update({'amount': amount,
                 'currency_code': data.get('currency_code', config.DEFAULT_CURRENCY)})
    if gateway_code is not None:
        data.update({'gateway_code': gateway_code})
    form = PaymentForm(request=request, extra=extra,
                       data=data, custom_fields=custom_fields,
                       is_payment_request=is_payment_request)
    if form.is_valid():
        url = form.connect()
        if url is not None:
            return form.instance, True
        # return form.errors, False
    return form.errors, False
