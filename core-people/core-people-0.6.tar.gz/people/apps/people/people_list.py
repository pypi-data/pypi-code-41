from permissions.models import Permission
from .humanresources_list import HumanResourcesList
from .people_form import PeopleFormWidget
from django.contrib.contenttypes.models import ContentType

class PeopleListWidget(HumanResourcesList):
    """
    People app for group responsibles.
    """
    UID   = 'people'
    TITLE = 'People'

    LIST_DISPLAY = (
        'thumbnail_80x80',
        'full_name',
        'email',
        'position',
    )

    ORQUESTRA_MENU = 'left'

    EDITFORM_CLASS = PeopleFormWidget

    @classmethod
    def has_permissions(cls, user):
        if user.is_superuser: return True

        # Search for the user groups with certain permissions
        contenttype = ContentType.objects.get_for_model(cls.MODEL)
        authgroups  = user.groups.filter(permissions__content_type=contenttype)
        authgroups  = authgroups.filter(permissions__codename='app_access_people')
        return Permission.objects.filter(auth_group__in=authgroups).exists()

    def has_add_permissions(self):
        return False

    def has_remove_permissions(self, obj):
        return False

    def get_queryset(self, request, qs):
        qs = qs.active()

        if self._nocontract_filter.value:
            qs = qs.noactivecontract()

        if self._noproposal_filter.value:
            qs = qs.noactiveproposal()

        return qs

    def get_toolbar_buttons(self, has_add_permission=False):
        return (
            '_add_btn' if has_add_permission else None,
            '_nocontract_filter',
            '_noproposal_filter',
        )
