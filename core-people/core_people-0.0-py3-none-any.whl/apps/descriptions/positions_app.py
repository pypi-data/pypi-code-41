from confapp import conf
from pyforms_web.widgets.django import ModelAdminWidget

from people.models import Position


class PositionsAdminApp(ModelAdminWidget):

    UID   = 'positions'
    TITLE = 'Positions'
    MODEL = Position

    SEARCH_FIELDS = ['name__icontains']
    FIELDSETS = ['name']
    LIST_DISPLAY = ['name']

    ########################################################
    #### ORQUESTRA CONFIGURATION ###########################
    ########################################################
    LAYOUT_POSITION = conf.ORQUESTRA_HOME
    ORQUESTRA_MENU = 'top>CommonDashboard'
    ORQUESTRA_MENU_ORDER = 0
    ORQUESTRA_MENU_ICON = 'address card'
    ########################################################

    AUTHORIZED_GROUPS = ['superuser']

