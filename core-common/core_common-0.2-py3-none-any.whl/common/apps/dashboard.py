from confapp import conf
from pyforms.basewidget import BaseWidget

class CommonDashboard(BaseWidget):
    """
    """
    UID = 'descriptions'
    TITLE = 'Descriptions'

    ORQUESTRA_MENU = 'top'
    ORQUESTRA_MENU_ICON = 'red database'
    ORQUESTRA_MENU_ORDER = 10000
    LAYOUT_POSITION = conf.ORQUESTRA_HOME

    AUTHORIZED_GROUPS = ['superuser']