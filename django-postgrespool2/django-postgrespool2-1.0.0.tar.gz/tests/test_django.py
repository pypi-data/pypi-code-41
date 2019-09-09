from django.test import TestCase
from .models import DogModel


class TestPool(TestCase):

    def tearUP(self):
        DogModel.objects.create(name='wow')
        DogModel.objects.create(name='gog')

    def test_simple_request(self):
        pass
