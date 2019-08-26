import unittest
from tests.util import *
from tests import mock_client


class ClientTestSuite(unittest.TestCase):
    def setUp(self):
        self.client = mock_client.C9Client(verbose=True)

    def tearDown(self):
        self.client.disconnect()

    def test_echo(self):
        response = self.client.echo()
        assert_equal(response, b'<ECHOSUCKA>\r')

    def test_home(self):
        self.client.connection.write(b'a')
        response = self.client.home()
        assert_equal(response, b'<HOME>\r')