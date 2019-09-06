import abc
import importlib
from email import message_from_string
from .crldocutils import error_handling


__copyright__ = 'Copyright (C) 2019, Nokia'


class RobotdocsconfBase(metaclass=abc.ABCMeta):

    @abc.abstractproperty
    def robotdocsconf(self):
        """Return dictionary of style:

        .. code-block:: python

            {
                'crl.examplelib.examplelib':
                    {'docformat': 'rest',
                     'synopsis': 'Example of test library functions.'},
                'crl.examplelib.examplelib.Example':
                    {'args': ['example'],
                     'docformat': 'rest',
                     'synopsis': 'Example of test library class.'}}
        """
    @property
    def metadata(self):
        return message_from_string(self._metadata_str)

    @abc.abstractproperty
    def _metadata_str(self):
        """Return metadata string of style::

            Author: John Doe
            Author-email: john.doe@example.com
            Version: 1.0

        All fields are optional and the number of fields is not limited.
        """


class EntrypointRobotdocsconf(RobotdocsconfBase):
    def __init__(self, robotdocs_ep):
        self.robotdocs_ep = robotdocs_ep
        self._robotdocsconf = self.robotdocs_ep.load()

    @property
    def robotdocsconf(self):
        return self._robotdocsconf

    @property
    def _metadata_str(self):
        metadata = ''
        with error_handling(
                'Failed to get metadata from entry point {}'.format(
                    self.robotdocs_ep)):
            metadata = self.robotdocs_ep.dist.get_metadata('METADATA')
        return metadata


class FileRobotdocsconf(RobotdocsconfBase):
    def __init__(self, path):
        self._path = path
        self._namespace = {}
        self._execfile()

    @property
    def robotdocsconf(self):
        return self._namespace['robotdocs']

    @property
    def _metadata_str(self):
        return ''

    @property
    def section(self):
        return self._namespace['section']

    def _execfile(self):
        module_name = 'robotdocsconf'
        spec = importlib.util.spec_from_file_location(module_name, self._path)
        module = importlib.util.module_from_spec(spec)
        spec.loader.exec_module(module)
        self._namespace = module.__dict__


class CumulativeRobotdocsconf(RobotdocsconfBase):

    def __init__(self, section):
        self._section = section
        self._robotdocsconf = {}

    def update(self, robotdocsconf):
        self._robotdocsconf.update(robotdocsconf.robotdocsconf)

    @property
    def robotdocsconf(self):
        return self._robotdocsconf

    @property
    def _metadata_str(self):
        return 'Name: {}'.format(self._section)
