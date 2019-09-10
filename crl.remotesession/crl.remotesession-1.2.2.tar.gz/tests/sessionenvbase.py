import abc
import six
from crl.remotesession.remotesession import RemoteSession


__copyright__ = 'Copyright (C) 2019, Nokia'


@six.add_metaclass(abc.ABCMeta)
class SessionEnvBase(object):
    def __init__(self):
        self._targetkwargs = None
        self.remotesession = RemoteSession()

    def set_targetkwargs(self, targetkwargs):
        self._targetkwargs = targetkwargs

    @abc.abstractmethod
    def initialize(self):
        """Initialize SessionEnv after setting attributes.
        """

    @abc.abstractmethod
    def exec_and_verify(self):
        """Verify SessionEnv execution.
        """

    @property
    def target(self):
        if self._targetkwargs:
            return self._targetkwargs['name']
        return 'default'

    @property
    def envname(self):
        return 'envname'

    @property
    def envtarget(self):
        return '{target}.{envname}'.format(target=self.target,
                                           envname=self.envname)

    @abc.abstractproperty
    def shelldicts(self):
        """Return *shelldicts* for *set_runner_target* call.
        """
