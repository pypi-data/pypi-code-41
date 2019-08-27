# Imports from Django.
from django.contrib import admin


class ElectionTypeAdmin(admin.ModelAdmin):
    list_display = ("label", "ap_code")
    ordering = ("label",)
    readonly_fields = ("uid",)

    fieldsets = (
        (
            "Names and labeling",
            {"fields": ("label", "short_label", "ap_code")},
        ),
        (
            "Election information",
            {"fields": ("number_of_winners", "winning_threshold")},
        ),
        ("Record locators", {"fields": ("slug", "uid")}),
    )
