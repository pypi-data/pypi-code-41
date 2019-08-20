# -*- coding: utf-8 -*-

from __future__ import unicode_literals

from django import template

from knpay_plugin.conf import config
from knpay_plugin.api import prepare_payload as prepare_payload_func

register = template.Library()


@register.simple_tag
def prepare_payload(payment_transaction):
    return prepare_payload_func(payment_transaction)


@register.inclusion_tag('knpay_plugin/gateway_choices.html', takes_context=True)
def show_gateway_choices(context):
    context['gateway_choices'] = config.GATEWAY_CHOICES
    return context
