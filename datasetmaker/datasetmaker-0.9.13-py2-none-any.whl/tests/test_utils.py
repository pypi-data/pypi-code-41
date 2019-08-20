import unittest
import pandas as pd
from datasetmaker.entity import Country
from datasetmaker.exceptions import CountryNotFoundException


class TestUtils(unittest.TestCase):
    def test_country_not_found(self):
        name_to_id = Country.name_to_id()
        df = pd.DataFrame([{'country': 'Sweden'}, {'country': 'Fakename'}])
        with self.assertRaises(CountryNotFoundException):
            df['id'] = df.country.map(name_to_id)
