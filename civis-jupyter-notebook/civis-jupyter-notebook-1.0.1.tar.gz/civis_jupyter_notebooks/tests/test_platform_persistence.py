import os
import subprocess
import nbformat
import requests
import unittest
import logging
import six
import pkg_resources
import platform

from civis_jupyter_notebooks import platform_persistence
from civis_jupyter_notebooks.platform_persistence import NotebookManagementError

if (six.PY2 or pkg_resources.parse_version('.'.join(platform.python_version_tuple()[0:2]))
        == pkg_resources.parse_version('3.4')):
    from mock import ANY, MagicMock, patch
else:
    from unittest.mock import ANY, MagicMock, patch

TEST_NOTEBOOK_PATH = '/path/to/notebook.ipynb'
TEST_PLATFORM_OBJECT_ID = '1914'
SAMPLE_NOTEBOOK = open(os.path.join(os.path.dirname(__file__), 'fixtures/sample_notebook.ipynb')).read()
SAMPLE_NEW_NOTEBOOK = open(os.path.join(os.path.dirname(__file__), 'fixtures/sample_new_notebook.ipynb')).read()


class NotebookWithoutNewFlag(nbformat.NotebookNode):
    """ Helper that tests if a NotebookNode has the metadata.civis.new_notebook flag set to True """
    def __eq__(self, other):
        return not other.get('metadata', {}).get('civis', {}).get('new_notebook', False)


