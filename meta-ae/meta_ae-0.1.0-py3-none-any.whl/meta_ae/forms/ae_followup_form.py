from django import forms
from edc_action_item.forms import ActionItemFormMixin
from edc_constants.constants import YES, DEAD
from edc_form_validators import FormValidatorMixin, FormValidator
from edc_registration.modelform_mixins import ModelFormSubjectIdentifierMixin
from edc_reportable import SEVERITY_INCREASED_FROM_G3, GRADE5

from ..models import AeFollowup
from pprint import pprint
from edc_utils.text import convert_php_dateformat
from django.conf import settings


class AeFollowupFormValidator(FormValidator):
    def clean(self):

        self.applicable_if(
            SEVERITY_INCREASED_FROM_G3, field="outcome", field_applicable="ae_grade"
        )

        self.applicable_if(
            SEVERITY_INCREASED_FROM_G3, field="outcome", field_applicable="ae_grade"
        )


class AeFollowupForm(
    FormValidatorMixin,
    ModelFormSubjectIdentifierMixin,
    ActionItemFormMixin,
    forms.ModelForm,
):

    form_validator_cls = AeFollowupFormValidator

    subject_identifier = forms.CharField(
        label="Subject Identifier",
        required=False,
        widget=forms.TextInput(attrs={"readonly": "readonly"}),
    )

    def clean(self):
        cleaned_data = super().clean()

        ae_initial = self.cleaned_data.get("ae_initial")
        if not ae_initial and self.instance:
            ae_initial = self.instance.ae_initial
        outcome_date = self.cleaned_data.get("outcome_date")
        if ae_initial and outcome_date:
            if outcome_date < ae_initial.ae_start_date:
                formatted_dte = ae_initial.ae_start_date.strftime(
                    convert_php_dateformat(settings.SHORT_DATE_FORMAT)
                )
                raise forms.ValidationError(
                    {
                        "outcome_date": (
                            f"May not be before the AE start date {formatted_dte}."
                        )
                    }
                )

        if cleaned_data.get("followup") == YES:
            if (
                cleaned_data.get("ae_grade") == GRADE5
                or cleaned_data.get("outcome") == DEAD
            ):
                raise forms.ValidationError(
                    {
                        "followup": (
                            "Expected No. Submit a death report when the "
                            "severity increases to grade 5."
                        )
                    }
                )

        return cleaned_data

    class Meta:
        model = AeFollowup
        fields = "__all__"
