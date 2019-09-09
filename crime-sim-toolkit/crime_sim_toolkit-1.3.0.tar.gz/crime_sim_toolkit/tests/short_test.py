import os
import json
import unittest
from unittest.mock import patch
import pandas as pd
import folium
from crime_sim_toolkit import vis_utils, utils
import crime_sim_toolkit.initialiser as Initialiser
import crime_sim_toolkit.poisson_sim as Poisson_sim
import pkg_resources

# specified for directory passing test
test_dir = os.path.dirname(os.path.abspath(__file__))

resource_package = 'crime_sim_toolkit'

class Test(unittest.TestCase):


    def test_add_zero_counts(self):
        """
        Test that adding zero function works
        """
        self.data = pd.read_csv(pkg_resources.resource_filename(resource_package, 'tests/testing_data/test_counts1.csv'))

        self.init = Initialiser.Initialiser(LA_names=['Kirklees','Calderdale','Leeds','Bradford','Wakefield'])

        self.test = self.init.add_zero_counts(self.data)

        self.assertTrue(isinstance(self.test, pd.DataFrame))

        self.assertEqual(len(self.test[self.test.Day == 3].LSOA_code.unique()), 1388)

if __name__ == "__main__":
    unittest.main(verbosity=2)
