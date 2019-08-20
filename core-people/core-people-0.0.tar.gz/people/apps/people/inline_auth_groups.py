from django.contrib.auth.models import User, Group
from people.models import Person
from pyforms_web.widgets.django import ModelFormWidget, ModelAdminWidget
from django.conf import settings

class UserAuthGroupsForm(ModelFormWidget):
    """Minimalistic User form only able to modify User groups."""
    MODEL = User
    FIELDSETS = ['groups']

    def __init__(self, *args, **kwargs):
        """
        Since we are coming from AuthGroup model, we need to
        redirect the PKs before showing the form.
        """
        person = Person.objects.get(pk=kwargs['parent_pk'])
        user   = person.auth_user
        kwargs['pk']    = user.pk
        kwargs['model'] = self.MODEL

        super().__init__(*args, **kwargs)


class AuthGroupsInline(ModelAdminWidget):
    MODEL = Group
    TITLE = 'Django Authorization Groups'

    EDITFORM_CLASS = UserAuthGroupsForm

    LIST_DISPLAY = ['name']

    AUTHORIZED_GROUPS = ['superuser', settings.APP_PROFILE_HR_PEOPLE]

    def get_queryset(self, request, queryset):
        person = Person.objects.get(pk=self.parent_pk)
        user = person.auth_user
        return user.groups.all()

    def has_add_permissions(self):
        # should always be False, use the Django Admin to manage these groups
        return False

    def has_remove_permissions(self, obj):
        # should always be False, use the Django Admin to manage these groups
        return False
