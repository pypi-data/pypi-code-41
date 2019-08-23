from confapp import conf
from pyforms.basewidget import no_columns
from pyforms_web.widgets.django import ModelAdminWidget

from news.models import MailingList


class MailingListsApp(ModelAdminWidget):

    UID   = 'mailing-lists'
    TITLE = 'Mailing lists'
    MODEL = MailingList

    SEARCH_FIELDS = ['name__icontains', 'email__icontains']

    LIST_HEADERS = ['Name', 'Email', 'Template', 'Remind', 'When']
    LIST_DISPLAY = ['name', 'email', 'template', 'send_reminder', 'send_frequency']

    FIELDSETS = [
        no_columns('send_frequency', 'send_reminder'),
        'name', 'subject', 'email', 'template', 'reminder_template'
    ]

    ########################################################
    #### ORQUESTRA CONFIGURATION ###########################
    ########################################################
    LAYOUT_POSITION = conf.ORQUESTRA_HOME
    ORQUESTRA_MENU = 'left>MessagesApp'
    ORQUESTRA_MENU_ORDER = 0
    ORQUESTRA_MENU_ICON = 'address book outline'
    ########################################################
