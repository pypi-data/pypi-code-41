from django.db import models
from edc_constants.choices import YES_NO
from edc_constants.constants import NOT_APPLICABLE
from edc_model.validators import datetime_is_future

from ..choices import YES_NO_NOT_ELIGIBLE


class PartTwoFieldsModelMixin(models.Model):

    part_two_report_datetime = models.DateTimeField(
        verbose_name="Report Date and Time",
        null=True,
        blank=False,
        help_text="Date and time of report.",
    )

    congestive_heart_failure = models.CharField(
        verbose_name=(
            "Does the patient have congestive heart failure "
            "requiring pharmacologic therapy"
        ),
        max_length=15,
        choices=YES_NO,
        null=True,
        blank=False,
    )

    liver_disease = models.CharField(
        verbose_name=("Is there clinical evidence of liver disease"),
        max_length=15,
        choices=YES_NO,
        null=True,
        blank=False,
        help_text=(
            "Evidence of chronic liver disease: Jaundice, pruritus, "
            "hepatomegaly, ascites, spider naevi and flapping tremors."
        ),
    )

    alcoholism = models.CharField(
        verbose_name=(
            "Does the patient have any evidence of alcoholism or "
            "acute alcohol intoxication"
        ),
        max_length=15,
        choices=YES_NO,
        null=True,
        blank=False,
        help_text=(
            "Evidence of alcoholism or acute alcohol intoxication: "
            "flushing, amnesia, mental confusion, nausea or vomiting, "
            "slurred speech, dehydration, dry skin and brittle hair."
        ),
    )

    acute_metabolic_acidosis = models.CharField(
        verbose_name=(
            "Does the patient have any signs or symptoms of acute metabolic acidosis"
        ),
        max_length=15,
        choices=YES_NO,
        null=True,
        blank=False,
        help_text="lactic acidosis and/or diabetic ketoacidosis",
    )
    renal_function_condition = models.CharField(
        verbose_name=(
            "Does the patient have any acute condition which can alter renal "
            "function including: dehydration, severe infection or shock"
        ),
        max_length=15,
        choices=YES_NO,
        null=True,
        blank=False,
    )

    tissue_hypoxia_condition = models.CharField(
        verbose_name=(
            "Does the patient have any acute condition which can cause tissue "
            "hypoxia"
        ),
        max_length=15,
        choices=YES_NO,
        null=True,
        blank=False,
        help_text=(
            "Including: decompensated heart failure, respiratory failure, "
            "recent myocardial infarction or shock"
        ),
    )

    acute_condition = models.CharField(
        verbose_name=(
            "Does the patient have any acute condition requiring "
            "immediate hospital care/admission"
        ),
        max_length=15,
        choices=YES_NO,
        null=True,
        blank=False,
    )

    metformin_sensitivity = models.CharField(
        verbose_name=(
            "Does the patient have any known hypersensitivity to metformin "
            "or any excipients associated with its preparation"
        ),
        max_length=15,
        choices=YES_NO,
        null=True,
        blank=False,
        help_text=(
            "For example: Magnesium stearate, sodium "
            "carboxymethylcellulose, hypromellose"
        ),
    )

    advised_to_fast = models.CharField(
        verbose_name=(
            "Has the patient been advised to return fasted for the second "
            "stage of the screening?"
        ),
        max_length=15,
        choices=YES_NO_NOT_ELIGIBLE,
        default=NOT_APPLICABLE,
    )

    appt_datetime = models.DateTimeField(
        verbose_name="Appointment date for second stage of screening",
        validators=[datetime_is_future],
        null=True,
        blank=True,
    )

    class Meta:
        abstract = True
