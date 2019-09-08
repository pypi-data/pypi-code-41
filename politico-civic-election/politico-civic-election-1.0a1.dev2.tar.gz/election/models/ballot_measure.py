# Imports from Django.
from django.db import models


# Imports from other dependencies.
from civic_utils.models import CivicBaseModel
from civic_utils.models import UniqueIdentifierMixin
from geography.models import Division


class BallotMeasure(UniqueIdentifierMixin, CivicBaseModel):
    """A ballot measure."""

    natural_key_fields = ["division", "election_day", "number"]
    uid_prefix = "ballot_measure"
    uid_base_field = "number"
    default_serializer = "election.serializers.BallotMeasureSerializer"

    label = models.CharField(max_length=255, blank=True)
    short_label = models.CharField(max_length=50, null=True, blank=True)

    question = models.TextField()
    division = models.ForeignKey(
        Division, related_name="ballot_measures", on_delete=models.PROTECT
    )
    number = models.CharField(max_length=3)
    election_day = models.ForeignKey(
        "ElectionDay", related_name="ballot_measures", on_delete=models.PROTECT
    )

    class Meta:
        unique_together = ("division", "election_day", "number")

    def __str__(self):
        return self.uid

    def save(self, *args, **kwargs):
        """
        **uid field**: :code:`ballot_measure:{number}`
        **identifier**: :code:`<division uid>__<election day uid>__<this uid>`
        """
        self.generate_unique_identifier(always_overwrite_uid=True)

        super(BallotMeasure, self).save(*args, **kwargs)

    def get_uid_prefix(self):
        return (
            f"{self.division.uid}__{self.election_day.uid}__{self.uid_prefix}"
        )
