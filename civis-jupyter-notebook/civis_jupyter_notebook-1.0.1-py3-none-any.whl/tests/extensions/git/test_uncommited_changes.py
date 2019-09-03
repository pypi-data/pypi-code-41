import unittest
import six
import pkg_resources
import platform

from civis_jupyter_notebooks.extensions.git.uncommitted_changes import UncommittedChangesHandler
from civis_jupyter_notebooks.git_utils import CivisGitError

if (six.PY2 or pkg_resources.parse_version('.'.join(platform.python_version_tuple()[0:2]))
        == pkg_resources.parse_version('3.4')):
    from mock import patch, MagicMock
else:
    from unittest.mock import patch, MagicMock


class UncommittedChangesHandlerTest(unittest.TestCase):

    def setUp(self):
        self.handler = UncommittedChangesHandler(MagicMock(), MagicMock())
        self.handler.finish = MagicMock()
        self.handler.set_status = MagicMock()

    @patch('civis_jupyter_notebooks.extensions.git.uncommitted_changes.CivisGit')
    def test_get_will_return_404(self, civis_git):
        civis_git.return_value.is_git_enabled.return_value = False

        dummy_response = {}
        self.handler.get()
        self.handler.set_status.assert_called_with(404, 'Not a git enabled notebook')
        self.handler.finish.assert_called_with(dummy_response)

    @patch('civis_jupyter_notebooks.extensions.git.uncommitted_changes.CivisGit')
    def test_get_will_return_200(self, civis_git):
        civis_git.return_value.is_git_enabled.return_value = True
        civis_git.return_value.has_uncommitted_changes.return_value = True

        dummy_response = {'dirty': True}

        self.handler.get()
        civis_git.return_value.has_uncommitted_changes.assert_called_with()
        self.handler.set_status.assert_called_with(200)
        self.handler.finish.assert_called_with(dummy_response)

    @patch('civis_jupyter_notebooks.extensions.git.uncommitted_changes.CivisGit')
    def test_get_will_return_200_even_with_error(self, civis_git):
        civis_git.return_value.is_git_enabled.return_value = True
        civis_git.return_value.has_uncommitted_changes.side_effect = CivisGitError('dummy error')
        dummy_response = {'dirty': False}
        self.handler.get()
        self.handler.set_status.assert_called_with(200)
        self.handler.finish.assert_called_with(dummy_response)


if __name__ == '__main__':
    unittest.main()
