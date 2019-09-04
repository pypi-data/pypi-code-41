from edc_constants.constants import YES, NO
from edc_form_validators import FormValidator
from meta_screening.calculators import CalculatorError, calculate_bmi, BMI
from django import forms


class ScreeningPartThreeFormValidator(FormValidator):
    def clean(self):

        self.required_if(YES, field="fasted", field_required="fasted_duration_str")

        self.applicable_if(
            YES,
            NO,
            field="pregnant",
            field_applicable="urine_bhcg",
            is_instance_field=True,
        )

        self.required_if(
            YES, field="unsuitable_for_study", field_required="reasons_unsuitable"
        )

        if self.cleaned_data.get("height") and self.cleaned_data.get("weight"):
            try:
                BMI(
                    height_cm=self.cleaned_data.get("height"),
                    weight_kg=self.cleaned_data.get("weight"),
                ).value
            except CalculatorError as e:
                raise forms.ValidationError(e)
