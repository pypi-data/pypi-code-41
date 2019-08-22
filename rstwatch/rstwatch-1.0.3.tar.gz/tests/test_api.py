"""
Test rstwatch.api module - external API
"""
import glob
import os
import shutil
import tempfile
import time
import unittest

from rstwatch.api import RSTWatch


class TestRSTWatch(unittest.TestCase):

    expected_html_file_set = set(['index.html', 'page1.html', 'page2.html'])

    def setUp(self):
        self.directory = tempfile.mkdtemp(prefix='test-rstwatch-')
        for subdir in ('include', 'web'):
            src = os.path.join('tests/data', subdir)
            dst = os.path.join(self.directory, subdir)
            shutil.copytree(src, dst)

    def tearDown(self):
        shutil.rmtree(self.directory, ignore_errors=True)

    def test_api(self):
        """
        Basic Happy Path test for high-level API
        """
        # Create API object
        web_dir = os.path.join(self.directory, 'web')
        api_obj = RSTWatch([web_dir])
        self.assertEqual([web_dir], api_obj.directories)

        # Make sure no html files exist yet
        html_files = glob.glob(os.path.join(web_dir, '*.html'))
        self.assertEqual(0, len(html_files))

        # Run 1 pass of directory scan
        api_obj.run(one_time=True)

        # Check for expected html files
        html_files = glob.glob(os.path.join(web_dir, '*.html'))
        html_file_set = set(os.path.basename(name) for name in html_files)
        self.assertEqual(self.expected_html_file_set, html_file_set)

        # Save the current mtime of each html file
        mtimes0 = [os.path.getmtime(filename) for filename in html_files]

        # Wait to make sure that mtime changes can be detected
        time.sleep(1.0)

        # Run 1 more pass of directory scan
        api_obj.run(one_time=True)

        # Make sure mtimes did not change, because no .rst file changed.
        mtimes1 = [os.path.getmtime(filename) for filename in html_files]
        self.assertEqual(mtimes0, mtimes1)
