from django.core.validators import MinValueValidator, MaxValueValidator
from django.db import models
from django.db.models.deletion import PROTECT
from edc_constants.choices import YES_NO
from edc_constants.constants import NOT_APPLICABLE
from edc_model.models import BaseUuidModel
from edc_model.validators import datetime_not_future
from edc_reportable import MILLIGRAMS_PER_DECILITER, MILLIMOLES_PER_LITER, PERCENT
from edc_reportable.choices import REPORTABLE


from ...constants import BLOOD_RESULTS_GLU_ACTION
from ...choices import FASTING_CHOICES
from ..subject_requisition import SubjectRequisition
from .blood_results_model_mixin import BloodResultsModelMixin


class BloodResultsGlu(BloodResultsModelMixin, BaseUuidModel):

    action_name = BLOOD_RESULTS_GLU_ACTION

    tracking_identifier_prefix = "GL"

    # blood glucose
    blood_glucose_requisition = models.ForeignKey(
        SubjectRequisition,
        on_delete=PROTECT,
        related_name="bg",
        verbose_name="Requisition",
        null=True,
        blank=True,
        help_text=(
            "Start typing the requisition identifier or select one from this visit"
        ),
    )

    blood_glucose_assay_datetime = models.DateTimeField(
        verbose_name="Result Report Date and Time",
        validators=[datetime_not_future],
        null=True,
        blank=True,
    )

    fasting = models.CharField(
        verbose_name="Was this fasting or non-fasting?",
        max_length=25,
        choices=FASTING_CHOICES,
        default=NOT_APPLICABLE,
    )

    blood_glucose = models.DecimalField(
        verbose_name="Blood Glucose",
        max_digits=8,
        decimal_places=4,
        null=True,
        blank=True,
    )

    blood_glucose_units = models.CharField(
        verbose_name="units",
        max_length=10,
        choices=(
            (MILLIGRAMS_PER_DECILITER, MILLIGRAMS_PER_DECILITER),
            (MILLIMOLES_PER_LITER, MILLIMOLES_PER_LITER),
        ),
        null=True,
        blank=True,
    )

    blood_glucose_abnormal = models.CharField(
        verbose_name="abnormal", choices=YES_NO, max_length=25, null=True, blank=True
    )

    blood_glucose_reportable = models.CharField(
        verbose_name="reportable",
        choices=REPORTABLE,
        max_length=25,
        null=True,
        blank=True,
    )

    # HbA1c
    hba1c_requisition = models.ForeignKey(
        SubjectRequisition,
        on_delete=PROTECT,
        related_name="hba1c",
        verbose_name="Requisition",
        null=True,
        blank=True,
        help_text=(
            "Start typing the requisition identifier or select one from this visit"
        ),
    )

    hba1c_assay_datetime = models.DateTimeField(
        verbose_name="Result Report Date and Time",
        validators=[datetime_not_future],
        null=True,
        blank=True,
    )

    hba1c = models.DecimalField(
        verbose_name="HbA1c",
        max_digits=8,
        decimal_places=4,
        validators=[MinValueValidator(1), MaxValueValidator(999)],
        null=True,
        blank=True,
    )

    hba1c_units = models.CharField(
        verbose_name="units",
        max_length=10,
        choices=((PERCENT, PERCENT),),
        null=True,
        blank=True,
    )

    hba1c_abnormal = models.CharField(
        verbose_name="abnormal", choices=YES_NO, max_length=25, null=True, blank=True
    )

    hba1c_reportable = models.CharField(
        verbose_name="reportable",
        choices=REPORTABLE,
        max_length=25,
        null=True,
        blank=True,
    )

    # eGFR
    egfr = models.DecimalField(
        verbose_name="eGFR",
        max_digits=8,
        decimal_places=4,
        null=True,
        blank=True,
        help_text="mL/min/1.73 m2 (system calculated)",
    )

    class Meta(BloodResultsModelMixin.Meta):
        verbose_name = "Blood Result: Glucose/HbA1c/eGFR"
        verbose_name_plural = "Blood Results: Glucose/HbA1c/eGFR"
