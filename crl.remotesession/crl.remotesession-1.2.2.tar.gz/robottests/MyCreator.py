from crl.remotesession.envcreatorbase import EnvCreatorBase


class MyCreator(EnvCreatorBase):
    @staticmethod
    def create(target, envname):
        return {envname: 'barfoo'}
