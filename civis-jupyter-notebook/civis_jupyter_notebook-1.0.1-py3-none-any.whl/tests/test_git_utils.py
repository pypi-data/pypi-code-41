import unittest
import os
import logging
import six
import pkg_resources
import platform

from git.exc import GitCommandError
from git import Repo
from civis_jupyter_notebooks.git_utils import CivisGit, CivisGitError

if (six.PY2 or pkg_resources.parse_version('.'.join(platform.python_version_tuple()[0:2]))
        == pkg_resources.parse_version('3.4')):
    from mock import patch
    from mock import MagicMock
else:
    from unittest.mock import patch
    from unittest.mock import MagicMock

REPO_URL = 'http://www.github.com/civisanalytics.foo.git'
REPO_MOUNT_PATH = '/root/work'
GIT_REPO_REF = 'master'


class GitUtilsTest(unittest.TestCase):

    def setUp(self):
        os.environ['GIT_REPO_URL'] = REPO_URL
        os.environ['GIT_REPO_REF'] = GIT_REPO_REF
        logging.disable(logging.INFO)

    @patch('civis_jupyter_notebooks.git_utils.Repo.clone_from')
    def test_clone_repository_throws_error(self, repo_clone):
        repo_clone.side_effect = GitCommandError('clone', 'failed')
        self.assertRaises(CivisGitError, lambda: CivisGit().clone_repository())

    @patch('civis_jupyter_notebooks.git_utils.Repo.clone_from')
    def test_clone_repository_succeeds(self, repo_clone):
        repo_clone.return_value = MagicMock(spec=Repo)
        CivisGit(repo_mount_path=REPO_MOUNT_PATH).clone_repository()

        repo_clone.assert_called_with(REPO_URL, REPO_MOUNT_PATH)
        repo_clone.return_value.git.checkout.assert_called_with(GIT_REPO_REF)

    @patch('os.environ.get')
    def test_is_git_enabled_returns_false(self, env):
        env.return_value = None
        cg = CivisGit()
        self.assertFalse(cg.is_git_enabled())

    def test_is_git_enabled_returns_true(self):
        self.assertTrue(CivisGit().is_git_enabled())

    def test_has_uncommitted_changes(self):
        def custom_side_effect(arg):
            if arg == 'HEAD':
                return []
            return ['foo.py']

        cg = CivisGit()
        cg.repo = MagicMock(spec=Repo)
        cg.repo().index.diff = MagicMock(side_effect=custom_side_effect)

        self.assertTrue(cg.has_uncommitted_changes())

    def test_has_no_uncommitted_changes(self):
        cg = CivisGit()
        cg.repo = MagicMock(spec=Repo)
        cg.repo().index.diff = MagicMock(return_value=[])

        self.assertFalse(cg.has_uncommitted_changes())

    def test_has_uncommitted_changes_throws_error(self):
        cg = CivisGit()
        cg.repo = MagicMock(spec=Repo)
        cg.repo().index.diff = MagicMock(side_effect=GitCommandError('diff', 'failed'))
        self.assertRaises(CivisGitError, lambda: cg.has_uncommitted_changes())


if __name__ == '__main__':
    unittest.main()
