from confapp import conf
from pyforms_web.widgets.django import ModelAdminWidget

from news.models import Message
from .message_form import MessageForm

class MessagesApp(ModelAdminWidget):

    UID   = 'messages'
    TITLE = 'Messages'
    MODEL = Message

    SEARCH_FIELDS = ['name__icontains']
    LIST_COLS_SIZES = ['30px', '30px', 'auto', 'auto', '50px', '50px']
    LIST_COLS_ALIGN = ['center', 'center', 'left', 'left', 'center', 'center']
    LIST_FILTER = ['subject', 'is_event', 'publish_start', 'publish_end']
    LIST_HEADERS = ['Event', 'Order','Subject', 'Name', 'Publish start', 'Publish end']
    LIST_DISPLAY = ['is_event', 'order', 'subject', 'name', 'publish_start', 'publish_end']

    EDITFORM_CLASS = MessageForm

    ########################################################
    #### ORQUESTRA CONFIGURATION ###########################
    ########################################################
    LAYOUT_POSITION      = conf.ORQUESTRA_HOME
    ORQUESTRA_MENU       = 'left'
    ORQUESTRA_MENU_ORDER = 0
    ORQUESTRA_MENU_ICON  = 'sticky note outline'
    ########################################################