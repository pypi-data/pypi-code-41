from confapp import conf
from pyforms_web.widgets.django import ModelAdminWidget

from finance.models import Grant

class GrantsAdminApp(ModelAdminWidget):

    UID   = 'grants'
    TITLE = 'Grants'
    MODEL = Grant

    LIST_DISPLAY = ['name', 'grantor']
    FIELDSETS = [
        'name',
        ('nationality', 'domain', 'grantor')
    ]
    SEARCH_FIELDS = ['name__icontains']

    ########################################################
    #### ORQUESTRA CONFIGURATION ###########################
    ########################################################
    LAYOUT_POSITION      = conf.ORQUESTRA_HOME
    ORQUESTRA_MENU       = 'left>FinancesDashboardWidget'
    ORQUESTRA_MENU_ORDER = 0
    ORQUESTRA_MENU_ICON  = 'flag'
    ########################################################

    AUTHORIZED_GROUPS = ['superuser']
    