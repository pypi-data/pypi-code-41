
from django.contrib import admin
from django.utils.translation import ugettext_lazy as _

from orders.constants import DAYS_OF_WEEK
from orders.decorators import template_list_item, short_description


class BaseOrderAdmin(admin.ModelAdmin):

    @template_list_item('orders/admin/customer.html', _('Customer'))
    def customer_tag(self, obj):
        return {'object': obj}

    @template_list_item('orders/admin/delivery.html', _('Delivery'))
    def delivery_tag(self, obj):
        return {'object': obj}

    @template_list_item('orders/admin/products.html', _('Products'))
    def products_tag(self, obj):
        return {'object': obj}

    @short_description(_('Order'))
    def order_tag(self, obj):
        day = DAYS_OF_WEEK[obj.date_created.weekday()]
        return '#{} - ({}) {}'.format(
            obj.id, day, obj.date_created.strftime('%d.%m.%Y %H:%M '))


class OrderStatusAdmin(admin.ModelAdmin):

    list_display = ['name', 'is_default']

    def save_model(self, request, obj, form, change):

        if obj.is_default:
            self.model.objects.update(is_default=False)

        super().save_model(request, obj, form, change)
