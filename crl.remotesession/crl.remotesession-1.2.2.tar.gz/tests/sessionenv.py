import abc
import six
import pytest
from crl.remotesession.remotesessionbase import RunResult
from crl.remotesession.exceptions import (
    NotImplementedInRemoteScript,
    RunnerTargetNotSet)
from .example_envcreator import ExampleEnvCreator
from .sessionenvbase import SessionEnvBase


__copyright__ = 'Copyright (C) 2019, Nokia'


@six.add_metaclass(abc.ABCMeta)
class MockSessionEnvBase(SessionEnvBase):
    def __init__(self):
        super(MockSessionEnvBase, self).__init__()
        self.mock_remoterunner = None
        self._envcreator = ExampleEnvCreator(self._envdictcreator)

    def set_mock_remoterunner(self, mock_remoterunner):
        self.mock_remoterunner = mock_remoterunner

    @staticmethod
    def _envdictcreator(target, envname):
        return {target: envname}

    def initialize(self):
        self.remotesession.set_envcreator(self._envcreator)
        self._set_target()
        self.mock_remoterunner.reset_mock()

    @abc.abstractmethod
    def _set_target(self):
        """Set *RemoteSesion* target if needed.
        """

    @abc.abstractmethod
    def exec_and_verify(self):
        """Verify SessionEnv execution.
        """

    @property
    def cmd(self):
        return 'cmd'

    @property
    def _set_target_meth(self):
        return self.mock_remoterunner.return_value.set_target

    @property
    def _set_target_property_meth(self):
        return self.mock_remoterunner.return_value.set_target_property

    @property
    def _execute_command_in_target_meth(self):
        return self.mock_remoterunner.return_value.execute_command_in_target

    @property
    def shelldicts(self):
        return [{'shellname': 'example'}]


@six.add_metaclass(abc.ABCMeta)
class SessionEnvExecBase(MockSessionEnvBase):

    def _set_target(self):
        self.remotesession.set_runner_target(self.shelldicts, **self._targetkwargs)

    def exec_and_verify(self):
        self._exec_cmd()
        self._set_target_meth.assert_called_once_with(self.shelldicts,
                                                      name=self.envtarget)
        self._set_target_property_meth.assert_called_once_with(
            target_name=self.envtarget,
            property_name='update_env_dict',
            property_value=self._envdictcreator(self.target, self.envname))
        self._verify_exec_call()

    @abc.abstractmethod
    def _exec_cmd(self):
        """Run e.g. *execute_command_in_target* or
        *execute_background_command_in_target*.
        """

    @abc.abstractmethod
    def _verify_exec_call(self):
        """Verify *exec_cmd* mock calls.
        """


class SessionEnvForeground(SessionEnvExecBase):

    def _exec_cmd(self):
        assert self.remotesession.execute_command_in_target(
            self.cmd, target=self.envtarget) == self.expected_ret

    @property
    def expected_ret(self):
        return RunResult(
            status=self._execute_command_in_target_meth.return_value.status,
            stdout=self._execute_command_in_target_meth.return_value.stdout,
            stderr=self._execute_command_in_target_meth.return_value.stderr)

    def _verify_exec_call(self):
        self._execute_command_in_target_meth.assert_called_once_with(
            self.cmd, target=self.envtarget,
            executable=None,
            progress_log=False,
            timeout=3600)


class SessionEnvBackground(SessionEnvExecBase):

    def _exec_cmd(self):
        self.remotesession.execute_background_command_in_target(
            self.cmd, target=self.envtarget)

    def _verify_exec_call(self):
        self._execute_background_command.assert_called_once_with(
            self.cmd, target=self.envtarget,
            exec_id='background',
            executable=None)

    @property
    def _execute_background_command(self):
        return self.mock_remoterunner.return_value.execute_background_command_in_target


@six.add_metaclass(abc.ABCMeta)
class SessionRaisesBase(MockSessionEnvBase):
    def exec_and_verify(self):
        with pytest.raises(self._exceptioncls) as excinfo:
            self.remotesession.execute_command_in_target(self.cmd,
                                                         target=self.envtarget)

        self._verify_exception_msg(str(excinfo.value))

    @abc.abstractproperty
    def _exceptioncls(self):
        """Return exception class of the exception when target is not set
        properly.
        """

    @abc.abstractmethod
    def _verify_exception_msg(self, msg):
        """Verify exception message of the exception raised when
        the target is not set properly.
        """


class SessionEnvRemoteScript(SessionRaisesBase):

    def _set_target(self):
        self.remotesession.set_target(host='host',
                                      username='username',
                                      password='password',
                                      **self._targetkwargs)

    @property
    def _exceptioncls(self):
        return NotImplementedInRemoteScript

    def _verify_exception_msg(self, msg):
        assert msg == (
            'RemoteScript target ({target}) cannot be used for creating '
            '{envtarget}'.format(
                target=self.target,
                envtarget=self.envtarget))


class SessionEnvTargetNotSet(SessionRaisesBase):

    def _set_target(self):
        pass

    @property
    def _exceptioncls(self):
        return RunnerTargetNotSet

    def _verify_exception_msg(self, msg):
        assert msg == (
            'Runner target ({target}) needed for creating {envtarget} is not set'
            '{envtarget}'.format(
                target=self.target,
                envtarget=self.envtarget))
