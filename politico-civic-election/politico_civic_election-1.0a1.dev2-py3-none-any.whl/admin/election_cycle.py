# Imports from Django.
from django.contrib import admin


class ElectionCycleAdmin(admin.ModelAdmin):
    list_display = ("name",)
    ordering = ("-name",)
    readonly_fields = ("uid", "slug")

    fieldsets = (
        ("Names and labeling", {"fields": ("name",)}),
        ("Record locators", {"fields": ("uid", "slug")}),
    )
