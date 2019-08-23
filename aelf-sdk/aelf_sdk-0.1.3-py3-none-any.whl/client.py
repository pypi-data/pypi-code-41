import hashlib

import base58
import requests
from coincurve import PrivateKey

from aelf.types_pb2 import Transaction, Hash, Address, MinerList, StringInput, CandidateVote, PublicKeysList


class AElf(object):
    _get_request_header = None
    _post_request_header = None

    _url = None
    _private_key = None
    _version = None

    def __init__(self, url='http://127.0.0.1:8000', private_key=None, version=None):
        self._url = '%s/api' % url
        if private_key is not None:
            self._private_key = PrivateKey(bytes(bytearray.fromhex(private_key)))

        version = '' if version is None else ';v=%s' % version
        self._post_request_header = {'Content-Type': 'application/json' + version}
        self._get_request_header = {'Accept': 'application/json' + version}

    def get_chain_status(self):
        """
        Get chain status
        :return: chain status
        """
        return requests.get('%s/blockchain/chainStatus' % self._url, headers=self._get_request_header).json()

    def get_block_height(self):
        """
        Get block height
        :return: block height
        """
        block_height = requests.get('%s/blockchain/blockHeight' % self._url, headers=self._get_request_header).content
        return int(block_height)

    def get_block(self, block_hash, include_transactions=False):
        """
        Get block
        :param block_hash: block hash
        :param include_transactions: whether include transactions
        :return: block
        """
        api = '%s/blockchain/block?includeTransactions=%s&blockHash=%s' % (self._url, include_transactions, block_hash)
        return requests.get(api, headers=self._get_request_header).json()

    def get_block_by_height(self, block_height, include_transactions=False):
        """
        Get block by height
        :param block_height: block height
        :param include_transactions: whether include transaction
        :return: block
        """
        api = '%s/blockchain/blockByHeight?includeTransactions=%s&blockHeight=%s' % (
            self._url, include_transactions, block_height)
        return requests.get(api, headers=self._get_request_header).json()

    def get_transaction_pool_status(self):
        """
        Get transaction pool status
        :return: transaction pool status
        """
        return requests.get('%s/blockchain/transactionPoolStatus' % self._url, headers=self._get_request_header).json()

    def create_raw_transaction(self, transaction):
        """
        Create raw transaction
        :param transaction: the json format transaction
            {
              "From": "string",
              "To": "string",
              "RefBlockNumber": 0,
              "RefBlockHash": "string",
              "MethodName": "string",
              "Params": "string"
            }
        :return: the raw transaction string
        """
        return requests.post('%s/blockchain/rawTransaction' % self._url,
                             json=transaction, headers=self._post_request_header).json()

    def send_transaction(self, transaction):
        """
        Send transaction
        :param transaction: transaction hex string
        :return: transaction id
        """
        return requests.post('%s/blockchain/sendTransaction' % self._url,
                             json={'RawTransaction': transaction}, headers=self._post_request_header).json()

    def send_raw_transaction(self, raw_transaction):
        """
        Send raw transaction
        :param raw_transaction: the json format transaction
            {
              "Transaction": "string",
              "Signature": "string",
              "ReturnTransaction": true
            }
        :return: transaction id
        """
        return requests.post('%s/blockchain/sendRawTransaction' % self._url,
                             json=raw_transaction, headers=self._post_request_header).json()

    def send_transactions(self, transactions):
        """
        Send transactions
        :param transactions: transactions (join by ',')
        :return: the list of transaction ids
        """
        return requests.post('%s/blockchain/sendTransaction' % self._url,
                             json={'RawTransactions': transactions}, headers=self._post_request_header).json()

    def execute_transaction(self, transaction):
        """
        Execute transaction
        :param transaction: Transaction object or transaction hex string
        :return: executed result
        """
        if isinstance(transaction, Transaction):
            transaction = transaction.SerializePartialToString().hex()

        response = requests.post('%s/blockchain/executeTransaction' % self._url,
                                 json={'RawTransaction': transaction},
                                 headers=self._post_request_header)
        return response.content

    def execute_raw_transaction(self, raw_transaction):
        """
        Execute raw transaction
        :param raw_transaction: raw transaction
        :return: executed result
        """
        return requests.post('%s/blockchain/executeRawTransaction' % self._url,
                             json=raw_transaction, headers=self._post_request_header).json()

    def get_transaction_result(self, transaction_id):
        """
        Get transaction result
        :param transaction_id: transaction id
        :return: transaction result
        """
        api = '%s/blockchain/transactionResult?transactionId=%s' % (self._url, transaction_id)
        return requests.get(api, headers=self._get_request_header).json()

    def get_transaction_results(self, block_hash):
        """
        Get transaction results
        :param block_hash: block hash
        :return: transaction results
        """
        api = '%s/blockchain/transactionResults?blockHash=%s' % (self._url, block_hash)
        return requests.get(api, headers=self._get_request_header).json()

    def get_peers(self):
        """
        Get peers
        """
        return requests.get('%s/net/peers' % self._url, headers=self._get_request_header).json()

    def add_peer(self, peer_address):
        """
        Add peer
        :param peer_address: peer address
        :return: True/False
        """
        json_data = {'Address': peer_address}
        return requests.post('%s/net/peer' % self._url, json=json_data, headers=self._post_request_header).json()

    def remove_peer(self, address):
        """
        Remove peer
        :param address: peer address
        :return: True/False
        """
        api = '%s/net/peer?address=%s' % (self._url, address)
        status_code = requests.delete(api, headers=self._get_request_header).status_code
        return status_code == 200

    def get_network_info(self):
        """
        Get network info
        :return: network info
        """
        return requests.get('%s/net/networkInfo' % self._url, headers=self._get_request_header).json()

    def get_task_queue_status(self):
        """
        Get task queue status
        :return: task queue status
        """
        return requests.get('%s/blockchain/taskQueueStatus' % self._url, headers=self._get_request_header).json()

    def get_merkle_path(self, transaction_id):
        """
        Get task queue status
        :return: task queue status
        """
        api = '%s/blockChain/merklePathByTransactionId?transactionId=%s' % (self._url, transaction_id)
        return requests.get(api, headers=self._get_request_header).json()

    def get_current_miners(self):
        """
        Get current miners
        :return: current miners
        """
        transaction = self._get_miners_transaction()
        raw_miner_list = self.execute_transaction(transaction)

        current_miners = []
        miner_list = MinerList()
        miner_list.ParseFromString(bytes.fromhex(raw_miner_list.decode()))
        for miner in miner_list.public_keys:
            address = self._get_from_address(miner)
            current_miners.append({
                'public_key': miner.hex(),
                'address': base58.b58encode_check(address.Value)
            })
        return current_miners

    def get_from_address(self):
        """
        Get self from address
        :return: from address (Address object)
        """
        return self._get_from_address(self._private_key.public_key.format(compressed=False))

    def get_from_address_string(self):
        """
        Get self from address string
        :return: from address string
        """
        address = self.get_from_address()
        return base58.b58encode_check(address.Value).decode()

    def get_system_contract_address(self, contract_name):
        """
        Get system contract address
        :param contract_name: system contract name
        :return: contract address object
        """
        transaction = self._get_contract_address_transaction(contract_name)
        raw_address_hex = self.execute_transaction(transaction)
        to_address = Address()
        to_address.ParseFromString(bytes.fromhex(raw_address_hex.decode()))
        return to_address

    def get_system_contract_address_string(self, contract_name):
        """
        Get system contract address
        :param contract_name: system contract name
        :return: contract address base58 string
        """
        to_address = self.get_system_contract_address(contract_name)
        return base58.b58encode_check(to_address.Value).decode()

    def get_candidates(self):
        """
        Get candidates
        :return: candidates
        """
        candidates = []
        transaction = self._get_candidates_transaction()
        raw_candidates = self.execute_transaction(transaction)
        public_key_list = PublicKeysList()
        public_key_list.ParseFromString(bytes.fromhex(raw_candidates.decode()))
        for public_key in public_key_list.value:
            address = self._get_from_address(public_key)
            candidates.append({
                'public_key': public_key.hex(),
                'address': base58.b58encode_check(address.Value)
            })
        return candidates

    def get_vote_info(self, public_keys):
        """
        Get vote info
        :param public_keys: public key for candidates/miners
        :return:
        """
        vote_info = []
        for public_key in public_keys:
            transaction = self._get_candidate_vote_transaction(public_key)
            raw_candidate_vote = self.execute_transaction(transaction)
            candidate_vote = CandidateVote()
            candidate_vote.ParseFromString(bytes.fromhex(raw_candidate_vote.decode()))
            vote_info.append({
                'obtained_active_voted_votes_amount': candidate_vote.obtained_active_voted_votes_amount,
                'all_obtained_voted_votes_amount': candidate_vote.all_obtained_voted_votes_amount
            })
        return vote_info

    def build_transaction(self, to_address, method_name, params=None):
        """
        Build transaction
        :param to_address: to address
        :param method_name: method name
        :param params: params for method
        :return: transaction object
        """
        assert self._private_key is not None, 'To execute transaction, please initialize AElf with private key.'

        chain_status = self.get_chain_status()
        best_chain_hash = chain_status['BestChainHash']
        best_chain_height = chain_status['BestChainHeight']

        transaction = Transaction()
        transaction.From.CopyFrom(self._get_from_address(self._private_key.public_key.format(compressed=False)))
        transaction.To.CopyFrom(to_address)
        transaction.MethodName = method_name
        if params is not None:
            transaction.Params = params
        transaction.RefBlockNumber = best_chain_height
        transaction.RefBlockPrefix = bytes(bytearray.fromhex(best_chain_hash))
        transaction.Signature = self.sign(transaction.SerializeToString())
        return transaction

    def sign(self, bytes_data):
        """
        Sign
        :param bytes_data: the data need sign
        :return: the signed data
        """
        return self._private_key.sign_recoverable(bytes_data)

    def _get_genesis_contract_address(self):
        """ get genesis contract address
        """
        response = requests.get('%s/blockchain/chainStatus' % self._url, headers=self._get_request_header)
        chain_status = response.json()
        genesis_contract_address = chain_status['GenesisContractAddress']
        return genesis_contract_address

    def _get_from_address(self, public_key):
        """ get from address
        """
        address = Address()
        public_key_hash = hashlib.sha256()
        public_key_hash.update(hashlib.sha256(public_key).digest())
        address.Value = public_key_hash.digest()
        return address

    def _get_contract_address_transaction(self, contract_name):
        """ build get contract address transaction
        """
        to_address_bytes = base58.b58decode_check(self._get_genesis_contract_address())
        to_address = Address()
        to_address.Value = to_address_bytes
        params = Hash()
        params.Value = hashlib.sha256(contract_name.encode('utf8')).digest()
        return self.build_transaction(to_address, 'GetContractAddressByName', params.SerializeToString())

    def _get_candidates_transaction(self):
        """ get candidates transaction
        """
        transaction = self._get_contract_address_transaction('AElf.ContractNames.Election')
        address = self.execute_transaction(transaction)
        to_address = Address()
        to_address.ParseFromString(bytes.fromhex(address.decode()))
        return self.build_transaction(to_address, 'GetCandidates')

    def _get_candidate_vote_transaction(self, block_producer):
        """ get candidate vote transaction
        """
        transaction = self._get_contract_address_transaction('AElf.ContractNames.Election')
        address = self.execute_transaction(transaction)
        to_address = Address()
        to_address.ParseFromString(bytes.fromhex(address.decode()))
        params = StringInput()
        params.StringValue = block_producer
        return self.build_transaction(to_address, 'GetCandidateVote', params.SerializeToString())

    def _get_miners_transaction(self):
        """ build get miners transaction
        """
        transaction = self._get_contract_address_transaction('AElf.ContractNames.Consensus')
        raw_address_hex = self.execute_transaction(transaction)
        to_address = Address()
        to_address.ParseFromString(bytes.fromhex(raw_address_hex.decode()))
        return self.build_transaction(to_address, 'GetCurrentMinerList')
