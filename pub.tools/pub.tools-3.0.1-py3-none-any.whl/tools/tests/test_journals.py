import unittest

from ..journals import atoj, jtoa


class TestJournals(unittest.TestCase):

    def test_atoj(self):
        self.assertEqual(atoj('J Cancer'), 'Journal of Cancer')

    def test_jtoa(self):
        self.assertEqual(jtoa('Journal of Cancer'), 'J Cancer')

    def test_cache(self):
        self.assertEqual(atoj('J Cancer', cache=True), 'Journal of Cancer')
        self.assertEqual(jtoa('Journal of Cancer', cache=True), 'J Cancer')


def test_suite():
    return unittest.defaultTestLoader.loadTestsFromName(__name__)
