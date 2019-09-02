from edc_constants.constants import YES
from edc_form_validators import FormValidator

from ..eligibility import part2_fields


class ScreeningPartTwoFormValidator(FormValidator):
    def clean(self):

        eligible = True
        for fld in part2_fields:
            print(fld, self.cleaned_data.get(fld))
            if self.cleaned_data.get(fld) == YES:
                eligible = False
                break

        self.applicable_if_true(eligible, field_applicable="advised_to_fast")

        self.required_if(YES, field="advised_to_fast", field_required="appt_datetime")

        self.required_if(
            YES, field="unsuitable_for_study", field_required="reasons_unsuitable"
        )
