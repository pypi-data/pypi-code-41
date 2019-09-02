from django import forms
from edc_action_item.forms import ActionItemFormMixin
from edc_form_validators import FormValidator
from edc_visit_tracking.modelform_mixins import SubjectModelFormMixin

from ...models import BloodResultsRft


class BloodResultsRftFormValidator(FormValidator):
    pass


class BloodResultsRftForm(ActionItemFormMixin, SubjectModelFormMixin, forms.ModelForm):

    form_validator_cls = BloodResultsRftFormValidator

    class Meta:
        model = BloodResultsRft
        fields = "__all__"
