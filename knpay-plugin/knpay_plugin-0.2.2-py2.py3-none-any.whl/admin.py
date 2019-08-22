# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.contrib import admin
from django.utils.translation import ugettext as _

from knpay_plugin.conf import config
from knpay_plugin.models import PaymentTransaction


@admin.register(PaymentTransaction)
class PaymentTransactionAdmin(admin.ModelAdmin):

    list_display = ('order_no', 'amount', 'status', 'created', 'status_changed_at')
    list_filter = ('status', 'created', 'status_changed_at')
    readonly_fields = ('created', 'status_changed_at')
    fieldsets = [
        (None, {
            'fields': ('status', 'is_consumed',)
        }),
        (_("Dates"), {
            'fields': ('created', 'status_changed_at')
        }),
        (_("Conf"), {
            'fields': ('order_no', ('amount', 'currency_code'), ('gateway_code', 'language'),)
        }),
    ]

    if not config.ADMIN_SHOW_OPTIONAL_FIELDS:
        fieldsets.append(
            (_("Customer information"), {
                'fields': (
                    ('customer_first_name', 'customer_last_name'),
                    ('customer_email', 'customer_phone'),
                    'customer_address_line1',
                    'customer_address_line2',
                    'customer_address_city',
                    'customer_address_state',
                    'customer_address_country', 'customer_address_postal_code'
                )
            })
        )

    if not config.ADMIN_SHOW_EXTRA_FIELD:
        fieldsets.append(
            (_("Custom data"), {
                'fields': ('extra',)
            })
        )

    fieldsets.append(
        (_("KNPay response"), {
            'fields': ('knpay_response',)
        })
    )

    def has_add_permission(self, request):
        return False

    def get_form(self, request, obj=None, **kwargs):
        form = super(PaymentTransactionAdmin, self).get_form(request, obj=obj, **kwargs)
        for field_name in form.base_fields:
            form.base_fields[field_name].disabled = True
        return form

    def change_view(self, request, object_id, form_url='', extra_context=None):
        extra_context = extra_context or {}
        extra_context['show_save_and_add_another'] = False
        extra_context['show_save_and_continue'] = False
        extra_context['show_save'] = False
        return super(PaymentTransactionAdmin, self).change_view(request, object_id,
                                                                form_url, extra_context=extra_context)