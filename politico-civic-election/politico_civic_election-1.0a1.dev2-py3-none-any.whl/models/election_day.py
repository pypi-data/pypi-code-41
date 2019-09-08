# Imports from Django.
from django.db import models


# Imports from other dependencies.
from civic_utils.models import CivicBaseModel
from civic_utils.models import CommonIdentifiersMixin


class ElectionDay(CommonIdentifiersMixin, CivicBaseModel):
    """
    A day on which one or many elections can be held.
    """

    natural_key_fields = ["cycle", "date"]
    uid_prefix = "date"
    default_serializer = "election.serializers.ElectionDaySerializer"

    date = models.DateField(unique=True)

    cycle = models.ForeignKey(
        "ElectionCycle",
        related_name="elections_days",
        on_delete=models.PROTECT,
    )

    def __str__(self):
        return self.uid

    def save(self, *args, **kwargs):
        """
        **uid field**: :code:`date:{date}`
        **identifier**: :code:`<cycle uid>__<this uid>`
        """
        self.generate_common_identifiers(
            always_overwrite_slug=True, always_overwrite_uid=True
        )

        super(ElectionDay, self).save(*args, **kwargs)

    def get_uid_base_field(self):
        return self.date.strftime("%Y-%m-%d")

    def get_uid_prefix(self):
        return f"{self.cycle.uid}__{self.uid_prefix}"

    def special_election_datestring(self):
        """
        Formatted date string used in URL for special elections.
        """
        return self.date.strftime("%b-%d").lower()
