import pytest
from crl.remotesession.exceptions import (
    RemoteSessionError,
    SessionTargetIsNotSet,
    SessionBackgroundExecIdAlreadyInUse,
    SessionExecIdIsNotSet,
    ExecFailedError,
    NotImplementedInRemoteScript,
    RunnerTargetNotSet)


__copyright__ = 'Copyright (C) 2019, Nokia'


@pytest.mark.parametrize('exccls', [
    SessionTargetIsNotSet,
    SessionBackgroundExecIdAlreadyInUse,
    SessionExecIdIsNotSet,
    ExecFailedError,
    NotImplementedInRemoteScript,
    RunnerTargetNotSet])
def test_exceptions_are_remotesessionerrors(exccls):
    with pytest.raises(RemoteSessionError):
        raise exccls()
