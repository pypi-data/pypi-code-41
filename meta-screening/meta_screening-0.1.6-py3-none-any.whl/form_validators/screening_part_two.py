from django import forms
from edc_constants.constants import YES, NOT_APPLICABLE
from edc_form_validators import FormValidator

from ..eligibility import part2_fields


class ScreeningPartTwoFormValidator(FormValidator):
    def clean(self):

        self.not_applicable_if(
            NOT_APPLICABLE,
            field="pregnant",
            field_applicable="urine_bhcg_performed",
            is_instance_field=True,
            msg="See response in part one.",
        )
        self.applicable_if(
            YES, field="urine_bhcg_performed", field_applicable="urine_bhcg"
        )
        self.required_if(
            YES, field="urine_bhcg_performed", field_required="urine_bhcg_date"
        )

        self.applicable_if_true(
            self.eligible_part_one, field_applicable="advised_to_fast"
        )

        self.required_if(YES, field="advised_to_fast", field_required="appt_datetime")

        self.raise_if_not_future_appt_datetime()

        self.required_if(
            YES, field="unsuitable_for_study", field_required="reasons_unsuitable"
        )

    @property
    def eligible_part_one(self):
        """Returns False if any of the required fields is YES.
        """
        for fld in part2_fields:
            if self.cleaned_data.get(fld) == YES:
                return False
        return True

    def raise_if_not_future_appt_datetime(self):
        """Raises if appt_datetime is not future relative to
        part_two_report_datetime.
        """
        tdelta = self.cleaned_data.get("appt_datetime") - self.cleaned_data.get(
            "part_two_report_datetime"
        )
        print(tdelta)

        hours = tdelta.seconds / 3600

        if (tdelta.days == 0 and hours < 10) or tdelta.days < 0:
            raise forms.ValidationError(
                {
                    "appt_datetime": (
                        f"Invalid date. Must be at least 10hrs "
                        f"from report date/time. Got {tdelta.days} days {round(hours,1)} hrs."
                    )
                }
            )
