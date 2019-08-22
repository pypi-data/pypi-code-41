"""
Test rstwatch running in a separate process (as from the command line)
"""
from __future__ import print_function
import glob
import os
import shutil
import signal
import subprocess
from subprocess import PIPE
import sys
import tempfile
import time
import unittest

import rstwatch.__main__


class TestCmdLine(unittest.TestCase):

    expected_html_files = set(['index.html', 'page1.html', 'page2.html'])

    def setUp(self):
        self.directory = tempfile.mkdtemp(prefix='test-rstwatch-')
        self.proc = None

    def tearDown(self):
        shutil.rmtree(self.directory, ignore_errors=True)

    def _copy_rst_files(self):
        for subdir in ('include', 'web'):
            src = os.path.join('tests/data', subdir)
            dst = os.path.join(self.directory, subdir)
            shutil.copytree(src, dst)

    def _query_html_files(self):
        web_dir = os.path.join(self.directory, 'web')
        html_files = glob.glob(os.path.join(web_dir, '*.html'))
        return set(os.path.basename(name) for name in html_files)
    
    
    def _create_pythonpath(self):
        # Set up PYPTHONPATH so "python setup.py test" works under Windows
        pythonpath = [os.getcwd()]
        for item in sys.path:
            if item.endswith('.egg') and os.path.exists(item):
                pythonpath.append(item)
        return os.pathsep.join(pythonpath)

    def _run_cmd(self, params, verbose=True, cwd=None, **kwargs):
        """
        Run a rstwatch command.
        :param params: List of strings; parameters for rstwatch.
        """
        env = os.environ.copy()
        env['PYTHONPATH'] = self._create_pythonpath()
        cmd = [sys.executable, '-m', 'rstwatch']
        cmd.extend(params)
        if verbose:
            print('$', subprocess.list2cmdline(cmd))
        if cwd is None:
            cwd = self.directory
        if hasattr(subprocess, 'CREATE_NEW_PROCESS_GROUP'):
            kwargs['creationflags'] = subprocess.CREATE_NEW_PROCESS_GROUP
        self.proc = subprocess.Popen(cmd, cwd=cwd, env=env, **kwargs)

    def _stop_cmd(self, check_rc=True):
        if self.proc is None:
            return None
        if self.proc.returncode is not None:
            return self.proc.returncode
        if hasattr(signal, 'CTRL_BREAK_EVENT'):
            sig = signal.CTRL_BREAK_EVENT
        else:
            sig = signal.SIGINT
        self.proc.send_signal(sig)
        rc = self.proc.wait()
        if check_rc and not sys.platform.startswith('win'):
            self.assertEqual(0, rc)
        return rc

    def test_cmd_exit(self):
        self._copy_rst_files()
        self._run_cmd(['--exit', 'web'])
        rc = self.proc.wait()
        self.assertEqual(0, rc)
        self.assertEqual(self.expected_html_files, self._query_html_files())

    def test_cmd_help(self):
        self._run_cmd(['--help'], stdout=PIPE, stderr=PIPE,
                      universal_newlines=True)
        out, err = self.proc.communicate()
        self.assertEqual(rstwatch.__main__.__doc__.strip(), out.strip())

    def test_cmd_session(self):
        # Test a rstwatch session in which files are created, deleted, and
        # changed. Assume that there is an upper bound on how long it will
        # take to regenerate a small number of little files.
        log_config = os.path.abspath('example/log-config.ini')
        log_filename = os.path.join(self.directory, 'rstwatch.log')
        max_process_start_time = 3.0
        poll_interval = 0.1
        max_regen_time = 0.9
        activity_wait_time = poll_interval + max_regen_time
        mtime_resolution_delay = 1.0

        # Copy the test files to the temp directory.
        self._copy_rst_files()

        # Start the rstwatch command
        self._run_cmd([
            '--interval={}'.format(poll_interval),
            '--log-config={}'.format(log_config),
            'web',
        ])

        # Wait for process to start up and create log file
        t0 = time.time()
        while True:
            start_delay = time.time() - t0
            if os.path.exists(log_filename):
                print("rstwatch started in", start_delay, "seconds.")
                break
            if start_delay > max_process_start_time:
                raise Exception("Timed out after {0} seconds waiting log file"
                                .format(start_delay))

        # Wait and check that html files are all generated
        time.sleep(activity_wait_time)
        expected_html_files = self.expected_html_files.copy()
        self.assertEqual(expected_html_files, self._query_html_files())

        # Add new page3
        page3_filename = os.path.join(self.directory, 'web', 'page3.rst')
        with open(page3_filename, 'w') as f:
            f.write("Page 3 - doesn't contain much.\n")
        time.sleep(activity_wait_time)
        expected_html_files.add('page3.html')
        self.assertEqual(expected_html_files, self._query_html_files())

        # Delete page2
        page2_filename = os.path.join(self.directory, 'web', 'page2.rst')
        os.remove(page2_filename)
        time.sleep(activity_wait_time)
        expected_html_files.remove('page2.html')
        self.assertEqual(expected_html_files, self._query_html_files())

        # Rename page1 to page0
        page0_filename = os.path.join(self.directory, 'web', 'page0.rst')
        page1_filename = os.path.join(self.directory, 'web', 'page1.rst')
        os.rename(page1_filename, page0_filename)
        time.sleep(activity_wait_time)
        expected_html_files.remove('page1.html')
        expected_html_files.add('page0.html')
        self.assertEqual(expected_html_files, self._query_html_files())

        # Blow away html files and verify that they get regenerated
        for basename in expected_html_files:
            filename = os.path.join(self.directory, 'web', basename)
            os.remove(filename)
        time.sleep(activity_wait_time)
        self.assertEqual(expected_html_files, self._query_html_files())

        # Modify include file and verify that page0 gets regenerated
        time.sleep(mtime_resolution_delay)
        page0_html_filename = os.path.join(self.directory, 'web', 'page0.html')
        stat_before = os.stat(page0_html_filename)
        footer_filename = os.path.join(self.directory, 'include', 'footer.rst')
        with open(footer_filename, 'a') as f:
            f.write('Another line added to footer.\n')
        time.sleep(activity_wait_time)
        stat_after = os.stat(page0_html_filename)
        self.assertTrue(stat_after.st_mtime > stat_before.st_mtime)

        # Send Ctrl-C signal to stop the process
        self._stop_cmd()
