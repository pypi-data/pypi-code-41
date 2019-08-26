from django.conf import settings

from confapp import conf
from pyforms_web.basewidget import BaseWidget


class FinancesDashboardWidget(BaseWidget):
    """
    """

    UID = 'finances'
    TITLE = 'Finances'

    # ORQUESTRA CONFIGURATION
    # =========================================================================
    ORQUESTRA_MENU = 'left'
    ORQUESTRA_MENU_ICON = 'dollar'
    ORQUESTRA_MENU_ORDER = 30
    LAYOUT_POSITION = conf.ORQUESTRA_HOME
    # =========================================================================

    AUTHORIZED_GROUPS = ['superuser', settings.PROFILE_LAB_ADMIN]
