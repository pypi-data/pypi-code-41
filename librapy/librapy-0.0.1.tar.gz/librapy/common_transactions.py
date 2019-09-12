#!/usr/bin/env python3

"""
This is a wrapper around common transactions to limit exposure to the various
facilities that go into generating and processing transactions.
"""

from grpc import insecure_channel

import time
import urllib.parse
import urllib.request

from librapy.types.account_resource import AccountResource
from librapy.lib.lcs import Serializer
from librapy.programs.programs import CreateAccount, Mint, PeerToPeerTransfer
from librapy.proto.admission_control_pb2 import SubmitTransactionRequest
from librapy.proto.admission_control_pb2_grpc import AdmissionControlStub
from librapy.proto.get_with_proof_pb2 import UpdateToLatestLedgerRequest
from librapy.types.transactions import RawTransaction

MAX_GAS_AMOUNT = 140000
GAS_UNIT_PRICE = 0
EXPIRATION_TIME = 100


def create_account(ac_uri, faucet_account, account_address, initial_amount):
    ac = get_admission_control(ac_uri)
    request = SubmitTransactionRequest()
    serializer = Serializer()
    signed_txn = serializer.encode_struct(RawTransaction(
        faucet_account.get_address(),
        faucet_account.sequence_number,
        CreateAccount(
            account_address,
            initial_amount * 10**6,
        ),
        MAX_GAS_AMOUNT,
        GAS_UNIT_PRICE,
        int(time.time()) + EXPIRATION_TIME,
    ).sign(faucet_account.get_signing_key())).get_buffer()

    request.signed_txn.signed_txn = signed_txn
    return ac.SubmitTransaction(request)


def get_account_state(ac_uri, account):
    ac = get_admission_control(ac_uri)
    request = UpdateToLatestLedgerRequest()
    requested_item = request.requested_items.add()
    requested_item.get_account_state_request.address = \
        account.get_address().value
    response = ac.UpdateToLatestLedger(request) \
        .response_items[0] \
        .get_account_state_response \
        .account_state_with_proof

    if not response.HasField('blob'):
        return False
    account_resource = AccountResource.from_blob(response.blob.blob)
    account.update(account_resource)
    return True


def get_admission_control(ac_uri):
    channel = insecure_channel(ac_uri)
    return AdmissionControlStub(channel)


def mint_remotely(mint_uri, account, amount):
    post_data = {
        "amount": amount * 10**6,
        "address": account.get_address().value.hex(),
    }
    request = urllib.request.Request(
        mint_uri + "/?" + urllib.parse.urlencode(post_data),
        b'',
    )
    try:
        return urllib.request.urlopen(request).read().decode()
    except urllib.error.HTTPError as err:
        # Need error logging / better error handling
        raise err


def mint_with_key(ac_uri, faucet_account, account_address, amount):
    ac = get_admission_control(ac_uri)
    request = SubmitTransactionRequest()
    serializer = Serializer()
    signed_txn = serializer.encode_struct(RawTransaction(
        faucet_account.get_address(),
        faucet_account.sequence_number,
        Mint(account_address, amount * 10**6),
        MAX_GAS_AMOUNT,
        GAS_UNIT_PRICE,
        int(time.time()) + EXPIRATION_TIME,
    ).sign(faucet_account.get_signing_key())).get_buffer()

    request.signed_txn.signed_txn = signed_txn
    return ac.SubmitTransaction(request)


def transfer(ac_uri, from_account, to_account_address, amount):
    ac = get_admission_control(ac_uri)
    request = SubmitTransactionRequest()
    serializer = Serializer()
    signed_txn = serializer.encode_struct(RawTransaction(
        from_account.get_address(),
        from_account.sequence_number,
        PeerToPeerTransfer(to_account_address, amount * 10**6),
        MAX_GAS_AMOUNT,
        GAS_UNIT_PRICE,
        int(time.time()) + EXPIRATION_TIME,
    ).sign(from_account.get_signing_key())).get_buffer()

    request.signed_txn.signed_txn = signed_txn
    return ac.SubmitTransaction(request)
