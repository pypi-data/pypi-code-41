from dateutil.relativedelta import relativedelta
from django.test import TestCase, tag
from edc_constants.constants import YES, BLACK, FEMALE, NOT_APPLICABLE, TBD, NO
from edc_utils.date import get_utcnow

from ..models import ScreeningPartOne, ScreeningPartTwo


class TestScreeningPartTwo(TestCase):
    def setUp(self):
        self.screening = ScreeningPartOne(
            report_datetime=get_utcnow(),
            hospital_identifier="111",
            initials="ZZ",
            gender=FEMALE,
            age_in_years=25,
            ethnicity=BLACK,
            hiv_pos=YES,
            art_six_months=YES,
            on_rx_stable=YES,
            lives_nearby=YES,
            staying_nearby=YES,
            pregnant=NOT_APPLICABLE,
            consent_ability=YES,
        )
        self.screening.save()
        self.screening_identifier = self.screening.screening_identifier

    def test_defaults(self):

        obj = ScreeningPartTwo.objects.get(
            screening_identifier=self.screening_identifier
        )
        self.assertEqual(obj.eligible_part_one, YES)
        self.assertTrue(obj.reasons_ineligible_part_one == "")

        self.assertEqual(obj.eligible_part_two, TBD)
        self.assertFalse(obj.reasons_ineligible_part_two)

        self.assertFalse(obj.eligible)
        self.assertFalse(obj.consented)

    def test_eligible(self):

        obj = ScreeningPartTwo.objects.get(
            screening_identifier=self.screening_identifier
        )
        self.assertEqual(obj.eligible_part_one, YES)
        self.assertTrue(obj.reasons_ineligible_part_one == "")

        obj.part_two_report_datetime = get_utcnow()
        obj.urine_bhcg_performed = NO
        obj.congestive_heart_failure = NO
        obj.liver_disease = NO
        obj.alcoholism = NO
        obj.acute_metabolic_acidosis = NO
        obj.renal_function_condition = NO
        obj.tissue_hypoxia_condition = NO
        obj.save()

        self.assertEqual(obj.eligible_part_two, TBD)
        self.assertFalse(obj.reasons_ineligible_part_two)
        self.assertFalse(obj.eligible)
        self.assertFalse(obj.consented)

        obj.acute_condition = NO
        obj.metformin_sensitivity = YES
        obj.save()

        self.assertEqual(obj.eligible_part_two, NO)
        self.assertIn("Metformin", obj.reasons_ineligible_part_two)
        self.assertFalse(obj.eligible)
        self.assertFalse(obj.consented)

        obj.acute_condition = NO
        obj.metformin_sensitivity = NO
        obj.advised_to_fast = YES
        obj.appt_datetime = get_utcnow() + relativedelta(days=1)
        obj.save()

        self.assertEqual(obj.eligible_part_two, YES)
        self.assertFalse(obj.reasons_ineligible_part_two)
        self.assertFalse(obj.eligible)
        self.assertFalse(obj.consented)
