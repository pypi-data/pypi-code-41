from confapp import conf
from pyforms_web.widgets.django import ModelAdminWidget

from people.models import GroupType

class GroupTypesAdminApp(ModelAdminWidget):

    UID   = 'group-types'
    TITLE = 'Group types'
    MODEL = GroupType

    SEARCH_FIELDS = ['name__icontains']
    FIELDSETS = ['name']
    LIST_DISPLAY = ['name']

    ########################################################
    #### ORQUESTRA CONFIGURATION ###########################
    ########################################################
    LAYOUT_POSITION      = conf.ORQUESTRA_HOME
    ORQUESTRA_MENU       = 'top>CommonDashboard'
    ORQUESTRA_MENU_ORDER = 0
    ORQUESTRA_MENU_ICON  = 'tags'
    ########################################################

    AUTHORIZED_GROUPS = ['superuser']
    
    