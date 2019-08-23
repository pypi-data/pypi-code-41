from confapp import conf
from orders.models import Order
from pyforms.controls import ControlCheckBox
from pyforms_web.widgets.django import ModelAdminWidget
from django.conf import settings

from .orders_form import OrderEditFormWidget
from .orders_list import OrderAdminWidget

from .all_orders_form import AllOrderEditFormWidget

from django.contrib.contenttypes.models import ContentType
from permissions.models import Permission


class AllOrderAdminWidget(OrderAdminWidget):

    UID   = 'all-orders'
    TITLE = 'All orders'

    ########################################################
    #### ORQUESTRA CONFIGURATION ###########################
    ########################################################
    ORQUESTRA_MENU       = 'left>OrderAdminWidget'
    ########################################################

    AUTHORIZED_GROUPS = ['superuser', settings.APP_PROFILE_ALL_ORDERS]

    EDITFORM_CLASS = AllOrderEditFormWidget

    @classmethod
    def has_permissions(cls, user):
        if user.is_superuser: return True

        # Search for the user groups with certain permissions
        contenttype = ContentType.objects.get_for_model(cls.MODEL)
        authgroups  = user.groups.filter(permissions__content_type=contenttype)
        authgroups  = authgroups.filter(permissions__codename='app_access_allorders')
        return Permission.objects.filter(djangogroup__in=authgroups).exists()



    def get_queryset(self, request, qs):
        qs = Order.objects.exclude(expensecode__expensecode_number='01')
        if self._curryear_filter.value:
            qs = qs.current_year()
        return qs


    def has_view_permissions(self, obj):
        return True

    def has_add_permissions(self):
        return True

    def has_remove_permissions(self, obj):
        return True