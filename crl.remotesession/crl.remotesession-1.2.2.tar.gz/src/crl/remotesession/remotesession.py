from .remotesessionexec import RemoteSessionExec
from .remotesessionfile import RemoteSessionFile


__copyright__ = 'Copyright (C) 2019, Nokia'


class RemoteSession(RemoteSessionExec,
                    RemoteSessionFile):
    pass
