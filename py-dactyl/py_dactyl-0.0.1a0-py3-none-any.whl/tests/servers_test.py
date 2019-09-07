import unittest
from unittest import mock

from pydactyl import PterodactylClient


class ServersTests(unittest.TestCase):

    def setUp(self):
        self.client = PterodactylClient(url='dummy', api_key='dummy')