from django.contrib.auth.admin import UserAdmin
from django.utils.translation import gettext_lazy as _

from .forms import UserAddWithoutPasswordForm


class SolarluxUserAdmin(UserAdmin):
    list_display = (
        "email",
        "title",
        "first_name",
        "last_name",
        "customer_no",
        "customer_name",
        "is_staff",
    )
    list_filter = ("is_staff", "is_superuser", "is_active", "groups")
    search_fields = ("first_name", "last_name", "email")
    ordering = ("email",)
    filter_horizontal = ("groups", "user_permissions")
    add_form = UserAddWithoutPasswordForm

    fieldsets = None

    add_fieldsets = (
        (None, {
            'classes': ('wide',),
            'fields': ('username', ),
        }),
    )
