#!/usr/bin/env python3

"""
Provides core programs (wrappers around scripts) for basic Libra functionality
"""

import os.path

from librapy.types.program import Program, TransactionArgument


class CreateAccount(Program):
    def __init__(self, address, initial_amount):
        super().__init__(
            [
                TransactionArgument(address),
                TransactionArgument(initial_amount),
            ],
        )

    def get_path(self):
        return os.path.join(os.path.dirname(__file__), 'create_account.prg')


class Mint(Program):
    def __init__(self, sender, amount):
        super().__init__(
            [
                TransactionArgument(sender),
                TransactionArgument(amount),
            ],
        )

    def get_path(self):
        return os.path.join(os.path.dirname(__file__), 'mint.prg')


class PeerToPeerTransfer(Program):
    def __init__(self, payee, amount):
        super().__init__(
            [
                TransactionArgument(payee),
                TransactionArgument(amount),
            ],
        )

    def get_path(self):
        return os.path.join(
            os.path.dirname(__file__),
            'peer_to_peer_transfer.prg',
        )


class RotateAuthenticationKey(Program):
    def __init__(self, key):
        super().__init__([TransactionArgument(key)])

    def get_path(self):
        return os.path.join(
            os.path.dirname(__file__),
            'rotate_authentication_key.prg',
         )
