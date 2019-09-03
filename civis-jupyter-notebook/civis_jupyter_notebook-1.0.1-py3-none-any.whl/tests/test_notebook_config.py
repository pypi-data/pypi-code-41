import unittest
import six
import os
import pkg_resources
import platform
from traitlets.config.loader import Config

from civis_jupyter_notebooks import notebook_config, platform_persistence

if (six.PY2 or pkg_resources.parse_version('.'.join(platform.python_version_tuple()[0:2]))
        == pkg_resources.parse_version('3.4')):
    from mock import patch, ANY
else:
    from unittest.mock import patch, ANY


class NotebookConfigTest(unittest.TestCase):
    @patch.dict(os.environ, {'DEFAULT_KERNEL': 'kern'})
    def test_config_jupyter_sets_notebook_config(self):
        c = Config({})
        notebook_config.config_jupyter(c)
        assert(c.NotebookApp.port == 8888)
        assert(c.MultiKernelManager.default_kernel_name == 'kern')

    @patch('civis_jupyter_notebooks.platform_persistence.initialize_notebook_from_platform')
    @patch('civis_jupyter_notebooks.platform_persistence.post_save')
    def test_get_notebook_initializes_and_saves(self, post_save, init_notebook):
        notebook_config.get_notebook('path')
        init_notebook.assert_called_with('path')
        post_save.assert_called_with(ANY, 'path', None)

    @patch('civis_jupyter_notebooks.platform_persistence.initialize_notebook_from_platform')
    @patch('civis_jupyter_notebooks.platform_persistence.logger')
    @patch('os.kill')
    def test_get_notebook_writes_log_and_kills_proc_on_error(self, kill, logger, init_notebook):
        init_notebook.side_effect = platform_persistence.NotebookManagementError('err')
        notebook_config.get_notebook('path')
        logger.error.assert_called_with('err')
        logger.warn.assert_called_with(ANY)
        kill.assert_called_with(ANY, ANY)

    @patch('civis_jupyter_notebooks.platform_persistence.find_and_install_requirements')
    def test_find_and_install_requirements_success(self, persistence_find_and_install_requirements):
        c = Config({})
        notebook_config.find_and_install_requirements('path', c)
        persistence_find_and_install_requirements.assert_called_with('path')

    @patch('civis_jupyter_notebooks.platform_persistence.find_and_install_requirements')
    @patch('civis_jupyter_notebooks.platform_persistence.logger')
    def test_find_and_install_requirements_logs_errors(self, logger, persistence_find_and_install_requirements):
        persistence_find_and_install_requirements.side_effect = platform_persistence.NotebookManagementError('err')
        c = Config({})
        notebook_config.find_and_install_requirements('path', c)
        logger.error.assert_called_with("Unable to install requirements.txt:\nerr")

    @patch('civis_jupyter_notebooks.notebook_config.stage_new_notebook')
    @patch('civis_jupyter_notebooks.notebook_config.config_jupyter')
    @patch('civis_jupyter_notebooks.notebook_config.find_and_install_requirements')
    @patch('civis_jupyter_notebooks.notebook_config.get_notebook')
    def test_civis_setup_success(
            self,
            get_notebook, find_and_install_requirements,
            config_jupyter, _stage_new_notebook):
        c = Config({})
        notebook_config.civis_setup(c)

        assert(c.NotebookApp.default_url == '/notebooks/notebook.ipynb')
        config_jupyter.assert_called_with(ANY)
        get_notebook.assert_called_with(notebook_config.ROOT_DIR + '/notebook.ipynb')
        find_and_install_requirements.assert_called_with(notebook_config.ROOT_DIR, ANY)

    @patch('civis_jupyter_notebooks.notebook_config.stage_new_notebook')
    @patch('os.environ.get')
    @patch('civis_jupyter_notebooks.notebook_config.config_jupyter')
    @patch('civis_jupyter_notebooks.notebook_config.find_and_install_requirements')
    @patch('civis_jupyter_notebooks.notebook_config.get_notebook')
    def test_civis_setup_uses_environment_setting(
            self,
            get_notebook, find_and_install_requirements,
            config_jupyter, environ_get, _stage_new_notebook):

        c = Config({})
        environ_get.return_value = 'subpath/foo.ipynb'
        notebook_config.civis_setup(c)

        assert(c.NotebookApp.default_url == '/notebooks/subpath/foo.ipynb')
        config_jupyter.assert_called_with(ANY)
        get_notebook.assert_called_with(notebook_config.ROOT_DIR + '/subpath/foo.ipynb')
        find_and_install_requirements.assert_called_with(notebook_config.ROOT_DIR + '/subpath', ANY)

    @patch('civis_jupyter_notebooks.notebook_config.CivisGit')
    def test_stage_new_notebook_stages_notebook_file(self, civis_git):
        civis_git.return_value.is_git_enabled.return_value = True
        repo = civis_git.return_value.repo.return_value
        repo.untracked_files = ['notebook.ipynb']

        notebook_config.stage_new_notebook('notebook.ipynb')
        repo.index.add.assert_called_with(['notebook.ipynb'])

    @patch('civis_jupyter_notebooks.notebook_config.CivisGit')
    def test_stage_new_notebook_git_is_disabled(self, civis_git):
        civis_git.return_value.is_git_enabled.return_value = False
        notebook_config.stage_new_notebook('notebook.ipynb')

        civis_git.return_value.repo.assert_not_called()

        civis_git.return_value.repo.untracked_files.assert_not_called()


if __name__ == '__main__':
    unittest.main()
