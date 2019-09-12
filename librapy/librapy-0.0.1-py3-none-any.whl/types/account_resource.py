#!/usr/bin/env python3

"""
Libra wraps account information with an AccountResource
"""

from librapy.lib.lcs import byte_decoder, Deserializer
from librapy.types.account_address import AccountAddress
from librapy.types.resources import AccessPath, StructTag


class AccountResource:
    module_name = "LibraAccount"
    struct_name = "T"

    def __init__(
        self,
        authentication_key,
        balance,
        delegated_withdrawal_capability,
        received_events,
        sent_events,
        sequence_number,
    ):
        self.authentication_key = authentication_key
        self.balance = balance
        self.delegated_withdrawal_capability = delegated_withdrawal_capability
        self.received_events = received_events
        self.sent_events = sent_events
        self.sequence_number = sequence_number

    def __repr__(self):
        return (
            "AccountResource ("
            "\n\tbalance: {}"
            "\n\tsequence_number: {}"
            "\n\tauthentication_key: {}"
            "\n\tdelegated_withdrawal_capability: {}"
            "\n\tsent_events: {}"
            "\n\treceived_events: {}"
            "\n)"
        ).format(
            self.balance,
            self.sequence_number,
            self.authentication_key.hex(),
            self.delegated_withdrawal_capability,
            self.sent_events,
            self.received_events,
        )

    def deserialize(deserializer):
        return AccountResource(
            deserializer.decode_bytes(),
            deserializer.decode_u64(),
            deserializer.decode_bool(),
            deserializer.decode_struct(EventHandle),
            deserializer.decode_struct(EventHandle),
            deserializer.decode_u64(),
        )

    def from_blob(blob):
        deserializer = Deserializer(blob)
        account_map = deserializer.decode_map(byte_decoder, byte_decoder)
        tag = StructTag(
            AccountAddress.default(),
            AccountResource.module_name,
            AccountResource.struct_name,
            [],
        )
        access_path = AccessPath.resource_access_vec(tag, [])
        value = account_map.get(access_path)
        if value is None:
            return None
        deserializer = Deserializer(value)
        return deserializer.decode_struct(AccountResource)


class EventHandle:
    def __init__(self, key, count):
        self.key = key
        self.count = count

    def __repr__(self):
        return "EventHandle(Key: {}, Count: {})".format(self.key, self.count)

    def deserialize(deserializer):
        return EventHandle(
            deserializer.decode_u64(),
            deserializer.decode_struct(EventKey),
        )


class EventKey:
    def __init__(self, value):
        self.value = value

    def __repr__(self):
        return "EventKey({})".format(self.value.hex())

    def deserialize(deserializer):
        return EventKey(deserializer.decode_bytes())
