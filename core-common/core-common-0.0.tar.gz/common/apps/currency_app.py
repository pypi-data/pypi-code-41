from confapp import conf
from pyforms_web.widgets.django import ModelAdminWidget

from common.models import Currency

class CurrencyAdminApp(ModelAdminWidget):

    UID   = 'currencies'
    TITLE = 'Currencies'
    MODEL = Currency

    SEARCH_FIELDS = ['name__icontains', 'symbol__icontains']
    FIELDSETS = ['name', 'symbol']
    LIST_DISPLAY = ['name', 'symbol']

    AUTHORIZED_GROUPS = ['superuser']

    ########################################################
    #### ORQUESTRA CONFIGURATION ###########################
    ########################################################
    LAYOUT_POSITION      = conf.ORQUESTRA_HOME
    ORQUESTRA_MENU       = 'top>CommonDashboard'
    ORQUESTRA_MENU_ORDER = 0
    ORQUESTRA_MENU_ICON  = 'dollar sign'
    ########################################################
    
    
    