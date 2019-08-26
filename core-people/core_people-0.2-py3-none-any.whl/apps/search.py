from confapp import conf
from django.db.models import Q
from people.models import Group
from people.models import Person
from pyforms.controls import ControlText
from pyforms.basewidget import BaseWidget
from pyforms.controls import ControlQueryList
from pyforms.controls import ControlAutoComplete


class SearchWidget(BaseWidget):

    MODEL = Person

    UID = 'search'
    TITLE = 'Find people'

    LIST_HEADERS = [
        'Name', 'Groups', 'Email', 'Extension', ''
    ]
    LIST_COLS_SIZES = [
        '40%', '35%', '15%', '5%', '5%'
    ]
    LIST_DISPLAY = [
        'name',
        'get_groups',
        'email',
        'phone_extension',
        'thumbnail_80x80',
    ]

    LIST_FILTER = [
        'groupmember__group',
        'groupmember__position',
    ]

    # Orquestra Configuration
    # =========================================================================

    LAYOUT_POSITION = conf.ORQUESTRA_HOME

    ORQUESTRA_MENU = 'left'
    ORQUESTRA_MENU_ICON = 'search'
    ORQUESTRA_MENU_ORDER = 0

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)

        self._search = ControlText('Search by name', on_enter_event=self.populate_list )
        self._groups = ControlAutoComplete("Filter by groups", queryset=Group.objects.all(), multiple=True, changed_event=self.populate_list)
        self._list   = ControlQueryList('People', list_display=self.LIST_DISPLAY, headers=self.LIST_HEADERS, columns_size=self.LIST_COLS_SIZES)

        self.formset = [
            '_search',
            '_groups',
            '_list'
        ]

        self.populate_list()
        
    def populate_list(self):
        qs = Person.objects.active()
        has_filter = False
        
        if self._search.value:
            qs = qs.filter(
                Q(full_name__icontains=self._search.value) |
                Q(email__icontains=self._search.value)
            )
            has_filter = True
        
        if self._groups.value:
            qs = qs.filter_by_groups(self._groups.value)
            has_filter = True

        if has_filter:
            qs = qs.order_by('full_name')
        else:
            qs = qs.order_by('?')

        self._list.value = qs
