#!/usr/bin/env python3

"""
Collection of all the components associated with an account.
"""


class Account:
    def __init__(self, address, signing_key):
        self.address = address
        self.signing_key = signing_key
        self.balance = 0
        self.sequence_number = 0

    def __repr__(self):
        return (
            "Account("
            "\n\taddress: {}"
            "\n\tbalance: {}"
            "\n\tsequence_number: {}"
            "\n\tpublic_key: {}"
            "\n)"
        ).format(
            self.address,
            self.balance,
            self.sequence_number,
            self.signing_key.verify_key.encode().hex(),
        )

    def get_address(self):
        return self.address

    def get_signing_key(self):
        return self.signing_key

    def update(self, account_resource):
        self.balance = account_resource.balance
        self.sequence_number = account_resource.sequence_number
