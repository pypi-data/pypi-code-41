# Imports from python.


# Imports from Django.
from django.contrib import admin
from django import forms


# Imports from election.
from election.models import Candidate
from election.models import Election


class CustomModelChoiceField(forms.ModelChoiceField):
    def label_from_instance(self, obj):
        if hasattr(obj, "person"):
            return obj.person.full_name
        else:
            return obj.race.label


class CandidateElectionAdminForm(forms.ModelForm):
    candidate = CustomModelChoiceField(queryset=Candidate.objects.all())
    election = CustomModelChoiceField(queryset=Election.objects.all())


class CandidateElectionAdmin(admin.ModelAdmin):
    form = CandidateElectionAdminForm
    list_display = ("get_candidate", "get_election")
    search_fields = ("candidate__person__name", "election__race__label")

    def get_candidate(self, obj):
        return obj.candidate.person.full_name

    def get_election(self, obj):
        return obj.election.race.label

    get_candidate.short_description = "Candidate"
    get_election.short_description = "Election"
