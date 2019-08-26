from confapp import conf
from pyforms.basewidget import segment
from pyforms_web.widgets.django import ModelAdminWidget


from research.models import AuthorAlias

class AuthorsAliasListWidget(ModelAdminWidget):
    """
    """
    UID = 'authors-alias'
    TITLE = 'Authors alias'

    MODEL = AuthorAlias

    ###########################################################################
    # ORQUESTRA CONFIGURATION

    LAYOUT_POSITION = conf.ORQUESTRA_HOME
    ORQUESTRA_MENU = 'left>PublicationsListWidget'
    ORQUESTRA_MENU_ORDER = 2
    ORQUESTRA_MENU_ICON = 'newspaper outline'
    #AUTHORIZED_GROUPS = ['superuser']

    ###########################################################################

    FIELDSETS = [
        segment(('name', 'person'))
    ]

    LIST_FILTER = ['person']

    SEARCH_FIELDS = [
        'name__icontains',
        'person__full_name__icontains'
    ]

    LIST_DISPLAY = [
        'name',
        'person'
    ]

    @classmethod
    def has_permissions(cls, user):
        if user.is_superuser:
            return True

        return user.groups.filter(
            permissions__codename__in=['app_access_imp_pub']
        ).exists()