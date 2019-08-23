from confapp import conf
from pyforms_web.widgets.django import ModelAdminWidget

from people.models import Group as ResearchGroup

from .groups_form import GroupFormApp


class GroupsListApp(ModelAdminWidget):
    """
    """
    UID = 'groups'
    TITLE = 'Groups'

    MODEL = ResearchGroup

    ORQUESTRA_MENU = 'middle-left>HRDashboard'
    ORQUESTRA_MENU_ICON = 'rocket'
    ORQUESTRA_MENU_ORDER = 10

    LAYOUT_POSITION = conf.ORQUESTRA_HOME

    USE_DETAILS_TO_EDIT = False

    EDITFORM_CLASS = GroupFormApp

    LIST_DISPLAY = [
        'name',
        'subject',
        'responsible',
        'type',
    ]

    LIST_FILTER = ['type']

    SEARCH_FIELDS = ['name__icontains']

    @classmethod
    def has_permissions(cls, user):
        if user.is_superuser:
            return True

        # user is allowed if Coordinator / Admin / Manager of any group
        for group in user.groups.all():
            parts = group.name.split(': ')
            if (
                len(parts) == 3 and
                parts[0] == 'PROFILE' and
                parts[1] in ('Group Coordinator',
                             'Group Admin',
                             'Group Manager')
            ):
                return True
        else:
            return False
