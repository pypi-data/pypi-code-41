# -*- coding: utf-8 -*-
from .account import Account
from .instance import BlockchainInstance
from graphenecommon.genesisbalance import (
    GenesisBalance as GrapheneGenesisBalance,
    GenesisBalances as GrapheneGenesisBalances,
)

from meta1base.account import Address, PublicKey
from meta1base import operations


@BlockchainInstance.inject
class GenesisBalance(GrapheneGenesisBalance):
    """ Read data about a Genesis Balances from the chain

        :param str identifier: identifier of the balance
        :param meta1 blockchain_instance: meta1() instance to use when
            accesing a RPC

    """

    type_id = 15

    def define_classes(self):
        self.account_class = Account
        self.operations = operations
        self.address_class = Address
        self.publickey_class = PublicKey


@BlockchainInstance.inject
class GenesisBalances(GrapheneGenesisBalances):
    """ List genesis balances that can be claimed from the
        keys in the wallet
    """

    def define_classes(self):
        self.genesisbalance_class = GenesisBalance
        self.publickey_class = PublicKey
        self.address_class = Address
