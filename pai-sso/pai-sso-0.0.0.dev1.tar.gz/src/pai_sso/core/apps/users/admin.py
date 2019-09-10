from django.contrib import admin

from django.contrib.auth.admin import UserAdmin as BaseUserAdmin
# from django.contrib.auth.models import User

from .models import User
from .forms import UserChangeForm, UserCreationForm

from ...common import PROFILE_FIELDS

# Define a new User admin
class UserAdmin(BaseUserAdmin):
    form = UserChangeForm
    add_form = UserCreationForm

    list_display = ('username', 'email', 'first_name', 'last_name', 'is_staff', 'last_login', 'role')
    list_filter = ('is_staff', 'is_superuser', 'is_active', 'groups', 'last_login')

    fields = ('username', ) + PROFILE_FIELDS
    fieldsets = None

    add_fieldsets = (
        (None, {
            'classes': ('wide',),
            'fields': ('username', 'email', 'password1', 'password2'),
        }),
    )

# Re-register UserAdmin
# admin.site.unregister(User)
admin.site.register(User, UserAdmin)
