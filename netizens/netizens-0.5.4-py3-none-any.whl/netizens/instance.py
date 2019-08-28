# -*- coding: utf-8 -*-
from graphenecommon.instance import AbstractBlockchainInstanceProvider, SharedInstance


class BlockchainInstance(AbstractBlockchainInstanceProvider):
    """ This is a class that allows compatibility with previous
        naming conventions
    """

    def __init__(self, *args, **kwargs):
        # Also allow 'netizens_instance'
        if kwargs.get("netizens_instance"):
            kwargs["blockchain_instance"] = kwargs["netizens_instance"]
        AbstractBlockchainInstanceProvider.__init__(self, *args, **kwargs)

    def get_instance_class(self):
        """ Should return the Chain instance class, e.g. `netizens.Netizens`
        """
        import netizens as ntz

        return ntz.Netizens

    @property
    def netizens(self):
        """ Alias for the specific blockchain
        """
        return self.blockchain


def shared_blockchain_instance():
    return BlockchainInstance().shared_blockchain_instance()


def set_shared_blockchain_instance(instance):
    instance.clear_cache()
    instance.set_shared_instance()


def set_shared_config(config):
    shared_blockchain_instance().set_shared_config(config)


shared_netizens_instance = shared_blockchain_instance
set_shared_netizens_instance = set_shared_blockchain_instance
