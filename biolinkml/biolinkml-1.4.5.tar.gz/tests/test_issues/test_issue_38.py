import os
import unittest

from biolinkml.generators.csvgen import CsvGenerator

sourcedir = os.path.join(os.path.abspath(os.path.dirname(__file__)), 'source')


class Issue38UnitTest(unittest.TestCase):
    def test_domain_slots(self):
        """ Subsets need to be imported as well """
        CsvGenerator(os.path.join(sourcedir, 'issue_38.yaml')).serialize()
        # We never get here if the imports fails
        self.assertEqual(True, True)


if __name__ == '__main__':
    unittest.main()
