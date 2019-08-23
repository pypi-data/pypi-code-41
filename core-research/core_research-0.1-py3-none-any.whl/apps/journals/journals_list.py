from confapp import conf
from pyforms_web.widgets.django import ModelAdminWidget


from research.models import Journal

from .journal_form import JournalFormWidget



class JournalListWidget(ModelAdminWidget):
    """
    """
    UID = 'journals'
    TITLE = 'Journals'

    MODEL = Journal

    ###########################################################################
    # ORQUESTRA CONFIGURATION

    LAYOUT_POSITION = conf.ORQUESTRA_HOME_FULL
    ORQUESTRA_MENU = 'left>PublicationsListWidget'
    ORQUESTRA_MENU_ORDER = 1
    ORQUESTRA_MENU_ICON = 'newspaper outline'
    #AUTHORIZED_GROUPS = ['superuser']

    ###########################################################################

    USE_DETAILS_TO_EDIT = False

    SEARCH_FIELDS = [
        'journal_name__icontains',
        'journal_abbreve__icontains'
    ]

    LIST_DISPLAY = [
        'journal_name',
        'journal_abbreve'
    ]

    EDITFORM_CLASS = JournalFormWidget
