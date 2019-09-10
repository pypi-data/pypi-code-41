# coding: utf-8
from django.test import TestCase

from django_pie.decorator import test_print
from django_pie.random import uuid_str, random_str


class TestRandom(TestCase):
    def setUp(self):
        pass

    @test_print
    def test_uuid_str(self):
        s = uuid_str()
        self.assertEqual(len(s), 32)
        s = uuid_str(dash=True)
        self.assertEqual(len(s), 36)

    @test_print
    def test_random_str(self):
        s = random_str()
        self.assertEqual(len(s), 16)
        s = random_str(20)
        self.assertEqual(len(s), 20)
        s = random_str(upper=True)
        self.assertEqual(s.isupper(), True)
        s = random_str(lower=True)
        self.assertEqual(s.islower(), True)
        s = random_str(alpha=True, number=False)
        self.assertEqual(s.isalpha(), True)
        s = random_str(alpha=False, number=True)
        self.assertEqual(s.isdigit(), True)
        s = random_str(alpha=False, special=True)
        print('random_str special:', s)
        self.assertEqual(len(s), 16)
