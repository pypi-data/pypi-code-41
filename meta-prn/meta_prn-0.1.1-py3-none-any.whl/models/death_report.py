from django.db import models
from edc_action_item.managers import (
    ActionIdentifierSiteManager,
    ActionIdentifierManager,
)
from edc_action_item.models import ActionModelMixin
from edc_constants.choices import YES_NO
from edc_identifier.model_mixins import TrackingModelMixin
from edc_model.models import BaseUuidModel
from edc_model.validators import datetime_not_future
from edc_protocol.validators import datetime_not_before_study_start
from edc_sites.models import SiteModelMixin
from edc_utils import get_utcnow
from django_crypto_fields.fields.encrypted_text_field import EncryptedTextField
from edc_model_fields.fields import OtherCharField

from ..constants import DEATH_REPORT_ACTION
from ..choices import CAUSE_OF_DEATH, INFORMANT_RELATIONSHIP, DEATH_LOCATIONS


class DeathReport(SiteModelMixin, ActionModelMixin, TrackingModelMixin, BaseUuidModel):

    action_name = DEATH_REPORT_ACTION

    tracking_identifier_prefix = "DR"

    subject_identifier = models.CharField(max_length=50, unique=True)

    report_datetime = models.DateTimeField(
        verbose_name="Report Date",
        validators=[datetime_not_before_study_start, datetime_not_future],
        default=get_utcnow,
    )

    death_datetime = models.DateTimeField(
        validators=[datetime_not_future], verbose_name="Date and Time of Death"
    )

    death_location_type = models.CharField(
        verbose_name="Where did the participant die?",
        max_length=50,
        choices=DEATH_LOCATIONS,
    )

    death_location_name = models.CharField(
        verbose_name="If death occurred at hospital / clinic, please give name of the facility",
        max_length=150,
        null=True,
        blank=True,
    )

    informant_contacts = EncryptedTextField(null=True, blank=True)

    informant_relationship = models.CharField(
        max_length=50,
        choices=INFORMANT_RELATIONSHIP,
        verbose_name="Informants relationship to the participant?",
    )

    other_informant_relationship = OtherCharField()

    death_certificate = models.CharField(
        verbose_name="Is a death certificate is available?",
        max_length=15,
        choices=YES_NO,
    )

    cause_of_death = models.CharField(
        max_length=50,
        choices=CAUSE_OF_DEATH,
        verbose_name="Primary cause of death",
        help_text=(
            "Primary cause of death in the opinion of the "
            "local study doctor and local PI"
        ),
    )

    cause_of_death_other = models.CharField(
        max_length=100,
        blank=True,
        null=True,
        verbose_name='If "Other" above, please specify',
    )

    secondary_cause_of_death = models.CharField(
        max_length=50,
        choices=CAUSE_OF_DEATH,
        verbose_name=("Secondary cause of death"),
        help_text=(
            "Secondary cause of death in the opinion of the "
            "local study doctor and local PI"
        ),
    )

    secondary_cause_of_death_other = models.CharField(
        max_length=100,
        blank=True,
        null=True,
        verbose_name='If "Other" above, please specify',
    )

    narrative = models.TextField(verbose_name="Narrative")

    on_site = ActionIdentifierSiteManager()

    objects = ActionIdentifierManager()

    def natural_key(self):
        return (self.action_identifier,)

    class Meta:
        verbose_name = "Death Report"
        indexes = [
            models.Index(
                fields=["subject_identifier", "action_identifier", "site", "id"]
            )
        ]
