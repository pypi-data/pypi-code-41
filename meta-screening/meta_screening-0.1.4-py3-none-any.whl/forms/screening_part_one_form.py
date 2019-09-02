from django import forms
from edc_form_validators import FormValidatorMixin

from ..form_validators import ScreeningPartOneFormValidator
from ..models import SubjectScreening


class ScreeningPartOneForm(FormValidatorMixin, forms.ModelForm):

    form_validator_cls = ScreeningPartOneFormValidator

    class Meta:
        model = SubjectScreening
        fields = "__all__"
