from dateutil.relativedelta import relativedelta
from django.contrib.sites.models import Site
from edc_constants.constants import YES, NO, FEMALE
from edc_reportable.units import MILLIGRAMS_PER_DECILITER
from edc_utils import get_utcnow
from faker import Faker
from model_mommy.recipe import Recipe

from .models import SubjectScreening

fake = Faker()

subjectscreening = Recipe(
    SubjectScreening,
    report_datetime=get_utcnow() - relativedelta(days=1),
    subject_identifier=None,
    gender=FEMALE,
    age_in_years=40,
    consent_ability=YES,
    pregnant=NO,
    preg_test_date=get_utcnow() - relativedelta(days=1),
    site=Site.objects.get_current(),
    part_two_report_datetime=get_utcnow() - relativedelta(days=1),
    congestive_heart_failure=NO,
    liver_disease=NO,
    alcoholism=NO,
    acute_metabolic_acidosis=NO,
    renal_function_condition=NO,
    tissue_hypoxia_condition=NO,
    acute_condition=NO,
    metformin_sensitivity=NO,
    advised_to_fast=YES,
    appt_datetime=get_utcnow() + relativedelta(days=1),
    part_three_report_datetime=get_utcnow(),
    weight=65,
    height=120,
    fasted=YES,
    fasted_duration_str="24:00",
    urine_bhcg=NO,
    hba1c=5.7,
    creatinine=0.6,
    creatinine_units=MILLIGRAMS_PER_DECILITER,
    fasting_glucose=6.9,
    fasting_glucose_datetime=get_utcnow(),
    ogtt_performed_datetime=get_utcnow(),
    #     ogtt_two_hr,
    #     ogtt_two_hr_units,
    #     ogtt_two_hr_datetime=get_utcnow(),
    #     ogtt_two_hr_duration="02:00",
)
