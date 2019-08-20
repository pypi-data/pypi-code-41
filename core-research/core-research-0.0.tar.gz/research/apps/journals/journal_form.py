from confapp import conf
from pyforms_web.widgets.django import ModelFormWidget
from pyforms_web.widgets.django import ModelAdminWidget
from research.models import Journal, JournalAlias


class JournalAliasList(ModelAdminWidget):
    MODEL = JournalAlias
    TITLE = 'Journal alias'

    FIELDSETS = ['name']
    LIST_DISPLAY = ['name']

class JournalFormWidget(ModelFormWidget):

    TITLE = 'Edit journal'
    MODEL = Journal

    LAYOUT_POSITION = conf.ORQUESTRA_NEW_TAB

    HAS_CANCEL_BTN_ON_EDIT = False
    CLOSE_ON_REMOVE        = True

    INLINES = [JournalAliasList]

    FIELDSETS = [
        'journal_name',
        'journal_abbreve',
        'journal_publisher',
        ('journal_issn', 'journal_essn'),
        'JournalAliasList'
    ]

    @property
    def title(self):
        obj = self.model_object
        if obj is None:
            return ModelFormWidget.title.fget(self)
        else:
            return "Journal: {0}".format(obj.journal_name)

    @title.setter
    def title(self, value):
        ModelFormWidget.title.fset(self, value)


    def has_remove_permissions(self):
        return False