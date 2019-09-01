from django.test import TestCase, tag
from edc_constants.constants import FEMALE, MALE, BLACK

from ..calculators import eGFR, CalculatorError, BMI


class TestCalculated(TestCase):
    @tag("1")
    def test_bmi_calculator(self):
        bmi = BMI(weight=56, height=1.50)
        print(bmi.value)

    @tag("1")
    def test_egfr_calculator(self):

        self.assertRaises(CalculatorError, gender=None)
        self.assertRaises(CalculatorError, gender="blah")

        egfr = eGFR(gender=FEMALE, age=30, scr=1.0)
        self.assertEqual(0.7, egfr.kappa)

        egfr = eGFR(gender=MALE, age=30, scr=1.0)
        self.assertEqual(0.9, egfr.kappa)

        egfr = eGFR(gender=FEMALE, age=30, scr=1.0)
        self.assertEqual(-0.329, egfr.alpha)

        egfr = eGFR(gender=MALE, age=30, scr=1.0)
        self.assertEqual(-0.411, egfr.alpha)

        egfr1 = eGFR(gender=MALE, ethnicity=BLACK, scr=1.3, age=30)
        egfr2 = eGFR(gender=MALE, ethnicity=BLACK, scr=0.9, age=30)

        print(egfr1.value)
        print(egfr2.value)
