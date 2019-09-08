# Imports from Django.
from django.db import models


# Imports from other dependencies.
from civic_utils.models import CivicBaseModel
from civic_utils.models import UniqueIdentifierMixin
from civic_utils.models import UUIDMixin


class CandidateElection(UniqueIdentifierMixin, UUIDMixin, CivicBaseModel):
    """
    A CandidateElection represents the abstract relationship between a
    candidate and an election and carries properties like whether the
    candidate is uncontested or whether we aggregate their vote totals.
    """

    natural_key_fields = ["candidate", "election"]
    uid_prefix = "candidate_in_election"
    default_serializer = "election.serializers.CandidateElectionSerializer"

    candidate = models.ForeignKey(
        "Candidate",
        on_delete=models.CASCADE,
        related_name="candidate_elections",
    )
    election = models.ForeignKey(
        "Election",
        on_delete=models.CASCADE,
        related_name="candidate_elections",
    )
    aggregable = models.BooleanField(default=True)
    uncontested = models.BooleanField(default=False)

    class Meta:
        unique_together = (("candidate", "election"),)

    def save(self, *args, **kwargs):
        """
        **uid field**: :code:`candidate_in_election:{election slug}`
        **identifier**: :code:`<candidate uid>__<this uid>`
        """
        self.generate_unique_identifier(always_overwrite_uid=True)

        super(CandidateElection, self).save(*args, **kwargs)

    def get_uid_prefix(self):
        return "{self.candidate.uid}__{self.uid_prefix}"

    def get_uid_base_field(self):
        return self.election.get_uid_base_field()
