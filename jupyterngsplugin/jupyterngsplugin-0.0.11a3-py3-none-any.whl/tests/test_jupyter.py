import os
import ssl
import unittest

from jupyterngsplugin.databases.sra import runs_from_bioproject_id


class TestSet(unittest.TestCase):
    def setUp(self):
        if (not os.environ.get('PYTHONHTTPSVERIFY', '') and
                getattr(ssl, '_create_unverified_context', None)):
            ssl._create_default_https_context = ssl._create_unverified_context

    def test_sra_bioproject(self):
        df = runs_from_bioproject_id('PRJNA339968', 'veraalva@ncbi.nlm.nih.gov')
        self.assertEqual(len(df), 34)
