from confapp import conf
from pyforms_web.widgets.django import ModelAdminWidget, ModelFormWidget

from pyforms.controls import ControlCodeMirror
from news.models import Template

class TemplateForm(ModelFormWidget):

    def __init__(self, *args, **kwargs):
        self.code = ControlCodeMirror('Code', height=900)

        super().__init__(*args, **kwargs)



class TemplatesApp(ModelAdminWidget):

    UID   = 'templates'
    TITLE = 'Templates'
    MODEL = Template

    SEARCH_FIELDS = ['name__icontains']
    LIST_DISPLAY = ['name']

    FIELDSETS = ['name', 'code']

    EDITFORM_CLASS = TemplateForm

    ########################################################
    #### ORQUESTRA CONFIGURATION ###########################
    ########################################################
    LAYOUT_POSITION      = conf.ORQUESTRA_HOME
    ORQUESTRA_MENU       = 'left>MessagesApp'
    ORQUESTRA_MENU_ORDER = 0
    ORQUESTRA_MENU_ICON  = 'pen square'
    ########################################################

