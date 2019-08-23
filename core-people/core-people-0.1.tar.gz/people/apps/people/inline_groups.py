from people.models import GroupMembership
from pyforms_web.widgets.django import ModelAdminWidget


class GroupsInline(ModelAdminWidget):
    MODEL = GroupMembership
    TITLE = 'Groups'

    LIST_DISPLAY = ['group', 'position', 'date_joined', 'date_left']

    FIELDSETS = [
        ('group', 'position', 'date_joined', 'date_left')
    ]
