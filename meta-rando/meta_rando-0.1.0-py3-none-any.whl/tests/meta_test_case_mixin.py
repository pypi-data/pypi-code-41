from meta_sites import meta_sites, fqdn
from meta_rando.constants import ACTIVE, PLACEBO
from meta_rando.utils import get_drug_assignment
from django.apps import apps as django_apps
from edc_facility.import_holidays import import_holidays
from edc_facility.models import Holiday
from edc_sites.tests import SiteTestCaseMixin
from edc_utils import get_utcnow
from faker import Faker
from model_mommy import mommy

from ..randomization_list_importer import RandomizationListImporter
from ..models import RandomizationList

fake = Faker()


class MetaTestCaseMixin(SiteTestCaseMixin):

    fqdn = fqdn

    default_sites = meta_sites

    site_names = [s[1] for s in default_sites]

    import_randomization_list = True

    @classmethod
    def setUpClass(cls):
        super().setUpClass()
        if cls.import_randomization_list:
            RandomizationListImporter(verbose=False)
        import_holidays(test=True)

    @classmethod
    def tearDownClass(cls):
        super().tearDownClass()
        RandomizationList.objects.all().delete()
        Holiday.objects.all().delete()

    def create_subject(self, consent_datetime=None, first_name=None):
        consent_datetime = consent_datetime or get_utcnow()
        first_name = first_name or fake.first_name()
        subject_screening = mommy.make_recipe(
            "meta_screening.subjectscreening", report_datetime=consent_datetime
        )
        consent = mommy.make_recipe(
            "meta_consent.subjectconsent",
            screening_identifier=subject_screening.screening_identifier,
            consent_datetime=consent_datetime,
            first_name=first_name,
        )
        return consent.subject_identifier

    def get_subject_by_drug_assignment(self, drug_assignment):
        RandomizationList = django_apps.get_model("meta_rando.randomizationlist")
        for _ in range(0, 4):
            subject_identifier = self.create_subject()
            obj = RandomizationList.objects.get(subject_identifier=subject_identifier)
            if (
                get_drug_assignment({"drug_assignment": obj.drug_assignment})
                == drug_assignment
            ):
                return subject_identifier
        return None

    def get_single_dose_subject(self):
        return self.get_subject_by_drug_assignment(ACTIVE)

    def get_control_subject(self):
        return self.get_subject_by_drug_assignment(PLACEBO)
