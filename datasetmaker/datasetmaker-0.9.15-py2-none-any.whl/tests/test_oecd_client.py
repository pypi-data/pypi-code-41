import unittest
from unittest.mock import patch
import datasetmaker as dam
from .mock_oecd_data import MockResponse


class TestOECDClient(unittest.TestCase):
    def setUp(self):
        resp_patcher = patch('datasetmaker.utils.requests.get')
        mock_resp = resp_patcher.start()
        mock_resp.return_value = MockResponse()
        self.addCleanup(resp_patcher.stop)

        self.client = dam.create_client(source='oecd')
        self.df = self.client.get(indicators=['oecd_lifeexpy_g1'])

    def test_has_correct_columns(self):
        self.assertIn('indicator', self.df.columns)
        self.assertIn('year', self.df.columns)
        self.assertIn('value', self.df.columns)
        self.assertIn('country', self.df.columns)

    def test_mapped_correct_country_code(self):
        self.assertIn('aut', self.df.country.tolist())
