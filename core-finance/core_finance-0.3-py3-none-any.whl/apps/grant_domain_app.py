from confapp import conf
from pyforms_web.widgets.django import ModelAdminWidget

from finance.models import Grantdomain

class GrantDomainAdminApp(ModelAdminWidget):

    UID   = 'grant-domains'
    TITLE = 'Grant domains'
    MODEL = Grantdomain

    LIST_DISPLAY = ['domain']
    FIELDSETS = ['domain']
    SEARCH_FIELDS = ['domain__icontains']

    ########################################################
    #### ORQUESTRA CONFIGURATION ###########################
    ########################################################
    LAYOUT_POSITION      = conf.ORQUESTRA_HOME
    ORQUESTRA_MENU       = 'top>CommonDashboard'
    ORQUESTRA_MENU_ORDER = 0
    ORQUESTRA_MENU_ICON  = 'flag'
    ########################################################

    AUTHORIZED_GROUPS = ['superuser']
    