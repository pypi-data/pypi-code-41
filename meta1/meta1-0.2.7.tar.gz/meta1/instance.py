# -*- coding: utf-8 -*-
from graphenecommon.instance import AbstractBlockchainInstanceProvider


class SharedInstance:
    """ This class merely offers a singelton for the Blockchain Instance
    """

    instance = None
    config = {}


class BlockchainInstance(AbstractBlockchainInstanceProvider):
    """ This is a class that allows compatibility with previous
        naming conventions
    """

    _sharedInstance = SharedInstance

    def __init__(self, *args, **kwargs):
        # Also allow 'meta1_instance'
        if kwargs.get("meta1_instance"):
            kwargs["blockchain_instance"] = kwargs["meta1_instance"]
        AbstractBlockchainInstanceProvider.__init__(self, *args, **kwargs)

    def get_instance_class(self):
        """ Should return the Chain instance class, e.g. `meta1.Meta1`
        """
        import meta1 as meta1

        return meta1.Meta1

    @property
    def meta1(self):
        """ Alias for the specific blockchain
        """
        return self.blockchain


def shared_blockchain_instance():
    return BlockchainInstance().shared_blockchain_instance()


def set_shared_blockchain_instance(instance):
    instance.clear_cache()
    # instance.set_shared_instance()
    BlockchainInstance.set_shared_blockchain_instance(instance)


def set_shared_config(config):
    BlockchainInstance.set_shared_config(config)


shared_meta1_instance = shared_blockchain_instance
set_shared_meta1_instance = set_shared_blockchain_instance
