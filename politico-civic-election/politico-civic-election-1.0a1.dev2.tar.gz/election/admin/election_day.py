# Imports from Django.
from django.contrib import admin
from django import forms


# Imports from election.
from election.models import ElectionCycle


class CustomModelChoiceField(forms.ModelChoiceField):
    def label_from_instance(self, obj):
        return obj.name


class ElectionDayAdminForm(forms.ModelForm):
    cycle = CustomModelChoiceField(queryset=ElectionCycle.objects.all())


class ElectionDayAdmin(admin.ModelAdmin):
    form = ElectionDayAdminForm
    list_display = ("date",)
    ordering = ("date",)
    readonly_fields = ("uid", "slug")

    fieldsets = (
        ("Names and labeling", {"fields": ("date",)}),
        ("Relationships", {"fields": ("cycle",)}),
        ("Record locators", {"fields": ("slug", "uid")}),
    )
