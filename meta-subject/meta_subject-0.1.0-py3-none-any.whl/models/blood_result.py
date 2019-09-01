from django.core.validators import MinValueValidator, MaxValueValidator
from django.db import models
from django.db.models.deletion import PROTECT
from edc_action_item.models import ActionModelMixin
from edc_constants.choices import YES_NO, YES_NO_NA
from edc_constants.constants import NOT_APPLICABLE
from edc_identifier.model_mixins import TrackingModelMixin
from edc_model.validators import datetime_not_future
from edc_registration.models import RegisteredSubject
from edc_reportable import (
    IU_LITER,
    GRAMS_PER_DECILITER,
    MILLIGRAMS_PER_DECILITER,
    MILLIMOLES_PER_LITER,
    PERCENT,
    MILLILITER_PER_MINUTE,
    CELLS_PER_MICROLITER,
    GRAMS_PER_LITER,
    site_reportables,
)
from edc_reportable.choices import REPORTABLE
from edc_visit_tracking.managers import CrfModelManager, CurrentSiteManager


from ..constants import BLOOD_RESULTS_ACTION
from ..choices import FASTING_CHOICES
from .crf_model_mixin import CrfModelMixin
from .subject_requisition import SubjectRequisition


class BloodResult(ActionModelMixin, TrackingModelMixin, CrfModelMixin):

    action_name = BLOOD_RESULTS_ACTION

    tracking_identifier_prefix = "BR"

    # blood glucose
    bg_requisition = models.ForeignKey(
        SubjectRequisition,
        on_delete=PROTECT,
        related_name="bg",
        verbose_name="Requisition",
        null=True,
        blank=True,
        help_text="Start typing the requisition identifier or select one from this visit",
    )

    bg_assay_datetime = models.DateTimeField(
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

    glu = models.DecimalField(
        verbose_name="WBC", decimal_places=2, max_digits=6, null=True, blank=True
    )

    glu_units = models.CharField(
        verbose_name="units",
        max_length=10,
        choices=(
            (MILLIGRAMS_PER_DECILITER, MILLIGRAMS_PER_DECILITER),
            (MILLIMOLES_PER_LITER, MILLIMOLES_PER_LITER),
        ),
        null=True,
        blank=True,
    )

    glu_abnormal = models.CharField(
        verbose_name="abnormal", choices=YES_NO, max_length=25, null=True, blank=True
    )

    glu_reportable = models.CharField(
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
        help_text="Start typing the requisition identifier or select one from this visit",
    )

    hba1c_assay_datetime = models.DateTimeField(
        verbose_name="Result Report Date and Time",
        validators=[datetime_not_future],
        null=True,
        blank=True,
    )

    hba1c = models.IntegerField(
        verbose_name="Hemoglobin A1c",
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

    # Renal function test #####################################

    rft_requisition = models.ForeignKey(
        SubjectRequisition,
        on_delete=PROTECT,
        related_name="ft",
        verbose_name="Requisition",
        null=True,
        blank=True,
        help_text="Start typing the requisition identifier or select one from this visit",
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
    serum_crea = models.DecimalField(
        verbose_name="Serum Creatinine",
        decimal_places=2,
        max_digits=6,
        null=True,
        blank=True,
    )

    serum_crea_units = models.CharField(
        verbose_name="units",
        max_length=10,
        choices=((MILLIGRAMS_PER_DECILITER, MILLIGRAMS_PER_DECILITER),),
        null=True,
        blank=True,
    )

    serum_crea_abnormal = models.CharField(
        verbose_name="abnormal", choices=YES_NO, max_length=25, null=True, blank=True
    )

    serum_crea_reportable = models.CharField(
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

    # eGFR
    e_grf = models.DecimalField(
        verbose_name="eGFR mL/min per 1.73 m2",
        decimal_places=2,
        max_digits=6,
        null=True,
        blank=True,
    )

    e_grf_units = models.CharField(
        verbose_name="units",
        max_length=10,
        choices=((MILLILITER_PER_MINUTE, MILLILITER_PER_MINUTE),),
        null=True,
        blank=True,
    )

    e_grf_abnormal = models.CharField(
        verbose_name="abnormal", choices=YES_NO, max_length=25, null=True, blank=True
    )

    e_grf_reportable = models.CharField(
        verbose_name="reportable",
        choices=REPORTABLE,
        max_length=25,
        null=True,
        blank=True,
    )

    # Liver function test #####################################
    lft_requisition = models.ForeignKey(
        SubjectRequisition,
        on_delete=PROTECT,
        related_name="lft",
        verbose_name="Requisition",
        null=True,
        blank=True,
        help_text="Start typing the requisition identifier or select one from this visit",
    )

    lft_assay_datetime = models.DateTimeField(
        verbose_name="Result Report Date and Time",
        validators=[datetime_not_future],
        null=True,
        blank=True,
    )

    # ALT
    ast = models.IntegerField(
        validators=[MinValueValidator(1), MaxValueValidator(999)],
        verbose_name="AST",
        null=True,
        blank=True,
    )

    ast_units = models.CharField(
        verbose_name="units",
        max_length=10,
        choices=((IU_LITER, IU_LITER),),
        null=True,
        blank=True,
    )

    ast_abnormal = models.CharField(
        verbose_name="abnormal", choices=YES_NO, max_length=25, null=True, blank=True
    )

    ast_reportable = models.CharField(
        verbose_name="reportable",
        choices=REPORTABLE,
        max_length=25,
        null=True,
        blank=True,
    )

    # AST
    alt = models.IntegerField(
        validators=[MinValueValidator(1), MaxValueValidator(999)],
        verbose_name="ALT",
        null=True,
        blank=True,
    )

    alt_units = models.CharField(
        verbose_name="units",
        max_length=10,
        choices=((IU_LITER, IU_LITER),),
        null=True,
        blank=True,
    )

    alt_abnormal = models.CharField(
        verbose_name="abnormal", choices=YES_NO, max_length=25, null=True, blank=True
    )

    alt_reportable = models.CharField(
        verbose_name="reportable",
        choices=REPORTABLE,
        max_length=25,
        null=True,
        blank=True,
    )

    # ALP
    alp = models.IntegerField(
        validators=[MinValueValidator(1), MaxValueValidator(999)],
        verbose_name="ALP",
        null=True,
        blank=True,
    )

    alp_units = models.CharField(
        verbose_name="units",
        max_length=10,
        choices=((IU_LITER, IU_LITER),),
        null=True,
        blank=True,
    )

    alp_abnormal = models.CharField(
        verbose_name="abnormal", choices=YES_NO, max_length=25, null=True, blank=True
    )

    alp_reportable = models.CharField(
        verbose_name="reportable",
        choices=REPORTABLE,
        max_length=25,
        null=True,
        blank=True,
    )

    # Serum Amylase
    serum_amyl = models.IntegerField(
        validators=[MinValueValidator(1), MaxValueValidator(999)],
        verbose_name="Serum Amylase",
        null=True,
        blank=True,
    )

    serum_amyl_units = models.CharField(
        verbose_name="units",
        max_length=10,
        choices=((IU_LITER, IU_LITER),),
        null=True,
        blank=True,
    )

    serum_amyl_abnormal = models.CharField(
        verbose_name="abnormal", choices=YES_NO, max_length=25, null=True, blank=True
    )

    serum_amyl_reportable = models.CharField(
        verbose_name="reportable",
        choices=REPORTABLE,
        max_length=25,
        null=True,
        blank=True,
    )

    # Serum GGT
    ggt = models.IntegerField(
        validators=[MinValueValidator(1), MaxValueValidator(999)],
        verbose_name="GGT",
        null=True,
        blank=True,
    )

    ggt_units = models.CharField(
        verbose_name="units",
        max_length=10,
        choices=((IU_LITER, IU_LITER),),
        null=True,
        blank=True,
    )

    ggt_abnormal = models.CharField(
        verbose_name="abnormal", choices=YES_NO, max_length=25, null=True, blank=True
    )

    ggt_reportable = models.CharField(
        verbose_name="reportable",
        choices=REPORTABLE,
        max_length=25,
        null=True,
        blank=True,
    )

    # Serum Albumin
    serum_alb = models.IntegerField(
        validators=[MinValueValidator(1), MaxValueValidator(999)],
        verbose_name="Serum Albumin",
        null=True,
        blank=True,
    )

    serum_alb_units = models.CharField(
        verbose_name="units",
        max_length=10,
        choices=((GRAMS_PER_LITER, GRAMS_PER_LITER),),
        null=True,
        blank=True,
    )

    serum_alb_abnormal = models.CharField(
        verbose_name="abnormal", choices=YES_NO, max_length=25, null=True, blank=True
    )

    serum_alb_reportable = models.CharField(
        verbose_name="reportable",
        choices=REPORTABLE,
        max_length=25,
        null=True,
        blank=True,
    )

    # Full blood count ############################
    fbc_requisition = models.ForeignKey(
        SubjectRequisition,
        on_delete=PROTECT,
        related_name="fbc",
        verbose_name="Requisition",
        null=True,
        blank=True,
        help_text="Start typing the requisition identifier or select one from this visit",
    )

    fbc_assay_datetime = models.DateTimeField(
        verbose_name="Result Report Date and Time",
        validators=[datetime_not_future],
        null=True,
        blank=True,
    )

    # Hb
    haemoglobin = models.DecimalField(
        decimal_places=1, max_digits=6, null=True, blank=True
    )

    haemoglobin_units = models.CharField(
        verbose_name="units",
        max_length=10,
        choices=((GRAMS_PER_DECILITER, GRAMS_PER_DECILITER),),
        null=True,
        blank=True,
    )

    haemoglobin_abnormal = models.CharField(
        verbose_name="abnormal", choices=YES_NO, max_length=25, null=True, blank=True
    )

    haemoglobin_reportable = models.CharField(
        verbose_name="reportable",
        choices=REPORTABLE,
        max_length=25,
        null=True,
        blank=True,
    )

    # HCT
    hct = models.IntegerField(
        validators=[MinValueValidator(1), MaxValueValidator(999)],
        verbose_name="Haematocrit",
        null=True,
        blank=True,
    )

    hct_units = models.CharField(
        verbose_name="units",
        max_length=10,
        choices=((PERCENT, PERCENT),),
        null=True,
        blank=True,
    )

    hct_abnormal = models.CharField(
        verbose_name="abnormal", choices=YES_NO, max_length=25, null=True, blank=True
    )

    hct_reportable = models.CharField(
        verbose_name="reportable",
        choices=REPORTABLE,
        max_length=25,
        null=True,
        blank=True,
    )

    # RBC
    rbc = models.IntegerField(
        validators=[MinValueValidator(1), MaxValueValidator(999999)],
        verbose_name="Red blood cell count",
        null=True,
        blank=True,
    )

    rbc_units = models.CharField(
        verbose_name="units",
        max_length=10,
        choices=((CELLS_PER_MICROLITER, CELLS_PER_MICROLITER),),
        null=True,
        blank=True,
    )

    rbc_abnormal = models.CharField(
        verbose_name="abnormal", choices=YES_NO, max_length=25, null=True, blank=True
    )

    rbc_reportable = models.CharField(
        verbose_name="reportable",
        choices=REPORTABLE,
        max_length=25,
        null=True,
        blank=True,
    )

    # WBC
    wbc = models.DecimalField(
        verbose_name="WBC", decimal_places=2, max_digits=6, null=True, blank=True
    )

    wbc_units = models.CharField(
        verbose_name="units",
        max_length=10,
        choices=((CELLS_PER_MICROLITER, CELLS_PER_MICROLITER),),
        null=True,
        blank=True,
    )

    wbc_abnormal = models.CharField(
        verbose_name="abnormal", choices=YES_NO, max_length=25, null=True, blank=True
    )

    wbc_reportable = models.CharField(
        verbose_name="reportable",
        choices=REPORTABLE,
        max_length=25,
        null=True,
        blank=True,
    )

    # platelets
    platelets = models.IntegerField(
        validators=[MinValueValidator(1), MaxValueValidator(9999)],
        null=True,
        blank=True,
    )

    platelets_units = models.CharField(
        verbose_name="units",
        max_length=10,
        choices=((CELLS_PER_MICROLITER, CELLS_PER_MICROLITER),),
        null=True,
        blank=True,
    )

    platelets_abnormal = models.CharField(
        verbose_name="abnormal", choices=YES_NO, max_length=25, null=True, blank=True
    )

    platelets_reportable = models.CharField(
        verbose_name="reportable",
        choices=REPORTABLE,
        max_length=25,
        null=True,
        blank=True,
    )

    results_abnormal = models.CharField(
        verbose_name="Are any of the above results abnormal?",
        choices=YES_NO,
        max_length=25,
    )

    results_reportable = models.CharField(
        verbose_name="If any results are abnormal, are results within grade III "
        "or above?",
        max_length=25,
        choices=YES_NO_NA,
        help_text=(
            "If YES, this value will open Adverse Event Form.<br/><br/>"
            "Note: On Day 1 only abnormal bloods should not be reported as adverse"
            "events."
        ),
    )

    summary = models.TextField(null=True, blank=True)

    on_site = CurrentSiteManager()

    objects = CrfModelManager()

    def save(self, *args, **kwargs):
        self.summary = "\n".join(self.get_summary())
        super().save(*args, **kwargs)

    def get_summary(self):
        registered_subject = RegisteredSubject.objects.get(
            subject_identifier=self.subject_visit.subject_identifier
        )
        opts = dict(
            gender=registered_subject.gender,
            dob=registered_subject.dob,
            report_datetime=self.subject_visit.report_datetime,
        )
        summary = []
        for field in [f.name for f in self._meta.fields]:
            value = getattr(self, field)
            grp = site_reportables.get("ambition").get(field)
            if value and grp:
                units = getattr(self, f"{field}_units")
                opts.update(units=units)
                grade = grp.get_grade(value, **opts)
                if grade and grade.grade:
                    summary.append(f"{field}: {grade.description}.")
                elif not grade:
                    normal = grp.get_normal(value, **opts)
                    if not normal:
                        summary.append(f"{field}: {value} {units} is abnormal")
        return summary

    def get_action_item_reason(self):
        return self.summary

    @property
    def abnormal(self):
        return self.results_abnormal

    @property
    def reportable(self):
        return self.results_reportable

    class Meta(CrfModelMixin.Meta):
        verbose_name = "Blood Result"
        verbose_name_plural = "Blood Results"
