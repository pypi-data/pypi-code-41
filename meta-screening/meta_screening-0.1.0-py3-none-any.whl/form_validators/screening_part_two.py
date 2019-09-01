from edc_constants.constants import FEMALE, MALE
from edc_constants.constants import YES, NO
from edc_form_validators import FormValidator


class ScreeningPartTwoFormValidator(FormValidator):

    def clean(self):

        self.required_if(
            YES, field="advised_to_fast", field_required="appt_datetime")

        self.required_if(
            YES, field="unsuitable_for_study", field_required="reasons_unsuitable")
