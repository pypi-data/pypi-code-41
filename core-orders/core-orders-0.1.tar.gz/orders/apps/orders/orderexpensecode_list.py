from pyforms.basewidget import no_columns
from orders.models import OrderExpenseCode
from pyforms_web.widgets.django import ModelAdminWidget

class OrderExpenseCodeInline(ModelAdminWidget):
    MODEL = OrderExpenseCode
    TITLE = 'Expenses codes'

    #EDITFORM_CLASS = OrderExpenseCodeEditFormAdmin

    LIST_DISPLAY = [
        'expensecode',
        'purchase_order',
        'orderexpensecode_amount',
    ]

    FIELDSETS = [
        'expensecode',
        no_columns('purchase_order', 'orderexpensecode_amount')
    ]