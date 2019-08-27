import unittest

from goenrichment.go import load_goenrichdb


class TestSet(unittest.TestCase):
    def setUp(self):
        self.godb = load_goenrichdb("ftp://ftp.ncbi.nlm.nih.gov/pub/goenrichment/goenrichDB_human.pickle")

    def test_godb_alt_id(self):
        self.assertEqual(len(self.godb['alt_id']), 2375)

    def test_godb_graph(self):
        self.assertEqual(len(self.godb['graph'].node), 45006)

    def test_godb_M(self):
        self.assertEqual(self.godb['M'], 39810)
