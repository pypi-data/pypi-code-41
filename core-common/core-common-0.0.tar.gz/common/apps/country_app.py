from confapp import conf
from pyforms_web.widgets.django import ModelAdminWidget

from common.models import Country

class CountryAdminApp(ModelAdminWidget):

    UID   = 'countries'
    TITLE = 'Countries'
    MODEL = Country

    SEARCH_FIELDS = ['name__icontains', 'code__icontains']
    FIELDSETS = ['name', 'code']
    LIST_DISPLAY = ['name', 'code']

    AUTHORIZED_GROUPS = ['superuser']

    ########################################################
    #### ORQUESTRA CONFIGURATION ###########################
    ########################################################
    LAYOUT_POSITION      = conf.ORQUESTRA_HOME
    ORQUESTRA_MENU       = 'top>CommonDashboard'
    ORQUESTRA_MENU_ORDER = 0
    ORQUESTRA_MENU_ICON  = 'flag outline'
    ########################################################
    
    
    