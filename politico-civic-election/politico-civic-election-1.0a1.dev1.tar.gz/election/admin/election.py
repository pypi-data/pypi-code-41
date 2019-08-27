# Imports from Django.
from django.contrib import admin
from django import forms


# Imports from other dependencies.
from government.models import Party


# Imports from election.
from election.models import CandidateElection
from election.models import ElectionDay
from election.models import ElectionType


class CustomModelChoiceField(forms.ModelChoiceField):
    def label_from_instance(self, obj):
        if hasattr(obj, "name"):
            return obj.name
        elif hasattr(obj, "date"):
            return obj.date
        else:
            return obj.label


class CandidateElectionInline(admin.StackedInline):
    model = CandidateElection
    extra = 0


class ElectionAdminForm(forms.ModelForm):
    election_type = CustomModelChoiceField(queryset=ElectionType.objects.all())
    election_day = CustomModelChoiceField(queryset=ElectionDay.objects.all())
    party = CustomModelChoiceField(
        queryset=Party.objects.all(), required=False
    )


class ElectionAdmin(admin.ModelAdmin):
    form = ElectionAdminForm
    list_display = (
        "get_office",
        "election_date",
        "get_election_type",
        "get_party",
        "special",
    )
    list_filter = (
        "election_day__date",
        "race__special",
        "election_type__label",
    )
    ordering = ("election_day__date", "division__label", "party__label")
    search_fields = ("race__label", "election_day__date", "election_day__slug")
    autocomplete_fields = ["race", "division"]
    inlines = [CandidateElectionInline]
    readonly_fields = ("uid",)
    fieldsets = (
        (
            "Relationships",
            {
                "fields": (
                    "race",
                    "election_type",
                    "election_day",
                    "division",
                    "party",
                )
            },
        ),
        ("Record locators", {"fields": ("uid",)}),
    )

    def get_office(self, obj):
        return obj.race.office.label

    def election_date(self, obj):
        return obj.election_day.date

    def get_election_type(self, obj):
        return obj.election_type.label

    def get_party(self, obj):
        if obj.party:
            return obj.party.label
        else:
            return None

    def special(self, obj):
        return obj.race.special

    get_office.short_description = "Office"
    get_party.short_description = "Primary Party"
    get_election_type.short_description = "Election Type"
