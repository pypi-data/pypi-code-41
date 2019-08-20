from dateutil.parser    import parse as parse_date
from research.models    import Journal, AuthorAlias
from pyforms.controls   import ControlButton
from ..publications     import PublicationsListWidget
from ..publication_form import PublicationFormWidget
from django.db.models import Q

from pyforms_web.widgets.django import ModelAdminWidget


class PubForm(PublicationFormWidget):
    pass

class PubsList(PublicationsListWidget):

    UID = None

    EDITFORM_CLASS = PubForm
    LIST_FILTER = []
    USE_DETAILS_TO_EDIT = True
    LIST_ROWS_PER_PAGE = 5

    def __init__(self, *args, **kwargs):

        self.authors  = kwargs.get('authors')
        self.pubtitle = kwargs.get('title')
        self.doi      = kwargs.get('doi')
        self.pubdate  = kwargs.get('pubdate')
        self.pubyear  = kwargs.get('pubyear')
        self.journal_name = kwargs.get('journal_name')

        self._addbutton = ControlButton(
            'Add button',
            label_visible=False,
            visible=False,
            default=self.__addbutton_evt
        )

        super().__init__(*args, **kwargs)

        self._list.filter_event = self.__list_changed_evt

        self.formset = ['_details', '_list', '_addbutton']


    def get_toolbar_buttons(self, *args, **kwargs):
        return []

    def get_queryset(self, request, qs):
        return ModelAdminWidget.get_queryset(self, request, qs)

    def __addbutton_evt(self):
        self.show_create_form()

        form = self._details.value
        form.publication_title.value = self.pubtitle
        form.publication_year.value  = self.pubyear
        try:
            form.publication_publish.value = parse_date(self.pubdate)
        except:
            pass
        journals = Journal.objects.filter(
            Q(journal_name=self.journal_name) | Q(journalalias__name=self.journal_name)
        )
        journal = journals[0]
        form.journal.value             = journal.pk
        form.publication_doi.value     = self.doi
        form.publication_authors.value = self.authors

        people = []
        authors = AuthorAlias.objects.filter(name__in=self.authors.split(';'))
        form.authors.value = [ a.person.pk for a in authors]

        self._addbutton.hide()


    def __list_changed_evt(self):

        if self._list.value.count()==0:
            self._addbutton.show()
        else:
            self._addbutton.hide()

    @classmethod
    def has_permissions(cls, user):
        if user.is_superuser:
            return True

        return user.groups.filter(
            permissions__codename__in=['app_access_imp_pub']
        ).exists()
