from crl.remotesession.envcreatorbase import EnvCreatorBase


__copyright__ = 'Copyright (C) 2019, Nokia'


class AtestExampleEnvCreator(EnvCreatorBase):

    def __init__(self, source, remotesession):
        self._source = source
        self._remotesession = remotesession

    def create(self, target, envname):
        source_update_dict = self._remotesession.get_source_update_env_dict(
            path=self._source,
            target=target)
        source_update_dict.update(self.get_update_dict(envname))
        return source_update_dict

    @staticmethod
    def get_update_dict(envname):
        return {envname: 'envname-example'}
