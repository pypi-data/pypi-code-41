from confapp import conf
from django.conf import settings
from pyforms.controls import ControlCheckBox
from pyforms_web.widgets.django import ModelAdminWidget
from django.contrib.contenttypes.models import ContentType
from permissions.models import Permission

from orders.models import Order
from .orders_form import OrderEditFormWidget

class OrderAdminWidget(ModelAdminWidget):

    LIST_ROWS_PER_PAGE = 30

    UID   = 'orders'
    MODEL = Order

    TITLE = 'Orders'

    LIST_DISPLAY = [
        'order_desc',
        'order_req',
        'finance',
        'order_amount',
        'order_reqnum',
        'order_reqdate',
        'order_ponum',
        'expense_codes'
    ]

    LIST_FILTER = [
        'order_req',
        'finance',
        'order_reqdate',
        'order_paymethod',
        'expensecode__expensecode_number',
        'expensecode__financeproject',
        'responsible',
        'group'
    ]

    SEARCH_FIELDS = [
        'order_reqnum__contains',
        'order_req__icontains',
        'order_desc__icontains',
        'order_notes__icontains',
        'orderexpensecode__purchase_order__icontains',
    ]

    EDITFORM_CLASS = OrderEditFormWidget

    USE_DETAILS_TO_EDIT = False

    ########################################################
    #### ORQUESTRA CONFIGURATION ###########################
    ########################################################
    LAYOUT_POSITION      = conf.ORQUESTRA_HOME_FULL
    ORQUESTRA_MENU       = 'left'
    ORQUESTRA_MENU_ORDER = 16
    ORQUESTRA_MENU_ICON  = 'shopping cart'
    #AUTHORIZED_GROUPS   = ['superuser'] #groups with authorization to visualize the app
    ########################################################

    EXPORT_CSV = True


    @classmethod
    def has_permissions(cls, user):
        if user.is_superuser: return True

        # Search for the user groups with certain permissions
        contenttype = ContentType.objects.get_for_model(cls.MODEL)
        authgroups  = user.groups.filter(permissions__content_type=contenttype)
        authgroups  = authgroups.filter(permissions__codename='app_access_orders')
        return Permission.objects.filter(djangogroup__in=authgroups).exists()


    def __init__(self, *args, **kwargs):


        self._curryear_filter = ControlCheckBox(
            'Current year only',
            default=False,
            label_visible=False,
            changed_event=self.populate_list,
        )

        self._notdelivered_filter = ControlCheckBox(
            'Not delivered',
            default=False,
            label_visible=False,
            changed_event=self.populate_list,
        )

        self._pedingpos_filter = ControlCheckBox(
            'Pending POs',
            default=False,
            label_visible=False,
            changed_event=self.populate_list,
        )

        super().__init__(*args, **kwargs)


    def get_toolbar_buttons(self, has_add_permission=False):
        return tuple( (['_add_btn'] if has_add_permission else []) +  [' ','_curryear_filter', '_notdelivered_filter', '_pedingpos_filter'])

    def get_queryset(self, request, qs):

        if self._curryear_filter.value:
            qs = qs.current_year()

        if self._notdelivered_filter.value:
            qs = qs.not_delivered()

        if self._pedingpos_filter.value:
            qs = qs.pending_pos()

        return qs
