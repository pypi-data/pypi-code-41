from confapp import conf
from pyforms.basewidget import no_columns
from pyforms_web.widgets.django import ModelAdminWidget

from news.models import Subject

class SubjectsApp(ModelAdminWidget):

    UID   = 'subjects'
    TITLE = 'Subjects'
    MODEL = Subject

    SEARCH_FIELDS = ['name__icontains']

    LIST_COLS_SIZES = ['50px', '50px', 'auto']
    LIST_COLS_ALIGN = ['center', 'center', 'left']
    LIST_HEADERS = ['Active', 'Order', 'Title']
    LIST_FILTER  = ['active']
    LIST_DISPLAY = ['active', 'order', 'name']

    FIELDSETS = [
        no_columns('order', 'active'),
        'name',
        'text'
    ]

    ########################################################
    #### ORQUESTRA CONFIGURATION ###########################
    ########################################################
    LAYOUT_POSITION      = conf.ORQUESTRA_HOME
    ORQUESTRA_MENU       = 'left>MessagesApp'
    ORQUESTRA_MENU_ORDER = 0
    ORQUESTRA_MENU_ICON  = 'tag'
    ########################################################