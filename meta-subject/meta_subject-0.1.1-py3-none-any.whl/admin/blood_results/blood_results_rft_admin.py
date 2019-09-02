from django.contrib import admin

from edc_model_admin import audit_fieldset_tuple

from ...admin_site import meta_subject_admin
from ...forms import BloodResultsRftForm
from ...models import BloodResultsRft
from .blood_results_modeladmin_mixin import (
    BloodResultsModelAdminMixin,
    conclusion_fieldset,
    summary_fieldset,
)


@admin.register(BloodResultsRft, site=meta_subject_admin)
class BloodResultsRftAdmin(BloodResultsModelAdminMixin):

    form = BloodResultsRftForm

    autocomplete_fields = ["rft_requisition"]

    fieldsets = (
        (None, {"fields": ("subject_visit", "report_datetime")}),
        ("Renal Function Tests", {"fields": ["rft_requisition", "rft_assay_datetime"]}),
        (
            "Serum Urea",
            {
                "fields": [
                    "serum_urea",
                    "serum_urea_units",
                    "serum_urea_abnormal",
                    "serum_urea_reportable",
                ]
            },
        ),
        (
            "Serum Creatinine",
            {
                "fields": [
                    "serum_creat",
                    "serum_creat_units",
                    "serum_creat_abnormal",
                    "serum_creat_reportable",
                ]
            },
        ),
        (
            "Serum Uric Acid",
            {
                "fields": [
                    "serum_uric_acid",
                    "serum_uric_acid_units",
                    "serum_uric_acid_abnormal",
                    "serum_uric_acid_reportable",
                ]
            },
        ),
        conclusion_fieldset,
        summary_fieldset,
        audit_fieldset_tuple,
    )
