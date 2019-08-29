"""Keeper module to call keeper-contracts."""
#  Copyright 2018 Ocean Protocol Foundation
#  SPDX-License-Identifier: Apache-2.0

import logging
import os

from eth_utils import big_endian_to_int

from ocean_keeper.agreements.agreement_manager import AgreementStoreManager
from ocean_keeper.conditions.access import AccessSecretStoreCondition
from ocean_keeper.conditions.condition_manager import ConditionStoreManager
from ocean_keeper.conditions.escrow_reward import EscrowRewardCondition
from ocean_keeper.conditions.hash_lock import HashLockCondition
from ocean_keeper.conditions.lock_reward import LockRewardCondition
from ocean_keeper.conditions.sign import SignCondition
from ocean_keeper.didregistry import DIDRegistry
from ocean_keeper.dispenser import Dispenser
from ocean_keeper.generic_contract import GenericContract
from ocean_keeper.templates.access_secret_store_template import EscrowAccessSecretStoreTemplate
from ocean_keeper.templates.template_manager import TemplateStoreManager
from ocean_keeper.token import Token
from ocean_keeper.utils import split_signature, generate_multi_value_hash
from ocean_keeper.wallet import Wallet
from ocean_keeper.web3.signature import SignatureFix
from ocean_keeper.web3_provider import Web3Provider


class Keeper(object):
    """The Keeper class aggregates all contracts in the Ocean Protocol node."""

    DEFAULT_NETWORK_NAME = 'development'
    _network_name_map = {
        1: 'Main',
        2: 'Morden',
        3: 'Ropsten',
        4: 'Rinkeby',
        42: 'Kovan',
        77: 'POA_Sokol',
        99: 'POA_Core',
        8995: 'nile',
        8996: 'spree',
        2199: 'duero',
        0xcea11: 'pacific'
    }

    def __init__(self, artifacts_path, contract_names=None):
        self.network_name = Keeper.get_network_name(Keeper.get_network_id())
        self.artifacts_path = artifacts_path
        self.accounts = Web3Provider.get_web3().eth.accounts
        self._contract_name_to_instance = {}
        if contract_names:
            for name in contract_names:
                contract = GenericContract(name)
                self._contract_name_to_instance = contract
                setattr(self, name, contract)

        self.dispenser = None
        if self.network_name != 'pacific':
            self.dispenser = Dispenser.get_instance()
        self.token = Token.get_instance()
        self.did_registry = DIDRegistry.get_instance()
        self.template_manager = TemplateStoreManager.get_instance()
        self.escrow_access_secretstore_template = EscrowAccessSecretStoreTemplate.get_instance()
        self.agreement_manager = AgreementStoreManager.get_instance()
        self.condition_manager = ConditionStoreManager.get_instance()
        self.sign_condition = SignCondition.get_instance()
        self.lock_reward_condition = LockRewardCondition.get_instance()
        self.escrow_reward_condition = EscrowRewardCondition.get_instance()
        self.access_secret_store_condition = AccessSecretStoreCondition.get_instance()
        self.hash_lock_condition = HashLockCondition.get_instance()
        contracts = [
            self.token,
            self.did_registry,
            self.template_manager,
            self.escrow_access_secretstore_template,
            self.agreement_manager,
            self.condition_manager,
            self.sign_condition,
            self.lock_reward_condition,
            self.escrow_reward_condition,
            self.access_secret_store_condition,
            self.hash_lock_condition
        ]
        if self.dispenser:
            contracts.append(self.dispenser)
        self._contract_name_to_instance = {contract.name: contract
                                           for contract in contracts if contract}

    @staticmethod
    def get_instance(artifacts_path=None, contract_names=None):
        """Return the Keeper instance (singleton)."""
        return Keeper(artifacts_path, contract_names)

    @staticmethod
    def get_network_name(network_id):
        """
        Return the keeper network name based on the current ethereum network id.
        Return `development` for every network id that is not mapped.

        :param network_id: Network id, int
        :return: Network name, str
        """
        if os.environ.get('KEEPER_NETWORK_NAME'):
            logging.debug('keeper network name overridden by an environment variable: {}'.format(
                os.environ.get('KEEPER_NETWORK_NAME')))
            return os.environ.get('KEEPER_NETWORK_NAME')

        return Keeper._network_name_map.get(network_id, Keeper.DEFAULT_NETWORK_NAME)

    @staticmethod
    def get_network_id():
        """
        Return the ethereum network id calling the `web3.version.network` method.

        :return: Network id, int
        """
        return int(Web3Provider.get_web3().version.network)

    @staticmethod
    def sign_hash(msg_hash, account):
        """
        This method use `personal_sign`for signing a message. This will always prepend the
        `\x19Ethereum Signed Message:\n32` prefix before signing.

        :param msg_hash:
        :param account: Account
        :return: signature
        """
        wallet = Wallet(Web3Provider.get_web3(), account.key_file, account.password, account.address)
        s = wallet.sign(msg_hash)
        return s.signature.hex()

    @staticmethod
    def ec_recover(message, signed_message):
        """
        This method does not prepend the message with the prefix `\x19Ethereum Signed Message:\n32`.
        The caller should add the prefix to the msg/hash before calling this if the signature was
        produced for an ethereum-prefixed message.

        :param message:
        :param signed_message:
        :return:
        """
        w3 = Web3Provider.get_web3()
        v, r, s = split_signature(w3, w3.toBytes(hexstr=signed_message))
        signature_object = SignatureFix(vrs=(v, big_endian_to_int(r), big_endian_to_int(s)))
        return w3.eth.account.recoverHash(message, signature=signature_object.to_hex_v_hacked())

    @staticmethod
    def unlock_account(account):
        """
        Unlock the account.

        :param account: Account
        :return:
        """
        return Web3Provider.get_web3().personal.unlockAccount(account.address, account.password)

    @staticmethod
    def get_ether_balance(address):
        """
        Get balance of an ethereum address.

        :param address: address, bytes32
        :return: balance, int
        """
        return Web3Provider.get_web3().eth.getBalance(address, block_identifier='latest')

    @property
    def contract_name_to_instance(self):
        return self._contract_name_to_instance

    def get_contract(self, contract_name):
        contract = self.contract_name_to_instance.get(contract_name)
        if contract:
            return contract

        try:
            return GenericContract(contract_name)
        except Exception as e:
            logging.error(f'Cannot load contract {contract_name}: {e}')
            return None

    @staticmethod
    def generate_multi_value_hash(types, values):
        return generate_multi_value_hash(types, values)
