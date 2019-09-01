from edc_constants.constants import HIGH_PRIORITY
from edc_action_item.action_with_notification import ActionWithNotification
from edc_action_item.site_action_items import site_action_items

from .constants import END_OF_STUDY_ACTION, LOSS_TO_FOLLOWUP_ACTION, DEATH_REPORT_ACTION


class EndOfStudyAction(ActionWithNotification):
    name = END_OF_STUDY_ACTION
    display_name = "Submit End of Study Report"
    notification_display_name = "End of Study Report"
    parent_action_names = []
    reference_model = "meta_prn.endofstudy"
    show_link_to_changelist = True
    admin_site_name = "meta_prn_admin"
    priority = HIGH_PRIORITY


class LossToFollowupAction(ActionWithNotification):
    name = LOSS_TO_FOLLOWUP_ACTION
    display_name = "Submit Loss to Follow Up Report"
    notification_display_name = " Loss to Follow Up Report"
    parent_action_names = []
    reference_model = "meta_prn.losstofollowup"
    show_link_to_changelist = True
    admin_site_name = "meta_prn_admin"
    priority = HIGH_PRIORITY


class DeathReportAction(ActionWithNotification):
    name = DEATH_REPORT_ACTION
    display_name = "Submit Death Report"
    notification_display_name = "Death Report"
    parent_action_names = []
    reference_model = "meta_prn.deathreport"
    show_link_to_changelist = True
    admin_site_name = "meta_prn_admin"
    priority = HIGH_PRIORITY


site_action_items.register(EndOfStudyAction)
site_action_items.register(LossToFollowupAction)
site_action_items.register(DeathReportAction)
