from django.conf import settings

from pyforms.controls import ControlCheckBox
from pyforms_web.web.middleware import PyFormsMiddleware
from pyforms_web.widgets.django import ModelAdminWidget

from people.models import GroupMembership


class MembershipsListWidget(ModelAdminWidget):

    MODEL = GroupMembership

    LIST_ROWS_PER_PAGE = 50

    LIST_DISPLAY = [
        'person',
        'position',
        'date_joined',
        'date_left',
    ]

    FIELDSETS = [
        ('person', 'position', 'date_joined', 'date_left'),
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
            qs = qs.active()
        return qs

    def has_add_permissions(self):
        user = PyFormsMiddleware.user()
        user_is_hr = settings.PROFILE_HUMAN_RESOURCES in user.groups.all()
        return user.is_superuser or user_is_hr

    def has_view_permissions(self, obj):
        user = PyFormsMiddleware.user()
        user_is_hr = settings.PROFILE_HUMAN_RESOURCES in user.groups.all()
        return user.is_superuser or user_is_hr

    def has_update_permissions(self, obj):
        user = PyFormsMiddleware.user()
        user_is_hr = settings.PROFILE_HUMAN_RESOURCES in user.groups.all()
        return user.is_superuser or user_is_hr

    def has_remove_permissions(self, obj):
        user = PyFormsMiddleware.user()
        user_is_hr = settings.PROFILE_HUMAN_RESOURCES in user.groups.all()
        return user.is_superuser or user_is_hr
