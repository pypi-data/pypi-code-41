from meta_prn.admin_site import meta_prn_admin
from meta_prn.models import DeathReport
from django.conf import settings
from django.contrib import admin
from django.core.exceptions import ObjectDoesNotExist
from django.template.loader import render_to_string
from django.urls.base import reverse
from django.utils.safestring import mark_safe
from edc_action_item import action_fieldset_tuple
from edc_constants.constants import DEAD
from edc_model_admin import audit_fieldset_tuple, SimpleHistoryAdmin
from edc_model_admin.dashboard import ModelAdminSubjectDashboardMixin
from edc_utils import convert_php_dateformat

from ..admin_site import meta_ae_admin
from ..forms import AeInitialForm
from ..models import AeInitial, AeFollowup
from ..templatetags.meta_ae_extras import (
    format_ae_description_template_name,
    format_ae_description,
)


@admin.register(AeInitial, site=meta_ae_admin)
class AeInitialAdmin(ModelAdminSubjectDashboardMixin, SimpleHistoryAdmin):

    form = AeInitialForm
    email_contact = settings.EMAIL_CONTACTS.get("ae_reports")
    additional_instructions = mark_safe(
        "Complete the initial AE report and forward to the TMG. "
        f'Email to <a href="mailto:{email_contact}">{email_contact}</a>'
    )

    fieldsets = (
        (
            "Part 1:",
            {
                "fields": (
                    "subject_identifier",
                    "ae_classification",
                    "ae_classification_other",
                    "report_datetime",
                    "ae_description",
                    "ae_awareness_date",
                    "ae_start_date",
                    "ae_grade",
                    "ae_study_relation_possibility",
                )
            },
        ),
        ("Part 2: Relationship to study drug", {"fields": ()}),
        ("Part 3:", {"fields": ("ae_cause", "ae_cause_other", "ae_treatment")}),
        ("Part 4:", {"fields": ("sae", "sae_reason")}),
        action_fieldset_tuple,
        audit_fieldset_tuple,
    )

    radio_fields = {
        "ae_cause": admin.VERTICAL,
        "ae_classification": admin.VERTICAL,
        "ae_grade": admin.VERTICAL,
        "ae_study_relation_possibility": admin.VERTICAL,
        "sae": admin.VERTICAL,
        "sae_reason": admin.VERTICAL,
    }

    ordering = ["-tracking_identifier"]

    list_display = [
        "identifier",
        "dashboard",
        "description",
        "follow_up_reports",
        "user",
    ]

    list_filter = [
        "ae_awareness_date",
        "ae_grade",
        "ae_classification",
        "sae",
        "sae_reason",
    ]

    search_fields = ["subject_identifier", "action_identifier", "tracking_identifier"]

    def user(self, obj):
        """Returns formatted user names and creation/modification dates.
        """
        return mark_safe(
            "<BR>".join(
                [
                    obj.user_created,
                    obj.created.strftime(
                        convert_php_dateformat(settings.SHORT_DATE_FORMAT)
                    ),
                    obj.user_modified,
                    obj.modified.strftime(
                        convert_php_dateformat(settings.SHORT_DATE_FORMAT)
                    ),
                ]
            )
        )

    def if_sae_reason(self, obj):
        """Returns the SAE reason.

        If DEATH, adds link to the death report.
        """
        if obj.sae_reason.short_name == DEAD:
            try:
                death_report = DeathReport.objects.get(
                    subject_identifier=obj.subject_identifier
                )
            except ObjectDoesNotExist:
                link = '<font color="red">Death report pending</font>'
            else:
                url_name = "meta_prn_deathreport"
                namespace = meta_prn_admin.name
                url = reverse(f"{namespace}:{url_name}_changelist")
                link = (
                    f'See report <a title="go to Death report"'
                    f'href="{url}?q={death_report.subject_identifier}">'
                    f"<span nowrap>{death_report.identifier}</span></a>"
                )
            return mark_safe(f"{obj.sae_reason.name}.<BR>{link}.")
        return obj.get_sae_reason_display()

    if_sae_reason.short_description = "If SAE, reason"

    def description(self, obj):
        """Returns a formatted comprehensive description of the SAE
        combining multiple fields.
        """
        context = format_ae_description({}, obj, 50)
        return render_to_string(format_ae_description_template_name, context)

    def follow_up_reports(self, obj):
        """Returns a formatted list of links to AE Follow up reports.
        """
        followups = []
        for ae_followup in AeFollowup.objects.filter(
            related_action_item=obj.action_item
        ):
            url_name = "_".join(ae_followup._meta.label_lower.split("."))
            namespace = meta_ae_admin.name
            url = reverse(f"{namespace}:{url_name}_changelist")
            report_datetime = ae_followup.report_datetime.strftime(
                convert_php_dateformat(settings.SHORT_DATETIME_FORMAT)
            )
            followups.append(
                f'<a title="go to AE follow up report for '
                f'{report_datetime}" '
                f'href="{url}?q={obj.action_identifier}">'
                f"<span nowrap>{ae_followup.identifier}</span></a>"
            )
        if followups:
            return mark_safe("<BR>".join(followups))
        return None
