# Imports from Django.
from django.contrib import admin
from django.utils.translation import gettext_lazy as _


# Imports from other dependencies.
from government.models import Party


# Imports from election.
from election.models import ElectionCycle


class PartyFilter(admin.SimpleListFilter):
    title = _("party")
    parameter_name = "party"

    def lookups(self, request, model_admin):
        return [
            (party.ap_code, _(party.__str__()))
            for party in Party.objects.all()
        ]

    def queryset(self, request, queryset):
        if not self.value():
            return queryset
        return queryset.filter(party__ap_code=self.value())


class CycleFilter(admin.SimpleListFilter):
    title = _("cycle")
    parameter_name = "cycle"

    def lookups(self, request, model_admin):
        return [
            (cycle.slug, _(cycle.name))
            for cycle in ElectionCycle.objects.all()
        ]

    def queryset(self, request, queryset):
        if not self.value():
            return queryset
        return queryset.filter(race__cycle__name=self.value())


class CandidateAdmin(admin.ModelAdmin):
    list_display = ("get_person", "get_race", "get_party")
    search_fields = ("person__full_name",)
    list_filter = (PartyFilter, CycleFilter)
    readonly_fields = ("uid",)

    fieldsets = (
        (
            "Relationships",
            {"fields": ("person", "party", "race", "top_of_ticket")},
        ),
        (
            "Identification",
            {"fields": ("ap_candidate_id", "incumbent", "prospective")},
        ),
        ("Record locators", {"fields": ("uid",)}),
    )

    def get_person(self, obj):
        return obj.person.full_name

    def get_race(self, obj):
        return obj.race.label

    def get_party(self, obj):
        return obj.party.label

    get_person.short_description = "Name"
    get_race.short_description = "Race"
    get_party.short_description = "Party"
