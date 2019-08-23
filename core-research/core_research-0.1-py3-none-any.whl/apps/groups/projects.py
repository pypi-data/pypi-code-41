from pyforms.controls import ControlCheckBox
from pyforms_web.widgets.django import ModelAdminWidget

from research.models import Project


class ProjectsListWidget(ModelAdminWidget):

    MODEL = Project

    LIST_DISPLAY = [
        'project_name',
    ]

    FIELDSETS = [
        'project_name',
        'project_desc',
        'project_collaborators',
        (
            'project_active',
            'project_funding',
            'project_order',
        ),
    ]

    def __init__(self, *args, **kwargs):

        self._active_filter = ControlCheckBox(
            'Only active',
            default=True,
            label_visible=False,
            changed_event=self.populate_list,
        )
        super().__init__(*args, **kwargs)

    def get_toolbar_buttons(self, has_add_permission=False):
        return ('_add_btn' if has_add_permission else None, '_active_filter')

    def get_queryset(self, request, qs):
        if self._active_filter.value:
            qs = qs.filter(project_active=True)
        return qs
