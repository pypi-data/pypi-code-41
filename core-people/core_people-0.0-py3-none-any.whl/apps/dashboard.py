from confapp import conf
from pyforms.basewidget import BaseWidget

class HRDashboard(BaseWidget):
    """
    """
    UID = 'hr-dashboard'
    TITLE = 'Human resources'

    ORQUESTRA_MENU_ORDER = 3
    ORQUESTRA_MENU = 'middle-left'
    ORQUESTRA_MENU_ICON = 'users'
    LAYOUT_POSITION = conf.ORQUESTRA_HOME
