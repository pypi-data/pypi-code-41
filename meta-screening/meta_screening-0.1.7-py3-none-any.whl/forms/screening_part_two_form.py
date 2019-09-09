from django import forms
from edc_form_validators import FormValidatorMixin
from edc_screening.modelform_mixins import AlreadyConsentedFormMixin

from ..form_validators import ScreeningPartTwoFormValidator
from ..models import SubjectScreening


class ScreeningPartTwoForm(
    AlreadyConsentedFormMixin, FormValidatorMixin, forms.ModelForm
):

    form_validator_cls = ScreeningPartTwoFormValidator

    def clean(self):
        cleaned_data = super().clean()
        return cleaned_data

    class Meta:
        model = SubjectScreening
        fields = "__all__"
