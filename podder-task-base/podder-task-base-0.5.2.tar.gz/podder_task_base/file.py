import os


class File(object):
    """
    File utility class.
    """

    def __init__(self):
        self.root_path = os.getenv("POC_BASE_ROOT", '')

    def get_config_path(self, path: str = '') -> str:
        """
        Returns absolute path to `config` directory.
        """
        return os.path.abspath(os.path.join(self.root_path, 'config', path))

    def get_input_path(self, path: str = '') -> str:
        """
        Returns absolute path to `input` directory.
        """
        return os.path.abspath(os.path.join(self.root_path, 'input', path))

    def get_output_path(self, path: str = '') -> str:
        """
        Returns absolute path to `output` directory.
        """
        return os.path.abspath(os.path.join(self.root_path, 'output', path))

    def get_tmp_path(self, path: str = '') -> str:
        """
        Returns absolute path to `tmp` directory.
        """
        return os.path.abspath(os.path.join(self.root_path, 'tmp', path))
