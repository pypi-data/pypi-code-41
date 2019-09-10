__copyright__ = 'Copyright (C) 2019, Nokia'


class RemoteSessionError(Exception):
    pass


class SessionTargetIsNotSet(RemoteSessionError):
    pass


class SessionBackgroundExecIdAlreadyInUse(RemoteSessionError):
    pass


class SessionExecIdIsNotSet(RemoteSessionError):
    pass


class ExecFailedError(RemoteSessionError):
    pass


class NotImplementedInRemoteScript(RemoteSessionError):
    pass


class RunnerTargetNotSet(RemoteSessionError):
    pass
