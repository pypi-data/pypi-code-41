# -*- coding: utf-8 -*-

from __future__ import unicode_literals

import json

from django.http import JsonResponse, HttpResponse
from django.utils.decorators import method_decorator
from django.utils.encoding import force_text
from django.utils.translation import ugettext as _
from django.views import generic
from django.views.decorators.cache import never_cache
from django.views.generic.detail import SingleObjectMixin
from django.views.generic.base import TemplateResponseMixin
from django.views.decorators.csrf import csrf_exempt

from knpay_plugin.forms import PaymentForm
from knpay_plugin.models import PaymentTransaction
from knpay_plugin.conf import config


class CreatePaymentMixin(object):
    form_class = PaymentForm

    def get_extra(self):
        """
        :return: custom values which can be queried against
         once customer returns to merchant website.
         IE: cart_id
        """
        return

    def get_initial(self):
        # amount formatted as per chosen currency
        # currency code ISO 4217 Currency Code
        initial = super(CreatePaymentMixin, self).get_initial()
        initial.update({
            'currency_code': config.DEFAULT_CURRENCY,
            'language': getattr(self.request, 'LANGUAGE_CODE', 'en')
        })
        return initial

    def get_form_kwargs(self):
        kwargs = {
            'request': self.request,
            'extra': self.get_extra(),
            'initial': self.get_initial(),
            'prefix': self.get_prefix(),
        }
        if self.request.method == 'POST':
            data = self.request.POST.copy()
            if not config.RENDER_FORM:
                data.update(self.get_initial())
            kwargs['data'] = data
        return kwargs

    def get_success_message(self, form):
        return _("Redirecting to payment page...")

    def get_error_message(self, form):
        return _("There was an error while redirecting you to payment page. "
                 "Refresh and try again.")

    def form_valid(self, form):
        url = form.connect()
        if url:
            return JsonResponse(
                {'redirect_url': url, 'message': self.get_success_message(form)},
                status=200)
        return JsonResponse({'message': self.get_error_message(form), 'errors': form.errors}, status=400)

    def form_invalid(self, form):
        return JsonResponse({'message': self.get_error_message(form), 'errors': form.errors_as_dict}, status=400)


@method_decorator([never_cache, csrf_exempt], name='dispatch')
class DisclosureView(SingleObjectMixin, generic.View):
    """
    View for handling incoming KNPay request
    """
    queryset = PaymentTransaction.objects.created()
    http_method_names = ['post']
    slug_url_kwarg = 'order_no'
    slug_field = 'order_no'

    def dispatch(self, request, *args, **kwargs):
        return super(DisclosureView, self).dispatch(request, *args, **kwargs)

    def post(self, request, *args, **kwargs):
        knpay_payload = json.loads(request.body)
        payment_transaction = self.get_object()
        result = knpay_payload['result']

        if result == 'success':
            method = 'acknowledge_payment'
        elif result == 'cancel':
            method = 'cancel'
        else:
            method = 'fail'

        getattr(payment_transaction, method)(knpay_payload)
        payment_transaction.save()
        return HttpResponse()


class BaseCompletedView(SingleObjectMixin,
                        TemplateResponseMixin,
                        generic.View):
    """
    Handle knpay redirect after silent post has ended.
    Place order, send confirmation emails, usually actions
    which happens only once in a transaction stage.
    """
    queryset = PaymentTransaction.objects.completed()
    slug_url_kwarg = 'order_no'
    slug_field = 'order_no'
    template_name = 'knpay_plugin/payment_details.html'

    def handle_successful_payment(self, request, *args, **kwargs):
        """
        This method will be called only once
        """
        return self.get(request, *args, **kwargs)

    def handle_canceled_payment(self, request, *args, **kwargs):
        """
        This method will be called only once
        """
        return self.get(request, *args, **kwargs)

    def get(self, request, *args, **kwargs):
        if not hasattr(self, 'object'):
            self.object = self.get_object()

        if not self.object.is_consumed:
            self.object.consume()
            if self.object.is_paid():
                self.handle_successful_payment(request, *args, **kwargs)
            else:
                self.handle_canceled_payment(request, *args, **kwargs)
        context = self.get_context_data(object=self.object)
        return self.render_to_response(context)


def get_payment_choices(request):
    val = []
    for choice in config.get_gateway_choices(limit_to_2_item_tuple=False):
        d = {'code': choice[0],
             'gateway_name': force_text(choice[1])}
        if len(choice) > 2:
            d['internal_code'] = choice[2]
        val.append(d)

    return JsonResponse(val, status=200)
