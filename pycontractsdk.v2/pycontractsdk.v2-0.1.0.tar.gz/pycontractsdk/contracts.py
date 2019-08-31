# -*- coding: utf-8 -*-

import time
import sys
import re
import json
import logging
from web3 import Web3, HTTPProvider, IPCProvider, WebsocketProvider
from web3.contract import ConciseContract
import eth_account, eth_utils
from pycontractsdk import keys, utils, config


log = logging.getLogger(__name__)
log.setLevel(logging.DEBUG)
formatter = logging.Formatter('%(asctime)s - %(name)s - %(levelname)s - %(message)s')
console = logging.StreamHandler()
console.setFormatter(formatter)
log.addHandler(console)


class Contract(object):
    """
    基础协约
    定义一些基础的方法
    """
    _w3 = Web3()
    _provider = ''                  # 哪种方式连接的以太坊(http://localhost:7545 | ws://localhost:7545 | /foo/ba/x.ipc)
    _contract_address = ''          # 智能协约的address
    _abi = ''                       # 智能协约的abi
    _private_key = ''               # 用于签名的 private key

    _gas = config.GAS               # 默认的gas值
    _gas_price = config.GAS_PRICE   # 默认的gas_prise值

    def __init__(self, provider=config.PROVIDER, timeout=60, *args, **kwargs):
        self._provider = provider
        if re.match('^http://.*', provider):
            self._w3 = Web3(HTTPProvider(provider, request_kwargs={'timeout': timeout}))
        elif re.match('^ws://.*', provider):
            self._w3 = Web3(WebsocketProvider(provider))
        else:
            self._w3 = Web3(IPCProvider(provider))

        self._contract_address = kwargs.pop('contract_address', '')
        self._abi = kwargs.pop('abi', '')
        self._private_key = kwargs.pop('private_key', '')

        self._gas = kwargs.pop('gas', self._gas)
        self._gas_price = kwargs.pop('gas_prise', self._gas_price)

    @property
    def w3(self):
        return self._w3

    @property
    def contract_address(self):
        return self._contract_address

    @contract_address.setter
    def contract_address(self, contract_address):
        self._contract_address = contract_address

    @property
    def abi(self):
        return self._abi

    @abi.setter
    def abi(self, abi):
        self._abi = abi

    @property
    def private_key(self):
        return self._private_key

    @private_key.setter
    def private_key(self, private_key):
        self._private_key = private_key

    def get_receipt(self, txid):
        return self._w3.eth.getTransactionReceipt(txid)

    def check_receipts(self, txid):
        """
        根据交易id获得receipts
        :param txid: 交易ID
        :return:
        """
        try:
            # receipt = self._w3.eth.getTransactionReceipt(txid)
            receipt = self._w3.eth.waitForTransactionReceipt(txid)
        except Exception as e:
            print(e)
            receipt = None
        return receipt

    def wait_for_tx(self, txid, second=120):
        """等待交易完成"""
        sec = 0
        timeout = False
        receipt = self.check_receipts(txid)
        while (receipt == None) or (receipt != None and receipt.blockHash == None):
            time.sleep(1)
            sec += 1
            print('.', end='')
            sys.stdout.flush()
            receipt = self.check_receipts(txid)
            if sec > second:
                timeout = True
                log.info('{}  {}\'s Transaction timeout'.format(txid,sec))
                log.info('Transaction timeout!')
                break
        print('seconds:[{}]'.format(sec))
        if receipt != None and receipt.blockHash != None:
            print('receipt: ' + str(dict(receipt)))
            return True, receipt
        return False, receipt if timeout else True, receipt

    def is_tx_sucess(self, txid):
        """
        查询 txid 上链是否成功
        :param txid:
        :return:
        """
        receipt = self.check_receipts(txid)
        if (receipt == None) or (receipt != None and receipt.blockHash == None):
            return False, receipt
        if receipt != None and receipt.blockHash != None:
            return True, receipt
        return False, receipt

    def get_address_nonce(self, address):
        """
        获得 address 对应的 nonce 值
        :param address:
        :return:
        """
        web3 = self._w3
        if eth_utils.is_address(address):
            nonce = web3.eth.getTransactionCount(eth_utils.to_checksum_address(address),
                                                 block_identifier=web3.eth.defaultBlock)
        else:
            raise ValueError("%s is not a address" % address)
        return nonce

    def get_private_key_nonce(self, private_key):
        """
        获得 private_key 对应的 nonce 值
        :param private_key:
        :return:
        """
        address = keys.privatekey_to_address(private_key)
        return self.get_address_nonce(address)

    def get_last_block(self):
        return self._w3.eth.getBlock()

    def last_block_number(self):
        """ 获得当前最后一个块的块号 """
        return self._w3.eth.blockNumber

    def get_transaction(self, tx_hash):
        return self._w3.eth.getTransaction(tx_hash)

    def get_transaction_receipt(self, tx_hash):
        return self._w3.eth.getTransactionReceipt(tx_hash)

    def get_contract(self):
        """ 用于调用 function 进行写（会进行上链操作） """
        web3 = self._w3
        starcoin_address_checksum = keys.to_check_sum_address(self._contract_address)
        contract = web3.eth.contract(abi=self._abi, address=starcoin_address_checksum)
        return contract

    def get_concise_contract(self):
        """ 用于读取本地状态数据的协约 """
        web3 = self._w3
        starcoin_address_checksum = keys.to_check_sum_address(self._contract_address)
        contract = web3.eth.contract(abi=self._abi, address=starcoin_address_checksum, ContractFactoryClass=ConciseContract)
        return contract

    def send_eth(self, sender_private_key, receiver_address, eth):
        """
        转eth
        :param sender_private_key: 发送者的私钥
        :param receiver_address: 接收者的address
        :param eth: 具体的ETH数量
        :param gas:
        :return:
        """
        web3 = self._w3
        nonce = self.get_private_key_nonce(sender_private_key)
        signed_txn = web3.eth.account.signTransaction(dict(
            nonce=nonce,
            gas=self._gas,
            gasPrice=self._gas_price,
            to=web3.toChecksumAddress(receiver_address),
            value=eth,
            # value=20000 * 10 ** 18,
            data='give {} {} eth'.format(receiver_address, eth).encode('utf8'),
            # data=b'',
        ),
            sender_private_key,
        )
        tx_hash = web3.eth.sendRawTransaction(signed_txn.rawTransaction)
        # 等待上链完成
        tx_hash_hex = eth_utils.encode_hex(tx_hash)
        (tf, receipt) = self.wait_for_tx(tx_hash_hex)
        log.debug(receipt)
        return tf, tx_hash_hex, receipt

    def send_row_transaction(self, row_transaction):
        """
        将签名的数据进行上链操作
        :param row_transaction:
        :return:
        """
        web3 = self._w3
        while True:
            try:
                tx_hash = web3.eth.sendRawTransaction(row_transaction)
            except ValueError as e:
                json_str = str(e)
                log.info(json_str)
                error_msg = json.loads(json.dumps(eval(json_str)))
                code = error_msg['code']
                if code == -32010:
                    time.sleep(1)
                    continue
            break
        tx_hash_hex = eth_utils.encode_hex(tx_hash)
        # (tf, receipt) = self.wait_for_tx(tx_hash_hex)
        # log.debug(receipt)
        receipt = self.get_receipt(tx_hash_hex)
        upload_success = utils.is_success_upload(receipt)
        return upload_success, tx_hash_hex, receipt

    def send_row_transaction_wait(self, row_transaction):
        """
        将签名的数据进行上链操作
        :param row_transaction:
        :return:
        """
        (upload_success, tx_hash_hex, receipt) = self.send_row_transaction(row_transaction)
        (upload_success, receipt) = self.wait_for_tx(tx_hash_hex)
        log.debug(receipt)
        return upload_success, tx_hash_hex, receipt

    def upload_function(self, contract_function, private_key):
        """
        将协约的方法进行签名和上链操作
        :param contract_function: 智能协约中对应的方法
        :param private_key: 签名用的private key
        :return:
        """
        web3 = self._w3
        nonce = self.get_private_key_nonce(private_key)
        # print('nonce:{}'.format(nonce))
        log.debug('nonce:{}'.format(nonce))

        tx_info = contract_function.buildTransaction(
            {'nonce': nonce,
             'gasPrice': int(self._gas_price) if isinstance(self._gas_price, str) else self._gas_price,
             'gas': int(self._gas) if isinstance(self._gas, str) else self._gas}
        )
        signed_txn = web3.eth.account.signTransaction(tx_info, private_key)
        tx_hash = web3.eth.sendRawTransaction(signed_txn.rawTransaction)
        tx_hash_hex = eth_utils.encode_hex(tx_hash)
        receipt = self.get_receipt(tx_hash_hex)
        # (tf, receipt) = self.wait_for_tx(tx_hash_hex)
        upload_success = utils.is_success_upload(receipt)
        return upload_success, tx_hash_hex, receipt

    def upload_function_wait(self, contract_function, private_key):
        """
        将协约的方法进行签名和上链操作 获得txid (会一直循环操作)
        如果pool里面已经有相同的txid，就会一直循环到下一个nonce值，在提交
        :param contract_function: 智能协约中对应的方法
        :param private_key: 签名用的private key
        :return:
        """
        web3 = self._w3
        while True:
            try:
                nonce = self.get_private_key_nonce(private_key)
                log.info("nonce:{}".format(nonce))
                tx_info = contract_function.buildTransaction(
                    {'nonce': nonce,
                     'gasPrice': int(self._gas_price) if isinstance(self._gas_price, str) else self._gas_price,
                     'gas': int(self._gas) if isinstance(self._gas, str) else self._gas }
                )
                signed_txn = web3.eth.account.signTransaction(tx_info, private_key)
                tx_hash = web3.eth.sendRawTransaction(signed_txn.rawTransaction)
            except ValueError as e:
                json_str = str(e)
                log.info(json_str)
                error_msg = json.loads(json.dumps(eval(json_str)))
                code = error_msg['code']
                if code == -32010:
                    time.sleep(1)
                    continue
            break
        tx_hash_hex = eth_utils.encode_hex(tx_hash)
        (tf, receipt) = self.wait_for_tx(tx_hash_hex)
        log.debug(receipt)
        return tf, tx_hash_hex, receipt

    def call_function_wait(self, function_name, *args, **kwargs):
        """
        等待上链成功
        :param function_name:   调用的协约方法
        :param args:            协约方法对应的参数，有顺序。
        :param kwargs:
        :return:
        """
        return self.call_function(function_name, True, *args)

    def call_function_nowait(self, function_name, *args, **kwargs):
        """
        不等待 直接 返回
        :param function_name:   调用的协约方法
        :param args:            协约方法对应的参数，有顺序。
        :param kwargs:
        :return:
        """
        return self.call_function(function_name, False, *args)

    def call_function(self, function_name, wait=True, *args, **kwargs):
        """
        调用智能协约的通用方法（会进行上链操作）
        :param function_name:   调用的协约方法
        :param wait:            是否等待receipt的返回
        :param args:            协约方法对应的参数，有顺序。
        :param kwargs:
        :return:
        """
        contract = self.get_contract()
        # 使用反射的方法调用web3
        function = getattr(contract.functions, function_name)(*args)
        if wait:
            tf, tx_hash, receipt = self.upload_function_wait(function, self._private_key)
        else:
            tf, tx_hash, receipt = self.upload_function(function, self._private_key)
        return tf, tx_hash, receipt

    def call_concise_function(self, function_name, *args, **kwargs):
        """
        调用智能协约的通用方法（不会上链，只是读取本地状态数据的协约）
        :param function_name: 调用的协约方法
        :param args: 协约方法对应的参数，有顺序。
        :param kwargs:
        :return:
        """
        contract = self.get_concise_contract()
        # 使用反射的方法调用web3
        value = getattr(contract, function_name)(*args)
        return value

    def getBalance(self, address, block_identifier=None):
        """
        获得地址的eth数量
        :param address:             需要查询的地址
        :param block_identifier:    第几个块上的数据，默认是最后一个块
        :return:
        """
        return self.w3.eth.getBalance(address, block_identifier)

    def __str__(self):
        return "connect provider : %s" % self._provider








