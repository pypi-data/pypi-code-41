"""
Test rstwatch.util module - internal utilities
"""
import glob
import os
import shutil
import tempfile
import unittest

from rstwatch.api import RSTWatch
import rstwatch.util
from rstwatch.util import IncludeFile, RSTFile, ScannedFile, SourceDirectory


class TestUtil(unittest.TestCase):

    def setUp(self):
        self.directory = tempfile.mkdtemp(prefix='test-rstwatch-')

    def tearDown(self):
        shutil.rmtree(self.directory, ignore_errors=True)

    def _common_update_tests(self, scan_obj):
        # Tests common to ScannedFile and IncludeFile
        # stat should be None before first call to update()
        self.assertTrue(scan_obj.stat is None)
        # update() should return None since file does not yet exist
        self.assertEqual(None, scan_obj.update())
        # Create new file
        with open(scan_obj.filename, 'w') as f:
            f.write('test\n')
        self.assertEqual(ScannedFile.NEW, scan_obj.update())
        self.assertEqual(ScannedFile.NEW, scan_obj.last_update_result)
        self.assertEqual(ScannedFile.UNCHANGED, scan_obj.update())
        self.assertEqual(ScannedFile.UNCHANGED, scan_obj.last_update_result)
        # Add to end of file
        with open(scan_obj.filename, 'a') as f:
            f.write('additional line\n')
        self.assertEqual(ScannedFile.CHANGED, scan_obj.update())
        self.assertEqual(ScannedFile.CHANGED, scan_obj.last_update_result)

    def test_ScannedFile(self):
        filename = os.path.join(self.directory, 'test.txt')
        scan_obj = ScannedFile(filename)
        self.assertEqual(filename, scan_obj.filename)
        self._common_update_tests(scan_obj)

    def test_IncludeFile(self):
        filename = os.path.join(self.directory, 'test.inc')
        scan_obj = IncludeFile(filename)
        self.assertEqual(filename, scan_obj.filename)
        self._common_update_tests(scan_obj)

    def test_RSTFile(self):
        # Construct all the prerequisites for an RSTFile object
        filename = os.path.join(self.directory, 'test.rst')
        api_obj = RSTWatch([self.directory])
        self.assertEqual([self.directory], api_obj.directories)
        dir_obj = SourceDirectory(api_obj, api_obj.directories[0])

        # Construct the RSTFile object
        rst_obj = RSTFile(dir_obj, filename)

        # Check some attributes
        self.assertEqual(filename, rst_obj.filename)
        self.assertEqual(None, rst_obj.stat)

        # Do first update
        self.assertEqual(None, rst_obj.update())
        self.assertEqual(False, rst_obj.target_needs_gen)

        # Create the RST file
        with open(filename, 'w') as f:
            f.write("Hello RST!\n")

        # After next update() it should say html file needs generation
        self.assertEqual(rst_obj.NEW, rst_obj.update())
        self.assertEqual(True, rst_obj.target_needs_gen)

        # After another update() it should know the source file is unchanged,
        # but the target still needs to be generated.
        self.assertEqual(rst_obj.UNCHANGED, rst_obj.update())
        self.assertEqual(True, rst_obj.target_needs_gen)

        # It knows the name of the target, but target does not yet exist
        self.assertFalse(os.path.exists(rst_obj.target.filename))

        # Tell SourceDirectory to generate the html file
        dir_obj.convert_rst_to_html(rst_obj.filename,
                                    rst_obj.target.filename)

        # Now the target should exist
        self.assertTrue(os.path.isfile(rst_obj.target.filename))

        # After another update() it knows that the html file is up-to-date
        self.assertEqual(rst_obj.UNCHANGED, rst_obj.update())
        self.assertEqual(False, rst_obj.target_needs_gen)

    def test_SourceDirectory_start_empty(self):
        # Construct the SourceDirectory object
        api_obj = RSTWatch([self.directory])
        self.assertEqual([self.directory], api_obj.directories)
        dir_obj = SourceDirectory(api_obj, api_obj.directories[0])

        # Scan empty directory - nothing should happen!
        num_changes = dir_obj.scan()
        self.assertEqual(0, num_changes)

        # Create two source files
        for i, filename in enumerate(('page1.rst', 'page2.rst')):
            with open(os.path.join(self.directory, filename), 'w') as f:
                f.write("This is page {}\n".format(i + 1))

        # Re-scan - should have two changes
        num_changes = dir_obj.scan()
        self.assertEqual(2, num_changes)

        # Re-scan - should have zero changes
        num_changes = dir_obj.scan()
        self.assertEqual(0, num_changes)

        # Re-scan with refresh=True - should have two changes
        num_changes = dir_obj.scan(refresh=True)
        self.assertEqual(2, num_changes)

    def test_SourceDirectory_start_with_files(self):
        # Construct the SourceDirectory object
        api_obj = RSTWatch([self.directory])
        dir_obj = SourceDirectory(api_obj, api_obj.directories[0])

        # Create two source files
        for i, src_basename in enumerate(('page1.rst', 'page2.rst')):
            with open(os.path.join(self.directory, src_basename), 'w') as f:
                f.write("This is page {}\n".format(i + 1))

        # Scan directory - should generate missing html files
        num_changes = dir_obj.scan()
        self.assertEqual(2, num_changes)
        html_files = glob.glob(os.path.join(self.directory, '*.html'))
        self.assertEqual(2, len(html_files))

        # Construct 2nd SourceDirectory object
        dir_obj = None
        dir_obj2 = SourceDirectory(api_obj, api_obj.directories[0])

        # Scan directory - should not change anything, html files up-to-date
        num_changes = dir_obj2.scan()
        self.assertEqual(0, num_changes)

        # Construct 3rd SourceDirectory object
        dir_obj2 = None
        dir_obj3 = SourceDirectory(api_obj, api_obj.directories[0])

        # Scan directory with refresh=True, should regenerate html files
        num_changes = dir_obj3.scan(refresh=True)
        self.assertEqual(2, num_changes)

    def test_broken_include(self):
        """
        Make sure we don't crash when encountering broken include link
        """
        # Construct the SourceDirectory object
        api_obj = RSTWatch([self.directory])
        dir_obj = SourceDirectory(api_obj, api_obj.directories[0])

        # Create source file with broken include link
        src_filename = os.path.join(self.directory, 'page1.rst')
        inc_filename = os.path.join(self.directory, 'included-file.txt')
        dst_filename = os.path.join(self.directory, 'page1.html')
        with open(src_filename, 'w') as f:
            f.write("Page 1 - with include directive\n")
            f.write("-------------------------------\n")
            f.write("\n")
            f.write(".. include:: included-file.txt\n")

        # Monkey-patch the log.exception() method to capture error message.
        log_trace = []

        def _log(msg, *args, **kwargs):
            log_trace.append((msg, args, kwargs))

        _saved_exception = rstwatch.util.log.exception
        rstwatch.util.log.exception = _log

        try:
            # Scan directory and attempt to generate html file.
            num_changes = dir_obj.scan()
            self.assertEqual(1, num_changes)
        finally:
            # Revert monkey-patch
            rstwatch.util.log.exception = _saved_exception

        # Check exception message
        self.assertEqual(1, len(log_trace))
        _, args, _ = log_trace[0]
        self.assertEqual(src_filename, args[0])
        self.assertEqual(dst_filename, args[1])

        # HTML file will not actually exist because of missing include file.
        self.assertFalse(os.path.isfile(dst_filename))

        # Create include file
        with open(inc_filename, 'w') as f:
            f.write("This is some included text.\n")

        # Re-scan directory.
        num_changes = dir_obj.scan()
        self.assertEqual(1, num_changes)

        # Now HTML file will exist.
        self.assertTrue(os.path.isfile(dst_filename))
