# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.apps import AppConfig
from django.utils.translation import ugettext_lazy as _


class KnpayPluginConfig(AppConfig):
    name = 'knpay_plugin'
    verbose_name = _("Payment")
