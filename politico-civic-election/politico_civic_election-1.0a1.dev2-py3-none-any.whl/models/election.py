# Imports from Django.
from django.db import models


# Imports from other dependencies.
from civic_utils.models import CivicBaseModel
from civic_utils.models import UniqueIdentifierMixin
from geography.models import Division
from government.models import Party


# Imports from election.
from election.models import CandidateElection


class Election(UniqueIdentifierMixin, CivicBaseModel):
    """
    A specific contest in a race held on a specific day.
    """

    natural_key_fields = ["race", "election_day", "party"]
    uid_prefix = "election"
    default_serializer = "election.serializers.ElectionSerializer"

    election_type = models.ForeignKey(
        "ElectionType", related_name="elections", on_delete=models.PROTECT
    )
    candidates = models.ManyToManyField(
        "Candidate", through="CandidateElection"
    )
    race = models.ForeignKey(
        "Race", related_name="elections", on_delete=models.PROTECT
    )
    party = models.ForeignKey(
        Party, null=True, blank=True, on_delete=models.PROTECT
    )
    election_day = models.ForeignKey(
        "ElectionDay", related_name="elections", on_delete=models.PROTECT
    )
    division = models.ForeignKey(
        Division, related_name="elections", on_delete=models.PROTECT
    )
    ap_election_id = models.CharField(max_length=10, blank=True, null=True)

    def __str__(self):
        return self.race.office.label

    def save(self, *args, **kwargs):
        """
        **uid field**: :code:`election:{election_day}[-{party}]`
        **identifier**: :code:`<race uid>__<this uid>`
        """
        self.generate_unique_identifier(always_overwrite_uid=True)

        super(Election, self).save(*args, **kwargs)

    def get_uid_prefix(self):
        return f"{self.race.uid}__{self.uid_prefix}"

    def get_uid_base_field(self):
        if self.party:
            return f"{self.election_day.slug}-{self.party.slug}"

        return self.election_day.slug

    def update_or_create_candidate(
        self, candidate, aggregable=True, uncontested=False
    ):
        """Create a CandidateElection."""
        candidate_election, c = CandidateElection.objects.update_or_create(
            candidate=candidate,
            election=self,
            defaults={"aggregable": aggregable, "uncontested": uncontested},
        )

        return candidate_election

    def delete_candidate(self, candidate):
        """Delete a CandidateElection."""
        CandidateElection.objects.filter(
            candidate=candidate, election=self
        ).delete()

    def get_candidates(self):
        """Get all CandidateElections for this election."""
        candidate_elections = CandidateElection.objects.filter(election=self)

        return [ce.candidate for ce in candidate_elections]

    def get_candidates_by_party(self):
        """
        Get CandidateElections serialized into an object with
        party-slug keys.
        """
        candidate_elections = CandidateElection.objects.filter(election=self)

        return {
            ce.candidate.party.slug: ce.candidate for ce in candidate_elections
        }

    def get_candidate_election(self, candidate):
        """Get CandidateElection for a Candidate in this election."""
        return CandidateElection.objects.get(
            candidate=candidate, election=self
        )

    def get_candidate_votes(self, candidate):
        """
        Get all votes attached to a CandidateElection for a Candidate in
        this election.
        """
        candidate_election = CandidateElection.objects.get(
            candidate=candidate, election=self
        )

        return candidate_election.votes.all()

    def get_votes(self):
        """
        Get all votes for this election.
        """
        candidate_elections = CandidateElection.objects.filter(election=self)

        votes = None
        for ce in candidate_elections:
            votes = votes | ce.votes.all()

        return votes

    def get_candidate_electoral_votes(self, candidate):
        """
        Get all electoral votes for a candidate in this election.
        """
        candidate_election = CandidateElection.objects.get(
            candidate=candidate, election=self
        )

        return candidate_election.electoral_votes.all()

    def get_electoral_votes(self):
        """
        Get all electoral votes for all candidates in this election.
        """
        candidate_elections = CandidateElection.objects.filter(election=self)

        electoral_votes = None
        for ce in candidate_elections:
            electoral_votes = electoral_votes | ce.electoral_votes.all()

        return electoral_votes

    def get_candidate_delegates(self, candidate):
        """
        Get all pledged delegates for a candidate in this election.
        """
        candidate_election = CandidateElection.objects.get(
            candidate=candidate, election=self
        )

        return candidate_election.delegates.all()

    def get_delegates(self):
        """
        Get all pledged delegates for any candidate in this election.
        """
        candidate_elections = CandidateElection.objects.filter(election=self)

        delegates = None
        for ce in candidate_elections:
            delegates = delegates | ce.delegates.all()

        return delegates
