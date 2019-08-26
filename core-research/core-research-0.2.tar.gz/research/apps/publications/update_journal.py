from pyforms.basewidget import BaseWidget, no_columns
from pyforms.controls import ControlAutoComplete
from pyforms.controls import ControlText
from pyforms.controls import ControlButton
from confapp import conf

from research.models import Journal, JournalAlias

class UpdateJournal(BaseWidget):

    TITLE = 'Update journal'

    LAYOUT_POSITION = conf.ORQUESTRA_NEW_WINDOW

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)

        self._name     = ControlText('Name \ Alias', default=kwargs.get('name', ''))
        self._journal  = ControlAutoComplete(
            'Journal',
            queryset=Journal.objects.all().order_by('journal_name')
        )
        self._createbtn = ControlButton('<i class="icon plus" ></i> Create', default=self.__createbtn_evt)
        self._updatebtn = ControlButton('<i class="icon edit" ></i> Add alias to the journal', default=self.__updatebtn_evt, css='basic')

        self.formset = [
            ('_name', '_journal'),
            no_columns('_createbtn', '_updatebtn')
        ]

    def __createbtn_evt(self):
        j = Journal(journal_name=self._name.value)
        j.save()
        self.close()

    def __updatebtn_evt(self):
        try:
            j = Journal.objects.get(pk=self._journal.value)
            alias = JournalAlias(name=self._name.value, journal=j)
            alias.save()
            self.close()
        except Journal.DoesNotExist as e:
            self.alert(str(e))

    @classmethod
    def has_permissions(cls, user):
        if user.is_superuser:
            return True

        return user.groups.filter(
            permissions__codename__in=['app_access_imp_pub']
        ).exists()