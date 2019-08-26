from confapp import conf
from pyforms_web.widgets.django import ModelAdminWidget

from common.models import Nationality

class NationalityAdminApp(ModelAdminWidget):

    UID   = 'nationalities'
    TITLE = 'Nationalities'
    MODEL = Nationality

    ########################################################
    #### ORQUESTRA CONFIGURATION ###########################
    ########################################################
    LAYOUT_POSITION      = conf.ORQUESTRA_HOME
    ORQUESTRA_MENU       = 'top>CommonDashboard'
    ORQUESTRA_MENU_ORDER = 0
    ORQUESTRA_MENU_ICON  = 'flag'
    ########################################################

    AUTHORIZED_GROUPS = ['superuser']
    