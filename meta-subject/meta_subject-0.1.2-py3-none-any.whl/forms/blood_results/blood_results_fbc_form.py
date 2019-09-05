from django import forms
from edc_action_item.forms import ActionItemFormMixin
from edc_form_validators import FormValidator
from edc_visit_tracking.modelform_mixins import SubjectModelFormMixin

from ...models import BloodResultsFbc


class BloodResultsFbcFormValidator(FormValidator):
    pass


class BloodResultsFbcForm(ActionItemFormMixin, SubjectModelFormMixin, forms.ModelForm):

    form_validator_cls = BloodResultsFbcFormValidator

    class Meta:
        model = BloodResultsFbc
        fields = "__all__"