class PlatformPersistenceTest(unittest.TestCase):
    def setUp(self):
        os.environ['CIVIS_API_KEY'] = 'hi mom'
        os.environ['PLATFORM_OBJECT_ID'] = TEST_PLATFORM_OBJECT_ID

        logging.disable(logging.INFO)

    @patch('os.makedirs')
    @patch('civis_jupyter_notebooks.platform_persistence.open')
    @patch('civis.APIClient')
    @patch('civis_jupyter_notebooks.platform_persistence.requests.get')
    def test_initialize_notebook_will_get_nb_from_platform(self, rg, _client, _op, _makedirs):
        rg.return_value = MagicMock(spec=requests.Response, status_code=200, content=SAMPLE_NOTEBOOK)
        platform_persistence.initialize_notebook_from_platform(TEST_NOTEBOOK_PATH)
        platform_persistence.get_client().notebooks.get.assert_called_with(TEST_PLATFORM_OBJECT_ID)

    @patch('os.makedirs')
    @patch('civis_jupyter_notebooks.platform_persistence.open')
    @patch('civis_jupyter_notebooks.platform_persistence.__pull_and_load_requirements')
    @patch('civis.APIClient')
    @patch('civis_jupyter_notebooks.platform_persistence.requests.get')
    def test_initialize_notebook_will_pull_nb_from_url(self, rg, _client, requirements, _op, _makedirs):
        url = 'http://whatever'
        rg.return_value = MagicMock(spec=requests.Response, status_code=200, content=SAMPLE_NOTEBOOK)
        platform_persistence.get_client().notebooks.get.return_value.notebook_url = url
        platform_persistence.get_client().notebooks.get.return_value.requirements_url = None
        platform_persistence.initialize_notebook_from_platform(TEST_NOTEBOOK_PATH)
        rg.assert_called_with(url)
        requirements.assert_not_called()

    @patch('os.makedirs')
    @patch('civis_jupyter_notebooks.platform_persistence.open')
    @patch('civis.APIClient')
    @patch('civis_jupyter_notebooks.platform_persistence.requests.get')
    def test_initialize_notebook_will_throw_error_on_nb_pull(self, rg, _client, _op, _makedirs):
        rg.return_value = MagicMock(spec=requests.Response, status_code=500, response={})
        self.assertRaises(NotebookManagementError,
                          lambda: platform_persistence.initialize_notebook_from_platform(TEST_NOTEBOOK_PATH))

    @patch('nbformat.write')
    @patch('os.makedirs')
    @patch('civis_jupyter_notebooks.platform_persistence.open')
    @patch('civis.APIClient')
    @patch('civis_jupyter_notebooks.platform_persistence.requests.get')
    def test_initialize_notebook_will_set_new_notebook_flag_to_false(self, rg, _client, _op, _makedirs, nbwrite):
        rg.return_value = MagicMock(spec=requests.Response, status_code=200, content=SAMPLE_NEW_NOTEBOOK)
        platform_persistence.get_client().notebooks.get.return_value.notebooks_url = 'something'
        platform_persistence.get_client().notebooks.get.return_value.requirements_url = None
        platform_persistence.initialize_notebook_from_platform(TEST_NOTEBOOK_PATH)
        nbwrite.assert_called_with(NotebookWithoutNewFlag(), ANY)

    @patch('os.path.isfile')
    @patch('nbformat.write')
    @patch('os.makedirs')
    @patch('civis_jupyter_notebooks.platform_persistence.open')
    @patch('civis.APIClient')
    @patch('civis_jupyter_notebooks.platform_persistence.requests.get')
    def test_initialize_notebook_will_use_s3_notebook_if_not_new_and_git_notebook_exists(self, rg, _client, _op,
                                                                                         _makedirs, nbwrite, isfile):
        rg.return_value = MagicMock(spec=requests.Response, status_code=200, content=SAMPLE_NOTEBOOK)
        platform_persistence.get_client().notebooks.get.return_value.notebooks_url = 'something'
        platform_persistence.get_client().notebooks.get.return_value.requirements_url = None
        isfile.return_value = True
        platform_persistence.initialize_notebook_from_platform(TEST_NOTEBOOK_PATH)
        nbwrite.assert_called_with(ANY, ANY)

    @patch('os.path.isfile')
    @patch('nbformat.write')
    @patch('os.makedirs')
    @patch('civis_jupyter_notebooks.platform_persistence.open')
    @patch('civis.APIClient')
    @patch('civis_jupyter_notebooks.platform_persistence.requests.get')
    def test_initialize_notebook_will_discard_s3_notebook_if_new_and_git_notebook_exists(self, rg, _client, _op,
                                                                                         _makedirs, nbwrite, isfile):
        rg.return_value = MagicMock(spec=requests.Response, status_code=200, content=SAMPLE_NEW_NOTEBOOK)
        platform_persistence.get_client().notebooks.get.return_value.notebooks_url = 'something'
        platform_persistence.get_client().notebooks.get.return_value.requirements_url = None
        isfile.return_value = True
        platform_persistence.initialize_notebook_from_platform(TEST_NOTEBOOK_PATH)
        nbwrite.assert_not_called()

    @patch('civis_jupyter_notebooks.platform_persistence.open')
    @patch('civis.APIClient')
    @patch('os.makedirs')
    @patch('civis_jupyter_notebooks.platform_persistence.requests.get')
    def test_initialize_notebook_will_create_directories_if_needed(self, rg, makedirs, _client, _op):
        rg.return_value = MagicMock(spec=requests.Response, status_code=200, content=SAMPLE_NOTEBOOK)
        platform_persistence.initialize_notebook_from_platform(TEST_NOTEBOOK_PATH)
        directory = os.path.dirname(TEST_NOTEBOOK_PATH)
        makedirs.assert_called_with(directory)

    @patch('os.makedirs')
    @patch('civis_jupyter_notebooks.platform_persistence.open')
    @patch('civis_jupyter_notebooks.platform_persistence.__pull_and_load_requirements')
    @patch('civis.APIClient')
    @patch('civis_jupyter_notebooks.platform_persistence.requests.get')
    def test_initialize_notebook_will_pull_requirements(self, rg, _client, requirements, _op, _makedirs):
        url = 'http://whatever'
        rg.return_value = MagicMock(spec=requests.Response, status_code=200, content=SAMPLE_NOTEBOOK)
        platform_persistence.get_client().notebooks.get.return_value.requirements_url = url
        platform_persistence.initialize_notebook_from_platform(TEST_NOTEBOOK_PATH)
        requirements.assert_called_with(url, TEST_NOTEBOOK_PATH)

    @patch('os.makedirs')
    @patch('civis_jupyter_notebooks.platform_persistence.open')
    @patch('civis_jupyter_notebooks.platform_persistence.__pull_and_load_requirements')
    @patch('civis.APIClient')
    @patch('civis_jupyter_notebooks.platform_persistence.requests.get')
    def test_initialize_notebook_will_error_on_requirements_pull(self, rg, _client, _requirements, _op, _makedirs):
        url = 'http://whatever'
        rg.return_value = MagicMock(spec=requests.Response, status_code=500)
        platform_persistence.get_client().notebooks.get.return_value.requirements_url = url
        self.assertRaises(NotebookManagementError,
                          lambda: platform_persistence.initialize_notebook_from_platform(TEST_NOTEBOOK_PATH))

    @patch('civis_jupyter_notebooks.platform_persistence.open')
    @patch('civis_jupyter_notebooks.platform_persistence.check_call')
    @patch('civis.APIClient')
    @patch('requests.put')
    def test_post_save_fetches_urls_from_api(self, _rput, client, _ccc, _op):
        platform_persistence.post_save({'type': 'notebook'}, '', {})
        platform_persistence.get_client().notebooks.list_update_links.assert_called_with(TEST_PLATFORM_OBJECT_ID)

    @patch('civis_jupyter_notebooks.platform_persistence.open')
    @patch('civis_jupyter_notebooks.platform_persistence.check_call')
    @patch('civis.APIClient')
    @patch('requests.put')
    @patch('civis_jupyter_notebooks.platform_persistence.save_notebook')
    def test_post_save_performs_two_put_operations(self, save, rput, _client, _ccc, _op):
        platform_persistence.post_save({'type': 'notebook'}, '', {})
        self.assertTrue(save.called)

    @patch('civis_jupyter_notebooks.platform_persistence.open')
    @patch('civis_jupyter_notebooks.platform_persistence.check_call')
    @patch('civis.APIClient')
    @patch('requests.put')
    @patch('civis_jupyter_notebooks.platform_persistence.save_notebook')
    @patch('civis_jupyter_notebooks.platform_persistence.get_update_urls')
    def test_post_save_skipped_for_non_notebook_types(self, guu, save, _rput, _client, _ccc, _op):
        platform_persistence.post_save({'type': 'blargggg'}, '', {})
        self.assertFalse(guu.called)
        self.assertFalse(save.called)

    @patch('civis_jupyter_notebooks.platform_persistence.open')
    @patch('civis_jupyter_notebooks.platform_persistence.check_call')
    @patch('civis.APIClient')
    @patch('requests.put')
    def test_post_save_generates_preview(self, _rput, _client, check_call, _op):
        platform_persistence.post_save({'type': 'notebook'}, 'x/y', {})
        check_call.assert_called_with(['jupyter', 'nbconvert', '--to', 'html', 'y'], cwd='x')

    @patch('civis_jupyter_notebooks.platform_persistence.open')
    @patch('civis_jupyter_notebooks.platform_persistence.check_call')
    @patch('civis.APIClient')
    @patch('requests.put')
    def test_generate_preview_throws_error_on_convert(self, _rput, _client, check_call, _op):
        check_call.side_effect = subprocess.CalledProcessError('foo', 255)
        self.assertRaises(NotebookManagementError,
                          lambda: platform_persistence.generate_and_save_preview('http://notebook_url_in_s3', 'os/path'))
        check_call.assert_called_with(['jupyter', 'nbconvert', '--to', 'html', 'path'], cwd='os')

    @patch('civis.APIClient')
    def test_will_regenerate_api_client(self, mock_client):
        platform_persistence.get_client()
        mock_client.assert_called_with(resources='all')

    @patch('os.path.isfile')
    @patch('os.path.isdir')
    @patch('civis_jupyter_notebooks.platform_persistence.pip_install')
    def test_find_and_install_requirements_calls_pip_install(self, pip_install, isdir, isfile):
        os.path.isdir.return_value = True
        os.path.isfile.return_value = True
        platform_persistence.find_and_install_requirements('/root/work/foo')
        pip_install.assert_called_with('/root/work/foo/requirements.txt')

    @patch('os.path.isfile')
    @patch('os.path.isdir')
    @patch('civis_jupyter_notebooks.platform_persistence.pip_install')
    def test_find_and_install_requirements_searches_tree(self, pip_install, isdir, isfile):
        os.path.isdir.return_value = True
        os.path.isfile.side_effect = [False, True]
        platform_persistence.find_and_install_requirements('/root/work/foo')
        pip_install.assert_called_with('/root/work/requirements.txt')

    @patch('os.path.isfile')
    @patch('os.path.isdir')
    @patch('civis_jupyter_notebooks.platform_persistence.pip_install')
    def test_find_and_install_requirements_excludes_root(self, pip_install, isdir, isfile):
        os.path.isdir.return_value = True
        os.path.isfile.return_value = True
        platform_persistence.find_and_install_requirements('/root')
        pip_install.assert_not_called()

    @patch('subprocess.check_output')
    @patch('sys.executable')
    def test_pip_install_calls_subprocess(self, executable, check_output):
        platform_persistence.pip_install('/path/requirements.txt')
        check_output.assert_called_with(
                [executable, '-m', 'pip', 'install', '-r', '/path/requirements.txt'],
                stderr=subprocess.STDOUT
                )

    @patch('subprocess.check_output')
    @patch('sys.executable')
    def test_pip_install_failure_raises_notebookmanagementerror(self, executable, check_output):
        check_output.side_effect = subprocess.CalledProcessError(returncode=1, cmd='cmd', output=b'installation error')
        with self.assertRaisesRegexp(NotebookManagementError, 'installation error'):
            platform_persistence.pip_install('/path/requirements.txt')


if __name__ == '__main__':
    unittest.main()
