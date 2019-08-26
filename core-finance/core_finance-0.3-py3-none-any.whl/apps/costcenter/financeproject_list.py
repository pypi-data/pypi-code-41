from django.conf import settings

from confapp import conf
from pyforms.controls import ControlCheckBox
from pyforms_web.web.middleware import PyFormsMiddleware
from pyforms_web.widgets.django import ModelAdminWidget

from finance.models import Project

from .financeproject_form import FinanceProjectFormApp


class FinanceProjectListApp(ModelAdminWidget):

    TITLE = 'Finance projects'

    MODEL = Project

    AUTHORIZED_GROUPS = ['superuser', settings.PROFILE_LAB_ADMIN]

    LIST_DISPLAY = [
        'code',
        'name',
        'start_date',
        'end_date',
    ]

    ADDFORM_CLASS = FinanceProjectFormApp
    EDITFORM_CLASS = FinanceProjectFormApp
    USE_DETAILS_TO_EDIT = False

    # ORQUESTRA CONFIGURATION
    # =========================================================================
    LAYOUT_POSITION = conf.ORQUESTRA_HOME
    # =========================================================================

    def __init__(self, *args, **kwargs):

        self._active = ControlCheckBox(
            'Active',
            default=True,
            label_visible=False,
            changed_event=self.populate_list,
            field_style='text-align:right;',
        )

        super().__init__(*args, **kwargs)

    def get_toolbar_buttons(self, has_add_permission=False):
        return tuple(
            (['_add_btn'] if has_add_permission else []) + [
                '_active',
            ]
        )

    def get_queryset(self, request, qs):

        if self._active.value:
            qs = qs.active()

        return qs

    def has_update_permissions(self, obj):
        if obj and obj.code == 'NO TRACK':
            return False
        else:
            return True

    def has_remove_permissions(self, obj):
        """Only superusers may delete these objects."""
        user = PyFormsMiddleware.user()
        return user.is_superuser
