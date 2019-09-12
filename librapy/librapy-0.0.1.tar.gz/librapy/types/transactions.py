#!/usr/bin/env python3

"""
Core components for constructing and parsing Libra transactions
"""

from nacl.signing import VerifyKey

from librapy.lib.common import InvalidInstanceException
from librapy.lib.lcs import Serializer
from librapy.types.account_address import AccountAddress
from librapy.types.program import Program

import librapy.lib.hasher as hasher


class TransactionPayload:
    def __init__(self, value):
        self.value = value

    def __repr__(self):
        return "TransactionPayload({})".format(self.value)

    def type_to_u32(self):
        if isinstance(self.value, Program):
            return 0
        if isinstance(self.value, WriteSet):
            return 1
        if isinstance(self.value, Module):
            return 2
        if isinstance(self.value, Script):
            return 3
        raise InvalidInstanceException(self.value)

    def deserialize(deserializer):
        value_type = deserializer.decode_u32()
        if value_type == 0:
            return deserializer.decode_struct(Program)
        if value_type == 1:
            return deserializer.decode_struct(WriteSet)
        if value_type == 2:
            return deserializer.decode_struct(Module)
        if value_type == 3:
            return deserializer.decode_struct(Script)
        raise InvalidInstanceException(value_type)

    def serialize(self, serializer):
        serializer.encode_u32(self.type_to_u32())
        serializer.encode_struct(self.value)
        return serializer


class WriteSet:
    pass


class Module:
    pass


class Script:
    pass


class RawTransaction:
    def __init__(
        self,
        sender,
        sequence_number,
        payload,
        max_gas_amount,
        gas_unit_price,
        expiration,
    ):
        self.sender = sender
        self.sequence_number = sequence_number
        self.payload = TransactionPayload(payload)
        self.max_gas_amount = max_gas_amount
        self.gas_unit_price = gas_unit_price
        self.expiration = expiration

    def __repr__(self):
        return (
            "RawTransaction ("
            "\n\tsender: {}"
            "\n\tsequence_number: {}"
            "\n\tpayload: {}"
            "\n\tmax_gas_amount: {}"
            "\n\tgas_unit_price: {}"
            "\n\texpiration: {}"
            "\n)"
        ).format(
            self.sender,
            self.sequence_number,
            self.payload,
            self.max_gas_amount,
            self.gas_unit_price,
            self.expiration,
        )

    def deserialize(deserializer):
        return RawTransaction(
            deserializer.decode_struct(AccountAddress),
            deserializer.decode_u64(),
            deserializer.decode_struct(TransactionPayload),
            deserializer.decode_u64(),
            deserializer.decode_u64(),
            deserializer.decode_u64(),
        )

    @classmethod
    def get_hash_prefix(cls):
        return b"RawTransaction"

    def serialize(self, serializer):
        serializer.encode_struct(self.sender)
        serializer.encode_u64(self.sequence_number)
        serializer.encode_struct(self.payload)
        serializer.encode_u64(self.max_gas_amount)
        serializer.encode_u64(self.gas_unit_price)
        serializer.encode_u64(self.expiration)
        return serializer

    def sign(self, signing_key):
        serializer = Serializer()
        self.serialize(serializer)

        hf = hasher.get_hash_function(self)
        hf.update(serializer.get_buffer())
        raw_txn_hash = hf.digest()
        signature = signing_key.sign(raw_txn_hash).signature

        return SignedTransaction(self, signing_key.verify_key, signature)


class SignedTransaction:
    def __init__(self, raw_txn, public_key, signature):
        self.raw_txn = raw_txn
        self.public_key = public_key
        self.signature = signature

    def __repr__(self):
        return (
            "SignedTransaction ("
            "\n\traw_txn: {}"
            "\n\tpublic_key: {}"
            "\n\tsignature: {}"
            "\n)"
        ).format(
            self.raw_txn,
            self.public_key.encode().hex(),
            self.signature.hex(),
        )

    def deserialize(deserializer):
        return SignedTransaction(
            deserializer.decode_struct(RawTransaction),
            VerifyKey(deserializer.decode_bytes()),
            deserializer.decode_bytes(),
        )

    def serialize(self, serializer):
        serializer.encode_struct(self.raw_txn)
        serializer.encode_bytes(self.public_key.encode())
        serializer.encode_bytes(self.signature)
        return serializer
