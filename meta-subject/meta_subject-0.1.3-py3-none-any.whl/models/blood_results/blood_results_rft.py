from django.db import models
from django.db.models.deletion import PROTECT
from edc_constants.choices import YES_NO
from edc_model.models import BaseUuidModel
from edc_model.validators import datetime_not_future
from edc_reportable import MILLIGRAMS_PER_DECILITER
from edc_reportable.choices import REPORTABLE

from ...constants import BLOOD_RESULTS_RFT_ACTION
from ..subject_requisition import SubjectRequisition
from .blood_results_model_mixin import BloodResultsModelMixin


class BloodResultsRft(BloodResultsModelMixin, BaseUuidModel):

    action_name = BLOOD_RESULTS_RFT_ACTION

    tracking_identifier_prefix = "RF"

    rft_requisition = models.ForeignKey(
        SubjectRequisition,
        on_delete=PROTECT,
        related_name="ft",
        verbose_name="Requisition",
        null=True,
        blank=True,
        help_text=(
            "Start typing the requisition identifier or select one from this visit"
        ),
    )

    rft_assay_datetime = models.DateTimeField(
        verbose_name="Result Report Date and Time",
        validators=[datetime_not_future],
        null=True,
        blank=True,
    )

    # Serum urea levels
    serum_urea = models.DecimalField(
        verbose_name="Serum Urea", decimal_places=2, max_digits=6, null=True, blank=True
    )

    serum_urea_units = models.CharField(
        verbose_name="units",
        max_length=10,
        choices=((MILLIGRAMS_PER_DECILITER, MILLIGRAMS_PER_DECILITER),),
        null=True,
        blank=True,
    )

    serum_urea_abnormal = models.CharField(
        verbose_name="abnormal", choices=YES_NO, max_length=25, null=True, blank=True
    )

    serum_urea_reportable = models.CharField(
        verbose_name="reportable",
        choices=REPORTABLE,
        max_length=25,
        null=True,
        blank=True,
    )

    # Serum creatinine levels
    serum_creat = models.DecimalField(
        verbose_name="Serum Creatinine",
        decimal_places=2,
        max_digits=6,
        null=True,
        blank=True,
    )

    serum_creat_units = models.CharField(
        verbose_name="units",
        max_length=10,
        choices=((MILLIGRAMS_PER_DECILITER, MILLIGRAMS_PER_DECILITER),),
        null=True,
        blank=True,
    )

    serum_creat_abnormal = models.CharField(
        verbose_name="abnormal", choices=YES_NO, max_length=25, null=True, blank=True
    )

    serum_creat_reportable = models.CharField(
        verbose_name="reportable",
        choices=REPORTABLE,
        max_length=25,
        null=True,
        blank=True,
    )

    # Serum uric acid levels
    serum_uric_acid = models.DecimalField(
        verbose_name="Serum Uric Acid",
        decimal_places=2,
        max_digits=6,
        null=True,
        blank=True,
    )

    serum_uric_acid_units = models.CharField(
        verbose_name="units",
        max_length=10,
        choices=((MILLIGRAMS_PER_DECILITER, MILLIGRAMS_PER_DECILITER),),
        null=True,
        blank=True,
    )

    serum_uric_acid_abnormal = models.CharField(
        verbose_name="abnormal", choices=YES_NO, max_length=25, null=True, blank=True
    )

    serum_uric_acid_reportable = models.CharField(
        verbose_name="reportable",
        choices=REPORTABLE,
        max_length=25,
        null=True,
        blank=True,
    )

    class Meta(BloodResultsModelMixin.Meta):
        verbose_name = "Blood Result: RFT"
        verbose_name_plural = "Blood Results: RFT"
