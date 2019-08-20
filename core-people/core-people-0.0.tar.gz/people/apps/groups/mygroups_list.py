from confapp import conf
from .groups_list import GroupsListApp

class MyGroupsApp(GroupsListApp):

    UID = 'my-groups'
    LAYOUT_POSITION = conf.ORQUESTRA_HOME

    ORQUESTRA_MENU = 'left'
    ORQUESTRA_MENU_ORDER = 10
    ORQUESTRA_MENU_ICON = 'rocket'

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)