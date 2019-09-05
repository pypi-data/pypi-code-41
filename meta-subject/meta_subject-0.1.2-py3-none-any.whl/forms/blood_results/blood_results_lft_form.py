from django import forms
from edc_action_item.forms import ActionItemFormMixin
from edc_form_validators import FormValidator
from edc_visit_tracking.modelform_mixins import SubjectModelFormMixin

from ...models import BloodResultsLft


class BloodResultsLftFormValidator(FormValidator):
    pass


class BloodResultsLftForm(ActionItemFormMixin, SubjectModelFormMixin, forms.ModelForm):

    form_validator_cls = BloodResultsLftFormValidator

    class Meta:
        model = BloodResultsLft
        fields = "__all__"
