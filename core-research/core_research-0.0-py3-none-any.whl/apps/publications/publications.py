from confapp import conf
from pyforms.controls import ControlCheckBox
from pyforms.controls import ControlAutoComplete
from pyforms_web.widgets.django import ModelAdminWidget

from research.models import Publication

from people.models import Person, Group

from .publication_form import PublicationFormWidget


class PublicationsListWidget(ModelAdminWidget):
    """
    """
    UID = 'publications'
    TITLE = 'Publications'

    MODEL = Publication

    ###########################################################################
    # ORQUESTRA CONFIGURATION

    LAYOUT_POSITION = conf.ORQUESTRA_HOME_FULL
    ORQUESTRA_MENU = 'left'
    ORQUESTRA_MENU_ORDER = 20
    ORQUESTRA_MENU_ICON = 'newspaper outline yellow'
    # AUTHORIZED_GROUPS = ['superuser']
    ###########################################################################

    USE_DETAILS_TO_EDIT = False

    LIST_DISPLAY = [
        'publication_title',
        'journal',
        'publication_year',
        'publication_authors',
    ]

    SEARCH_FIELDS = [
        'publication_title__icontains',
        'publication_abstract__icontains',
        'publication_authors__icontains',
        'authors__full_name__icontains',
        'publication_doi__icontains'
    ]

    LIST_FILTER = [
        'pubtype',
        'publication_year',
        'journal',
        'publication_keypub',
    ]

    EDITFORM_CLASS = PublicationFormWidget

    def __init__(self, *args, **kwargs):

        self._show_all_filter = ControlCheckBox(
            'Show only my publications',
            default=True,
            label_visible=True,
            changed_event=self.populate_list
        )

        self._researchgroups = ControlAutoComplete(
            'Groups', 
            queryset=Group.objects.all(), 
            multiple=True,
            changed_event=self.populate_list
        )

        self._people = ControlAutoComplete(
            'People', 
            queryset=Person.objects.all(), 
            multiple=True,
            changed_event=self.populate_list
        )

        super().__init__(*args, **kwargs)

        self._add_btn.label_visible=True



    def get_toolbar_buttons(self, *args, **kwargs):
        add_btn = super().get_toolbar_buttons(*args, **kwargs)
        return (add_btn, '_show_all_filter', '_people','_researchgroups')

    def get_queryset(self, request, qs):
        
        if self._show_all_filter.value:
            qs = qs.is_author(user=request.user)

        if self._researchgroups.value:
            qs = qs.filter_research_groups(self._researchgroups.value)

        if self._people.value:
            qs = qs.filter_people(self._people.value)

        return qs
