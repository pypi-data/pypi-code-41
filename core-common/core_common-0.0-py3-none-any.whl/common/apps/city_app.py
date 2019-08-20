from confapp import conf
from pyforms_web.widgets.django import ModelAdminWidget

from common.models import City

class CityAdminApp(ModelAdminWidget):

    UID   = 'cities'
    TITLE = 'Cities'
    MODEL = City

    LIST_FILTER = ['country']
    SEARCH_FIELDS = ['name__icontains']
    FIELDSETS = ['name', 'country']
    LIST_DISPLAY = ['name', 'country']

    AUTHORIZED_GROUPS = ['superuser']

    ########################################################
    #### ORQUESTRA CONFIGURATION ###########################
    ########################################################
    LAYOUT_POSITION      = conf.ORQUESTRA_HOME
    ORQUESTRA_MENU       = 'top>CommonDashboard'
    ORQUESTRA_MENU_ORDER = 0
    ORQUESTRA_MENU_ICON  = 'building outline'
    ########################################################
    
    
    