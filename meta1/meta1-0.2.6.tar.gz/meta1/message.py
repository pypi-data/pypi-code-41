# -*- coding: utf-8 -*-
from graphenecommon.message import Message as GrapheneMessage, InvalidMessageSignature
from meta1base.account import PublicKey

from .account import Account
from .instance import BlockchainInstance
from .exceptions import InvalidMemoKeyException, AccountDoesNotExistsException, WrongMemoKey


@BlockchainInstance.inject
class Message(GrapheneMessage):
    MESSAGE_SPLIT = (
        "-----BEGIN META1 SIGNED MESSAGE-----",
        "-----BEGIN META-----",
        "-----BEGIN SIGNATURE-----",
        "-----END META1 SIGNED MESSAGE-----",
    )

    def define_classes(self):
        self.account_class = Account
        self.publickey_class = PublicKey
