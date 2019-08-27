# Imports from Django.
from django.db import models


# Imports from other dependencies.
from civic_utils.models import CivicBaseModel
from civic_utils.models import UniqueIdentifierMixin
from civic_utils.models import UUIDMixin


class BallotAnswer(UniqueIdentifierMixin, UUIDMixin, CivicBaseModel):
    """An answer to a ballot question."""

    natural_key_fields = ["ballot_measure", "answer"]
    # natural_key_fields = ["ballot_measure", "priority"]
    uid_prefix = "ballot_answer"
    uid_base_field = "answer"
    default_serializer = "election.serializers.BallotAnswerSerializer"

    label = models.CharField(max_length=255, blank=True)
    short_label = models.CharField(max_length=50, null=True, blank=True)

    answer = models.TextField()
    winner = models.BooleanField(default=False)
    ballot_measure = models.ForeignKey(
        "BallotMeasure", on_delete=models.CASCADE
    )
    # priority = models.PositiveSmallIntegerField(default=10)

    def save(self, *args, **kwargs):
        """
        **uid field**: :code:`ballot_answer:{answer}`
        **identifier**: :code:`<ballot measure uid>__<this uid>`
        """
        self.generate_unique_identifier(always_overwrite_uid=True)

        super(BallotAnswer, self).save(*args, **kwargs)

    def get_uid_prefix(self):
        return f"{self.ballot_measure.uid}__{self.uid_prefix}"
