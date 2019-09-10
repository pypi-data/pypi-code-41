from crl.remotesession.envcreatorbase import EnvCreatorBase


__copyright__ = 'Copyright (C) 2019, Nokia'


class ExampleEnvCreator(EnvCreatorBase):

    def __init__(self, envdictcreator):
        self._envdictcreator = envdictcreator

    def create(self, target, envname):
        return self._envdictcreator(target, envname)
