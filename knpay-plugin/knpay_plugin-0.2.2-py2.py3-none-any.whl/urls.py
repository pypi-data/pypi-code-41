# -*- coding: utf-8 -*-

from __future__ import unicode_literals

from django.conf.urls import url
from knpay_plugin import views
from knpay_plugin.conf import config


urlpatterns = [
    url(r'^disclose/%s/$' % config.COMPLETE_VIEWS_REGEX,
        views.DisclosureView.as_view(), name='kp_disclosure'),
    url(r'^completed/%s/$' % config.COMPLETE_VIEWS_REGEX,
        views.BaseCompletedView.as_view(), name='kp_complete'),
    url(r'^pay-choices/$',
        views.get_payment_choices, name='kp_pay_choices'),

]
