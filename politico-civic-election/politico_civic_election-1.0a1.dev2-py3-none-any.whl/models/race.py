# Imports from Django.
from django.db import models


# Imports from other dependencies.
from civic_utils.models import CivicBaseModel
from civic_utils.models import CommonIdentifiersMixin
from government.models import Office


class Race(CommonIdentifiersMixin, CivicBaseModel):
    """
    A race for an office comprised of one or many elections.
    """

    SPECIAL_RACE_SLUG = "Special"
    STANDARD_RACE_SLUG = "Standard"

    natural_key_fields = ["office", "cycle", "special"]
    uid_prefix = "race"
    default_serializer = "election.serializers.RaceSerializer"

    label = models.CharField(max_length=255, blank=True)
    short_label = models.CharField(max_length=50, null=True, blank=True)
    description = models.TextField(blank=True, null=True)

    office = models.ForeignKey(
        Office, related_name="races", on_delete=models.PROTECT
    )
    cycle = models.ForeignKey(
        "ElectionCycle", related_name="races", on_delete=models.PROTECT
    )
    special = models.BooleanField(default=False)

    def __str__(self):
        return self.label

    def save(self, *args, **kwargs):
        """
        **uid field**: :code:`race:{'standard' or 'special'}`
        **identifier**: :code:`<office uid>__<cycle uid>__<this uid>`
        """
        name_label = f"{self.cycle.name} {self.office.label}"

        if self.special:
            name_label = f"{name_label} {self.SPECIAL_RACE_SLUG}"

        self.label = name_label

        self.generate_common_identifiers(
            always_overwrite_slug=False, always_overwrite_uid=True
        )

        super(Race, self).save(*args, **kwargs)

    def get_uid_base_field(self):
        return self.label

    def get_uid_prefix(self):
        return f"{self.office.uid}__{self.cycle.uid}__{self.uid_prefix}"

    def get_uid_suffix(self):
        if self.special:
            return self.SPECIAL_RACE_SLUG.lower()

        return self.STANDARD_RACE_SLUG.lower()
