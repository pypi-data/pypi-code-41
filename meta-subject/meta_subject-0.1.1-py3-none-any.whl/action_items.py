from meta_ae.constants import AE_INITIAL_ACTION
from edc_action_item import Action, site_action_items
from edc_constants.constants import YES, HIGH_PRIORITY

from .constants import (
    BLOOD_RESULTS_FBC_ACTION,
    BLOOD_RESULTS_GLU_ACTION,
    BLOOD_RESULTS_LFT_ACTION,
    BLOOD_RESULTS_RFT_ACTION,
)


class BaseBloodResultsAction(Action):
    name = None
    display_name = None
    reference_model = None

    priority = HIGH_PRIORITY
    show_on_dashboard = True
    create_by_user = False

    def reopen_action_item_on_change(self):
        return False

    def get_next_actions(self):
        next_actions = []
        if (
            self.reference_obj.results_abnormal == YES
            and self.reference_obj.results_reportable == YES
        ):
            # AE for reportable result, though not on DAY1.0
            next_actions = [AE_INITIAL_ACTION]
        return next_actions


class BloodResultsLftAction(BaseBloodResultsAction):
    name = BLOOD_RESULTS_LFT_ACTION
    display_name = "Reportable Blood Result: LFT"
    reference_model = "meta_subject.bloodresultslft"


class BloodResultsRftAction(BaseBloodResultsAction):
    name = BLOOD_RESULTS_RFT_ACTION
    display_name = "Reportable Blood Result: RFT"
    reference_model = "meta_subject.bloodresultsrft"


class BloodResultsFbcAction(BaseBloodResultsAction):
    name = BLOOD_RESULTS_FBC_ACTION
    display_name = "Reportable Blood Result: FBC"
    reference_model = "meta_subject.bloodresultsfbc"


class BloodResultsGluAction(BaseBloodResultsAction):
    name = BLOOD_RESULTS_GLU_ACTION
    display_name = "Reportable Blood Result: GLU"
    reference_model = "meta_subject.bloodresultsglu"


site_action_items.register(BloodResultsFbcAction)
site_action_items.register(BloodResultsLftAction)
site_action_items.register(BloodResultsRftAction)
site_action_items.register(BloodResultsGluAction)
