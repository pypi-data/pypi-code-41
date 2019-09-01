from edc_constants.constants import FEMALE, MALE
from edc_constants.constants import YES, NO
from edc_form_validators import FormValidator


class ScreeningPartThreeFormValidator(FormValidator):

    def clean(self):

        self.required_if(
            YES, field="fasted", field_required="fasted_duration_str")

        self.applicable_if(
            YES, NO, field="pregnant", field_applicable="urine_bhcg",
            is_instance_field=True)

        self.required_if(
            YES, field="unsuitable_for_study", field_required="reasons_unsuitable")
