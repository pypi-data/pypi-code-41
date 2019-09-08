# Imports from Django.
from django.contrib import admin


# Imports from election.
from election.admin.candidate import CandidateAdmin
from election.admin.candidate_election import CandidateElectionAdmin
from election.admin.election import ElectionAdmin
from election.admin.election_cycle import ElectionCycleAdmin
from election.admin.election_day import ElectionDayAdmin
from election.admin.election_event import ElectionEventAdmin
from election.admin.election_type import ElectionTypeAdmin
from election.admin.race import RaceAdmin
from election.models import Candidate
from election.models import CandidateElection
from election.models import Election
from election.models import ElectionCycle
from election.models import ElectionDay
from election.models import ElectionEvent
from election.models import ElectionType
from election.models import Race


admin.site.register(Race, RaceAdmin)
admin.site.register(Election, ElectionAdmin)
admin.site.register(CandidateElection, CandidateElectionAdmin)
admin.site.register(ElectionDay, ElectionDayAdmin)
admin.site.register(ElectionEvent, ElectionEventAdmin)
admin.site.register(ElectionType, ElectionTypeAdmin)
admin.site.register(ElectionCycle, ElectionCycleAdmin)
admin.site.register(Candidate, CandidateAdmin)
