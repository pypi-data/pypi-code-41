import logging
from crl.interactivesessions.remoterunner import (
    RemoteRunner, RunResult)
from crl.remotescript.RemoteScript import RemoteScript


__copyright__ = 'Copyright (C) 2019, Nokia'

LOGGER = logging.getLogger(__name__)


class RemoteSessionBase(object):  # pylint: disable=too-many-public-methods

    def __init__(self):
        self._remoterunner = RemoteRunner()
        self._remotescript = RemoteScript()
        self._envcreator = None

    def get_remoterunner(self):
        """Get RemoteRunner instance.
        """
        return self._remoterunner

    def set_envcreator(self, envcreator):
        """Set *EnvCreatorBase* derivative instance.
        This automates environment based creation of targets.

        **Example**:

        =============== ==================== ============
        ${envcreator}=  Get Library Instance MyEnvCreator
        Set Envcreator  ${envcreator}
        =============== ==================== ============
        """
        self._envcreator = envcreator

    @staticmethod
    def _getresult(ret):
        return RunResult(status=ret.status,
                         stdout=ret.stdout,
                         stderr=ret.stderr)

    def close(self):
        """
        Closes all targets and kills all the executions. Should be called at
        the very end of the all the suites.
        """
        self._remoterunner.close()
