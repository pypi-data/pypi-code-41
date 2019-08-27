# Imports from Django.
from django.db import models


# Imports from other dependencies.
from civic_utils.models import CivicBaseModel
from civic_utils.models import CommonIdentifiersMixin
from geography.models import Division
from government.models import Body


# Imports from election.
from election.models import Election
from election.models import ElectionDay


class ElectionEvent(CommonIdentifiersMixin, CivicBaseModel):
    """A statewide election event"""

    natural_key_fields = [
        "division",
        "election_day",
        "event_type",
        "dem_primary_type",
        "gop_primary_type",
    ]
    uid_prefix = "electionevent"
    default_serializer = "election.serializers.ElectionEventSerializer"

    PRIMARIES = "Primaries"
    PRIMARIES_RUNOFF = "Primaries Runoff"
    GENERAL = "General"
    GENERAL_RUNOFF = "General Runoff"
    SPECIAL_PRIMARY = "Special Primary"
    SPECIAL_RUNOFF = "Special Runoff"
    SPECIAL_GENERAL = "Special General"

    EVENT_TYPES = (
        (PRIMARIES, "Primaries"),
        (PRIMARIES_RUNOFF, "Primaries Runoff"),
        (GENERAL, "General"),
        (GENERAL_RUNOFF, "General Runoff"),
        (SPECIAL_PRIMARY, "Special Primary"),
        (SPECIAL_RUNOFF, "Special Runoff"),
        (SPECIAL_GENERAL, "Special General"),
    )

    OPEN = "open"
    SEMI_OPEN = "semi-open"
    SEMI_CLOSED = "semi-closed"
    CLOSED = "closed"
    JUNGLE = "jungle"

    PRIMARY_TYPES = (
        (OPEN, "Open"),
        (SEMI_OPEN, "Semi-open"),
        (SEMI_CLOSED, "Semi-closed"),
        (CLOSED, "Closed"),
        (JUNGLE, "Jungle"),
    )

    label = models.CharField(max_length=100)
    event_type = models.CharField(max_length=50, choices=EVENT_TYPES)
    dem_primary_type = models.CharField(
        max_length=50, choices=PRIMARY_TYPES, null=True, blank=True
    )
    gop_primary_type = models.CharField(
        max_length=50, choices=PRIMARY_TYPES, null=True, blank=True
    )
    election_day = models.ForeignKey(ElectionDay, on_delete=models.PROTECT)
    division = models.ForeignKey(Division, on_delete=models.PROTECT)
    early_vote_start = models.DateField(null=True, blank=True)
    early_vote_close = models.DateField(null=True, blank=True)
    vote_by_mail_application_deadline = models.DateField(null=True, blank=True)
    vote_by_mail_ballot_deadline = models.DateField(null=True, blank=True)
    online_registration_deadline = models.DateField(null=True, blank=True)
    registration_deadline = models.DateField(null=True, blank=True)
    poll_closing_time = models.DateTimeField(null=True, blank=True)

    class Meta:
        unique_together = (
            "division",
            "election_day",
            "event_type",
            "dem_primary_type",
            "gop_primary_type",
        )

    def __str__(self):
        return self.label

    def save(self, *args, **kwargs):
        """
        **uid field**: :code:`electionevent:{event type}[({party types})]`
        **identifier**: :code:`<division uid>__<election day uid>__<this uid>`
        """
        self.generate_common_identifiers(
            always_overwrite_slug=True, always_overwrite_uid=True
        )

        super(ElectionEvent, self).save(*args, **kwargs)

    def get_uid_base_field(self):
        if self.dem_primary_type and self.gop_primary_type:
            return (
                f"{self.event_type}"
                f"(DEM-{self.dem_primary_type},GOP-{self.gop_primary_type})"
            )
        elif self.dem_primary_type:
            return f"{self.event_type}(DEM-{self.dem_primary_type})"
        elif self.gop_primary_type:
            return f"{self.event_type}(GOP-{self.gop_primary_type})"

        return self.event_type

    def get_uid_prefix(self):
        f"{self.division.uid}__{self.election_day.uid}__{self.uid_prefix}"

    def get_statewide_offices(self):
        statewide_elections = Election.objects.filter(
            election_day=self.election_day, division=self.division
        )

        offices = []
        for election in statewide_elections:
            offices.append(election.race.office)

        return set(offices)

    def get_district_offices(self):
        district_elections = Election.objects.filter(
            election_day=self.election_day, division__parent=self.division
        )

        offices = []
        for election in district_elections:
            offices.append(election.race.office)

        return set(offices)

    def has_senate_election(self):
        offices = self.get_statewide_offices()
        senate = Body.objects.get(label="U.S. Senate")

        for office in offices:
            if office.body == senate:
                return True

        return False

    def has_house_election(self):
        offices = self.get_district_offices()
        house = Body.objects.get(label="U.S. House of Representatives")

        for office in offices:
            if office.body == house:
                return True

        return False

    def has_governor_election(self):
        offices = self.get_statewide_offices()
        for office in offices:
            if office.slug.endswith("governor"):
                return True

        return False
