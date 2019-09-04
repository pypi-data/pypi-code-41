from django.apps import apps as django_apps
from edc_constants.constants import MALE
from edc_constants.constants import YES, NO
from edc_form_validators import FormValidator
from django.core.exceptions import ObjectDoesNotExist


class ScreeningPartOneFormValidator(FormValidator):
    def clean(self):

        self.applicable_if(YES, field="hiv_pos", field_applicable="art_six_months")

        self.applicable_if(YES, field="hiv_pos", field_applicable="on_rx_stable")

        self.not_applicable_if(
            MALE, field="gender", field_applicable="pregnant", inverse=False
        )
