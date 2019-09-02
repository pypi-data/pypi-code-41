from django.test import TestCase, tag

from ..visit_schedules.schedule import schedule
from ..visit_schedules.visit_schedule import visit_schedule


class TestVisitSchedule(TestCase):
    def test_visit_schedule_models(self):

        self.assertEqual(visit_schedule.death_report_model, "meta_prn.deathreport")
        self.assertEqual(visit_schedule.offstudy_model, "edc_offstudy.subjectoffstudy")
        self.assertEqual(visit_schedule.locator_model, "edc_locator.subjectlocator")

    def test_schedule_models(self):
        self.assertEqual(schedule.onschedule_model, "meta_prn.onschedule")
        self.assertEqual(schedule.offschedule_model, "meta_prn.endofstudy")
        self.assertEqual(schedule.consent_model, "meta_consent.subjectconsent")
        self.assertEqual(schedule.appointment_model, "edc_appointment.appointment")
