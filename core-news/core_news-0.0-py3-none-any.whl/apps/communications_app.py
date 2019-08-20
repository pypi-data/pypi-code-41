from confapp import conf
from pyforms_web.widgets.django import ModelAdminWidget

from news.models import Communication

class CommunicationsApp(ModelAdminWidget):

    UID   = 'communications'
    TITLE = 'Communications'
    MODEL = Communication

    SEARCH_FIELDS = ['name__icontains']
    LIST_DISPLAY  = ['name']

    FIELDSETS = [
        ('sent_on', 'sent_to'),
        'name',
        'html',
    ]

    READ_ONLY = ['sent_on', 'sent_to', 'name', 'html']


    ########################################################
    #### ORQUESTRA CONFIGURATION ###########################
    ########################################################
    LAYOUT_POSITION      = conf.ORQUESTRA_HOME
    ORQUESTRA_MENU       = 'left>MessagesApp'
    ORQUESTRA_MENU_ORDER = 0
    ORQUESTRA_MENU_ICON  = 'newspaper'
    ########################################################

    
    def has_add_permissions(self):
        return False