import os
import unittest

from symmetry.common import config


class ConfigTest(unittest.TestCase):
    def test_get_config_path(self):
        expected = os.path.join(os.path.dirname(__file__), 'test_nodes.ini')
        os.environ['symmetry_nodes_ini'] = expected

        actual = config.get_nodes_config()

        self.assertEqual(expected, actual)
