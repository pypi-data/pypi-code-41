from edc_constants.constants import FEMALE, MALE
from edc_constants.constants import YES, NO
from edc_form_validators import FormValidator
from edc_reportable import NormalReference
from edc_reportable.units import MICROMOLES_PER_LITER
import pdb


gluc_fasting_ref = NormalReference(
    name="gluc",
    lower=6.1,
    upper=6.9,
    lower_inclusive=True,
    upper_inclusive=True,
    units=MICROMOLES_PER_LITER,
    gender=[MALE, FEMALE],
    age_lower=18,
    age_lower_inclusive=True,
)

gluc_2hr_ref = NormalReference(
    name="gluc_2hr",
    lower=7.00,
    upper=11.10,
    lower_inclusive=True,
    upper_inclusive=True,
    units=MICROMOLES_PER_LITER,
    gender=[MALE, FEMALE],
    age_lower=18,
    age_lower_inclusive=True,
)


class SubjectScreeningFormValidator(FormValidator):

    def clean(self):

        self.not_applicable_if(
            MALE, field="gender", field_applicable="pregnant", inverse=False)

        self.required_if(
            YES, field="pregnant", field_required="preg_test_date")

        self.required_if(
            YES, field="advised_to_fast", field_required="appt_datetime")

        self.required_if(
            YES, field="fasted", field_required="fasted_duration_str")

        pdb.set_trace()

        self.applicable_if(
            YES, NO, field="pregnant", field_required="urine_bhcg",
            is_instance_field=True)

        self.required_if(
            YES, field="unsuitable_for_study", field_required="reasons_unsuitable")


#         opt = dict(
#             name="gluc",
#             lower_inclusive=True,
#             upper_inclusive=True,
#             units=MICROMOLES_PER_LITER,
#             gender=[MALE, FEMALE],
#             age_lower=18,
#             age_lower_inclusive=True,
#         )
#
#         if self.cleaned_data.get("bmi") > 30:
#             gluc_ref = NormalReference(lower=6.1, upper=6.9, **opt)
#
#         self.required_if(YES, field="bmi", field_required="glucose_fasting")
#
#         self.required_if(YES, field="bmi", field_required="glucose_two_hours")
