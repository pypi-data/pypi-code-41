import unittest
from unittest.mock import patch
import datasetmaker as dam
from .mock_nobel_data import MockResponse


class TestNobelClient(unittest.TestCase):
    def setUp(self):
        resp_patcher = patch('datasetmaker.clients.nobel.requests.get')
        mock_resp = resp_patcher.start()
        mock_resp.return_value = MockResponse()
        self.addCleanup(resp_patcher.stop)

        self.client = dam.create_client(source='nobel')
        self.df = self.client.get()

    def test_has_correct_columns(self):
        self.assertIn('nobel_born_city', self.df.columns)

    def test_mapped_correct_country_code(self):
        self.assertIn('prus', self.df.nobel_born_country.tolist())

    def test_mapped_non_existing_country_is_none(self):
        self.assertTrue(self.df.nobel_born_country.isnull().any())
