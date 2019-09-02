from django.contrib import admin

from edc_model_admin import audit_fieldset_tuple

from ...admin_site import meta_subject_admin
from ...forms import BloodResultsGluForm
from ...models import BloodResultsGlu
from .blood_results_modeladmin_mixin import (
    BloodResultsModelAdminMixin,
    conclusion_fieldset,
    summary_fieldset,
)


@admin.register(BloodResultsGlu, site=meta_subject_admin)
class BloodResultsGluAdmin(BloodResultsModelAdminMixin):

    form = BloodResultsGluForm

    autocomplete_fields = ["blood_glucose_requisition", "hba1c_requisition"]

    fieldsets = (
        (None, {"fields": ("subject_visit", "report_datetime")}),
        (
            "Blood Glucose",
            {
                "fields": [
                    "blood_glucose_requisition",
                    "blood_glucose_assay_datetime",
                    "fasting",
                    "blood_glucose",
                    "blood_glucose_units",
                    "blood_glucose_abnormal",
                    "blood_glucose_reportable",
                ]
            },
        ),
        (
            "HbA1c",
            {
                "fields": [
                    "hba1c_requisition",
                    "hba1c_assay_datetime",
                    "hba1c",
                    "hba1c_units",
                    "hba1c_abnormal",
                    "hba1c_reportable",
                ]
            },
        ),
        ("eGFR (Calculated)", {"fields": ["egfr"]}),
        conclusion_fieldset,
        summary_fieldset,
        audit_fieldset_tuple,
    )

    readonly_fields = ["egfr"]

    radio_fields = {"fasting": admin.VERTICAL}
