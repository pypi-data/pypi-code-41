from confapp import conf
from pyforms_web.widgets.django import ModelAdminWidget

from finance.models import FinancingAgency

class FinancingAgencyAdminApp(ModelAdminWidget):

    UID   = 'financing-agency'
    TITLE = 'Financing agency'
    MODEL = FinancingAgency

    LIST_DISPLAY = ['name']
    FIELDSETS = ['name']
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
    