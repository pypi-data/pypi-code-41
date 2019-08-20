from confapp import conf

from django.conf import settings
from orders.models import Order, OrderExpenseCode

from pyforms.basewidget import segment
from pyforms.basewidget import no_columns
from pyforms_web.widgets.django import ModelAdminWidget
from pyforms_web.widgets.django import ModelFormWidget

from .orders_form import OrderEditFormWidget, OrderExpenseCodeInline

class AllOrderExpenseCodeInline(OrderExpenseCodeInline):

    def has_add_permissions(self):
        return True

    def has_view_permissions(self, obj):
        return True

    def has_remove_permissions(self, obj):
        return True
    


class AllOrderEditFormWidget(OrderEditFormWidget):

    #UID   = 'edit-all-orders'
    TITLE = 'Edit order (full access)'

    AUTHORIZED_GROUPS = ['superuser', settings.APP_PROFILE_ALL_ORDERS]

    #sub models to show in the interface
    INLINES = [AllOrderExpenseCodeInline, ]
    
    #formset of the edit form
    FIELDSETS = [
        no_columns( 'order_req', 'group'),
        (
            segment(
                'finance',
                'order_desc',
                ('order_amount', 'currency', 'order_paymethod'),
                field_css='fourteen wide',
            ),
            segment(
                ('order_reqnum', 'order_reqdate'),
                ('order_podate', 'expected_date'),
                ('order_deldate', ' '),
                'order_notes',
                css='secondary',
            ),
        ),
        segment(
            'AllOrderExpenseCodeInline',
            css='green'
        ),
        no_columns('responsible',)
    ]

    @classmethod
    def has_permissions(cls, user):
        from .all_orders_list import OrderAdminWidget
        return OrderAdminWidget.has_permissions(user)

    @property
    def title(self):
        obj = self.model_object
        if obj is None:
            return ModelFormWidget.title.fget(self)
        else:
            return "Order(full access): {0}".format(obj.order_id)

    @title.setter
    def title(self, value):
        ModelFormWidget.title.fset(self, value)


    def has_add_permissions(self):
        return True

    def has_view_permissions(self):
        return True

    def has_remove_permissions(self):
        return True

    def has_update_permissions(self):
        return True