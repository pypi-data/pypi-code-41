from confapp import conf
from pyforms_web.widgets.django import ModelAdminWidget

from common.models import Citizenship

class CitizenshipAdminApp(ModelAdminWidget):

    UID   = 'citizenships'
    TITLE = 'Citizenships'
    MODEL = Citizenship

    SEARCH_FIELDS = ['name__icontains']
    FIELDSETS = ['name']
    LIST_DISPLAY = ['name']

    AUTHORIZED_GROUPS = ['superuser']

    ########################################################
    #### ORQUESTRA CONFIGURATION ###########################
    ########################################################
    LAYOUT_POSITION      = conf.ORQUESTRA_HOME
    ORQUESTRA_MENU       = 'top>CommonDashboard'
    ORQUESTRA_MENU_ORDER = 0
    ORQUESTRA_MENU_ICON  = 'flag checkered'
    ########################################################
    
    
    