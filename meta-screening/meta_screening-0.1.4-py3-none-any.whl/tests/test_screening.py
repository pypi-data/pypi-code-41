from django.test import TestCase, tag
from edc_constants.constants import FEMALE, YES, NORMAL, NO, MALE, NOT_APPLICABLE
from edc_form_validators.base_form_validator import NOT_APPLICABLE_ERROR
from model_mommy import mommy

from ..models import SubjectScreening


class TestSubjectScreening(TestCase):
    def test_(self):
        obj = SubjectScreening(age_in_years=25)
        obj.save()

        self.assertFalse(obj.eligible)

    @tag("1")
    def test_eligible_with_default_recipe_criteria(self):
        subject_screening = mommy.make_recipe("meta_screening.subjectscreening")
        self.assertTrue(subject_screening.eligible)
        self.assertTrue(subject_screening.gender, MALE)

    def test_subject_invalid_age(self):
        subject_screening = mommy.prepare_recipe(
            "meta_screening.subjectscreening", age_in_years=17
        )
        self.assertFalse(subject_screening.eligible)

    def test_subject_age_minor_invalid_reason(self):
        subject_screening = mommy.make_recipe(
            "meta_screening.subjectscreening", age_in_years=17
        )
        self.assertFalse(subject_screening.eligible)
        self.assertIn(subject_screening.reasons_ineligible, "age<18.")
