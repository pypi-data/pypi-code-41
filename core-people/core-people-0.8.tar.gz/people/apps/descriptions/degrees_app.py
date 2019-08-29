from confapp import conf
from pyforms_web.widgets.django import ModelAdminWidget

from people.models import Degree

class DegreesAdminApp(ModelAdminWidget):

    UID   = 'degrees'
    TITLE = 'Degrees'
    MODEL = Degree

    SEARCH_FIELDS = ['name__icontains']
    FIELDSETS = ['name']
    LIST_DISPLAY = ['name']

    ########################################################
    #### ORQUESTRA CONFIGURATION ###########################
    ########################################################
    LAYOUT_POSITION      = conf.ORQUESTRA_HOME
    ORQUESTRA_MENU       = 'top>CommonDashboard'
    ORQUESTRA_MENU_ORDER = 0
    ORQUESTRA_MENU_ICON  = 'certificate'
    ########################################################

    AUTHORIZED_GROUPS = ['superuser']
    
    