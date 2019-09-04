from django.test import TestCase, tag

from ..models import SubjectScreening


class TestSubjectScreening(TestCase):
    def test_(self):
        obj = SubjectScreening(age_in_years=25)
        obj.save()

        self.assertFalse(obj.eligible)
