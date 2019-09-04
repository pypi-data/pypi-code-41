from edc_constants.constants import YES, NO, NOT_APPLICABLE
from edc_form_validators import FormValidator

from ..eligibility import part2_fields


class ScreeningPartTwoFormValidator(FormValidator):
    def clean(self):

        self.not_applicable_if(
            NOT_APPLICABLE,
            field="pregnant",
            field_applicable="urine_bhcg_performed",
            is_instance_field=True,
            msg="See response in part one.",
        )
        self.applicable_if(
            YES, field="urine_bhcg_performed", field_applicable="urine_bhcg"
        )
        self.required_if(
            YES, field="urine_bhcg_performed", field_required="urine_bhcg_date"
        )

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
