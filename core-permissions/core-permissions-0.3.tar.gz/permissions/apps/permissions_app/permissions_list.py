from confapp import conf
from pyforms_web.widgets.django import ModelAdminWidget

from permissions.models import Permission

from .permissions_form import PermissionsFormWidget

class PermissionsListWidget(ModelAdminWidget):
    """
    """
    UID = 'permissions'
    TITLE = 'Permissions'

    AUTHORIZED_GROUPS = ['superuser']

    MODEL = Permission

    ORQUESTRA_MENU = 'top'
    ORQUESTRA_MENU_ICON = 'red lock'
    ORQUESTRA_MENU_ORDER = 10000

    LIST_ROWS_PER_PAGE = 30

    LAYOUT_POSITION = conf.ORQUESTRA_HOME_FULL


    EDITFORM_CLASS = PermissionsFormWidget

    USE_DETAILS_TO_EDIT = False

    READ_ONLY = ['order', 'person', 'proposal', 'contract']

    SEARCH_FIELDS = ['auth_group__name__icontains']

    LIST_DISPLAY = [
        'ranking',
        'auth_group',
        'researchgroup',
        'order',
        'person',
        'proposal',
        'contract',
        'publication'
    ]

    LIST_FILTER = [
        'auth_group__user__username',
        'auth_group',
        'researchgroup',
        'ranking',
    ]

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)

        self._list.css = 'small'
        self._list.columns_size = ['3%', '10%', '10%', '15.4%', '15.4%', '15.4%', '15.4%']
