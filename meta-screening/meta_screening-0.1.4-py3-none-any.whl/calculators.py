from edc_constants.constants import FEMALE, MALE, BLACK, OTHER
from edc_reportable.units import (
    MILLIGRAMS_PER_DECILITER,
    MILLIMOLES_PER_LITER,
    MICROMOLES_PER_LITER,
)


class CalculatorError(Exception):
    pass


def converted_ogtt_two_hr(obj):
    """Return ogtt_two_hr in mmol/L or None.
    """
    # TODO: verify OGTT unit conversion
    if obj.ogtt_two_hr:
        if obj.ogtt_two_hr_units == MILLIGRAMS_PER_DECILITER:
            return float(obj.ogtt_two_hr) / 18
        if obj.ogtt_two_hr_units == MILLIMOLES_PER_LITER:
            return float(obj.ogtt_two_hr)
    return None


def converted_creatinine(obj):
    """Return Serum creatinine in micro-mol/L or None.
    """
    # TODO: verify creatinine unit conversion
    if obj.creatinine:
        if obj.creatinine_units == MILLIGRAMS_PER_DECILITER:
            return float(obj.creatinine) * 88.42
        if obj.creatinine_units == MICROMOLES_PER_LITER:
            return float(obj.creatinine)
    return None


def calculate_bmi(obj):
    calculated_bmi = None
    if obj.height and obj.weight:
        calculated_bmi = BMI(height_cm=obj.height, weight_kg=obj.weight).value
    return calculated_bmi


def calculate_egfr(obj):
    calculated_egfr = None
    if obj.gender and obj.age_in_years and obj.ethnicity and obj.converted_creatinine:
        opts = dict(
            gender=obj.gender,
            age=obj.age_in_years,
            ethnicity=obj.ethnicity,
            scr=obj.converted_creatinine,
        )
        calculated_egfr = eGFR(**opts).value
    return calculated_egfr


class BMI:
    def __init__(self, weight_kg=None, height_cm=None):
        self.weight = float(weight_kg)
        self.height = float(height_cm) / 100.0

    @property
    def value(self):
        return self.weight / (self.height ** 2)


class eGFR:

    """Reference http://nephron.com/epi_equation

    Levey AS, Stevens LA, et al. A New Equation to Estimate Glomerular
    Filtration Rate. Ann Intern Med. 2009; 150:604-612.
    """

    def __init__(self, gender=None, age=None, ethnicity=None, scr=None):
        self.gender = gender
        if not gender or self.gender not in [MALE, FEMALE]:
            raise CalculatorError("Invalid gender")
        self.age = float(age)
        self.ethnicity = ethnicity or OTHER
        self.scr = float(scr) / 88.42  # serum creatinine mg/L

    @property
    def value(self):
        return (
            141.000
            * (min(self.scr / self.kappa, 1.000) ** self.alpha)
            * (max(self.scr / self.kappa, 1.000) ** -1.209)
            * self.age_factor
            * self.gender_factor
            * self.ethnicity_factor
        )

    @property
    def alpha(self):
        return -0.329 if self.gender == FEMALE else -0.411

    @property
    def kappa(self):
        return 0.7 if self.gender == FEMALE else 0.9

    @property
    def ethnicity_factor(self):
        return 1.150 if self.ethnicity == BLACK else 1.000

    @property
    def gender_factor(self):
        return 1.018 if self.gender == FEMALE else 1.000

    @property
    def age_factor(self):
        return 0.993 ** self.age
