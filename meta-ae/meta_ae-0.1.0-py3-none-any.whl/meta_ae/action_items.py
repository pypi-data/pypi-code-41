from django.conf import settings
from django.utils.safestring import mark_safe
from edc_action_item import ActionWithNotification, site_action_items
from edc_adverse_event.constants import (
    AE_INITIAL_ACTION,
    AE_FOLLOWUP_ACTION,
    DEATH_REPORT_ACTION,
)
from edc_constants.constants import DEAD, LOST_TO_FOLLOWUP, YES, HIGH_PRIORITY
from edc_reportable import GRADE5
from edc_visit_schedule.utils import get_offschedule_models
from meta_subject.constants import BLOOD_RESULTS_ACTION


class AeFollowupAction(ActionWithNotification):
    name = AE_FOLLOWUP_ACTION
    display_name = "Submit AE Followup Report"
    notification_display_name = "AE Followup Report"
    parent_action_names = [AE_INITIAL_ACTION, AE_FOLLOWUP_ACTION]
    reference_model = "meta_ae.aefollowup"
    related_reference_model = "meta_ae.aeinitial"
    related_reference_fk_attr = "ae_initial"
    create_by_user = False
    show_link_to_changelist = True
    admin_site_name = "meta_ae_admin"
    instructions = mark_safe(
        f"Upon submission the TMG group will be notified "
        f'by email at <a href="mailto:{settings.EMAIL_CONTACTS.get("tmg") or "#"}">'
        f'{settings.EMAIL_CONTACTS.get("tmg") or "unknown"}</a>'
    )
    priority = HIGH_PRIORITY

    def get_next_actions(self):
        next_actions = []

        # add AE followup to next_actions if followup.
        next_actions = self.append_to_next_if_required(
            next_actions=next_actions,
            action_name=self.name,
            required=self.reference_obj.followup == YES,
        )

        # add Death report to next_actions if G5/Death
        next_actions = self.append_to_next_if_required(
            next_actions=next_actions,
            action_name=DEATH_REPORT_ACTION,
            required=(
                self.reference_obj.outcome == DEAD
                or self.reference_obj.ae_grade == GRADE5
            ),
        )

        # add Study termination to next_actions if LTFU
        if self.reference_obj.outcome == LOST_TO_FOLLOWUP:
            for offschedule_model in get_offschedule_models(
                subject_identifier=self.subject_identifier,
                report_datetime=self.reference_obj.report_datetime,
            ):
                action_cls = site_action_items.get_by_model(model=offschedule_model)
                next_actions = self.append_to_next_if_required(
                    next_actions=next_actions,
                    action_name=action_cls.name,
                    required=True,
                )
        return next_actions


class AeInitialAction(ActionWithNotification):
    name = AE_INITIAL_ACTION
    display_name = "Submit AE Initial Report"
    notification_display_name = "AE Initial Report"
    parent_action_names = [BLOOD_RESULTS_ACTION]
    reference_model = "meta_ae.aeinitial"
    show_link_to_changelist = True
    show_link_to_add = True
    admin_site_name = "meta_ae_admin"
    instructions = "Complete the initial AE report"
    priority = HIGH_PRIORITY

    def get_next_actions(self):
        """Returns next actions.

        1. Add death report action if death
        """
        next_actions = []
        deceased = (
            self.reference_obj.ae_grade == GRADE5
            or self.reference_obj.sae_reason.short_name == DEAD
        )

        # add next AeFollowup if not deceased
        if not deceased:
            next_actions = self.append_to_next_if_required(
                action_name=AE_FOLLOWUP_ACTION, next_actions=next_actions
            )

        # add next Death report if G5/Death
        next_actions = self.append_to_next_if_required(
            next_actions=next_actions,
            action_name=DEATH_REPORT_ACTION,
            required=deceased,
        )
        return next_actions


site_action_items.register(AeFollowupAction)
site_action_items.register(AeInitialAction)
