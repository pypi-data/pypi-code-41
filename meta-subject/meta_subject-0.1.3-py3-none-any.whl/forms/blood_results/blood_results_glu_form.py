from django import forms
from edc_action_item.forms import ActionItemFormMixin
from edc_form_validators import FormValidator
from edc_visit_tracking.modelform_mixins import SubjectModelFormMixin

from ...models import BloodResultsGlu


class BloodResultsGluFormValidator(FormValidator):
    pass


class BloodResultsGluForm(ActionItemFormMixin, SubjectModelFormMixin, forms.ModelForm):

    form_validator_cls = BloodResultsGluFormValidator

    class Meta:
        model = BloodResultsGlu
        fields = "__all__"
