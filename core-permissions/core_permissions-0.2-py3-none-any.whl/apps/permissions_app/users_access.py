from pyforms.controls import ControlQueryList, ControlAutoComplete
from pyforms.basewidget import BaseWidget
from django.contrib.auth.models import User
from people.models import Person

from humanresources.models import Contract, ContractProposal
from orders.models import Order

from confapp import conf

class UsersAccesses(BaseWidget):

    UID = 'users-accesses'
    TITLE = 'Users accesses'

    AUTHORIZED_GROUPS = ['superuser']


    ORQUESTRA_MENU = 'left>PermissionsListWidget'
    ORQUESTRA_MENU_ICON = 'lock'
    ORQUESTRA_MENU_ORDER = 1000

    LAYOUT_POSITION = conf.ORQUESTRA_HOME_FULL

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)

        self._user = ControlAutoComplete('User', 
            queryset=User.objects.all(), 
            changed_event=self.__populate_lists,
            queryset_filter=self.__members_queryset_filter
        )

        self._contracts = ControlQueryList('Contracts', 
            default=Contract.objects.filter(pk=None),
            list_display=['person', 'contract_ref', 'position', 'contract_start', 'contract_end', 'is_active'] )
        self._proposals = ControlQueryList('Proposals', 
            default=ContractProposal.objects.filter(pk=None),
            list_display=['personname', 'position', 'contractproposal_start', 'end_date', 'supervisor', 'status_icon'])
        self._people    = ControlQueryList('People',    
            default=Person.objects.filter(pk=None),
            list_display=['thumbnail_80x80', 'full_name', 'person_email', 'person_active'])
        self._orders    = ControlQueryList('Orders',    
            default=Order.objects.filter(pk=None),
            list_display=['order_desc', 'order_req', 'finance', 'order_amount', 'order_reqnum', 'order_reqdate', 'order_ponum', 'expense_codes'])


        self.formset = [
            '_user',
            {
                'a:Contracts':['_contracts'],
                'b:Proposals':['_proposals'],
                'c:People':   ['_people'],
                'd:Orders':   ['_orders'],
            }
        ]


    def __members_queryset_filter(self, qs, keyword, control):
        if keyword:
            return qs.filter(username__icontains=keyword)
        else:
            return qs


    def __populate_lists(self):
        try:
            user = User.objects.get(pk=self._user.value)

            self._contracts.value = Contract.objects.list_permissions(user)
            self._orders.value    = Order.objects.list_permissions(user)
            self._proposals.value = ContractProposal.objects.list_permissions(user)
            self._people.value    = Person.objects.list_permissions(user)

        except User.DoesNotExist:
            self._contracts.value = None
            self._orders.value    = None
            self._proposals.value = None
            self._people.value    = None

        