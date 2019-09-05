from django.contrib import admin

from edc_model_admin import audit_fieldset_tuple

from ...admin_site import meta_subject_admin
from ...forms import BloodResultsLftForm
from ...models import BloodResultsLft
from .blood_results_modeladmin_mixin import (
    BloodResultsModelAdminMixin,
    conclusion_fieldset,
    summary_fieldset,
)


@admin.register(BloodResultsLft, site=meta_subject_admin)
class BloodResultsLftAdmin(BloodResultsModelAdminMixin):

    form = BloodResultsLftForm

    autocomplete_fields = ["lft_requisition"]

    fieldsets = (
        (None, {"fields": ("subject_visit", "report_datetime")}),
        ("Liver Function Tests", {"fields": ["lft_requisition", "lft_assay_datetime"]}),
        ("AST", {"fields": ["ast", "ast_units", "ast_abnormal", "ast_reportable"]}),
        ("ALT", {"fields": ["alt", "alt_units", "alt_abnormal", "alt_reportable"]}),
        ("ALP", {"fields": ["alp", "alp_units", "alp_abnormal", "alp_reportable"]}),
        (
            "Serum Amylase",
            {
                "fields": [
                    "serum_amyl",
                    "serum_amyl_units",
                    "serum_amyl_abnormal",
                    "serum_amyl_reportable",
                ]
            },
        ),
        ("GGT", {"fields": ["ggt", "ggt_units", "ggt_abnormal", "ggt_reportable"]}),
        (
            "Serum Albumin",
            {
                "fields": [
                    "serum_alb",
                    "serum_alb_units",
                    "serum_alb_abnormal",
                    "serum_alb_reportable",
                ]
            },
        ),
        conclusion_fieldset,
        summary_fieldset,
        audit_fieldset_tuple,
    )
