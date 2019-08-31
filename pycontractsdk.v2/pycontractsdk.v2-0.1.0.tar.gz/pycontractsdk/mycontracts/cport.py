#!/usr/bin/env python
# -*- coding: utf8 -*-
"""
Author:       yuyongpeng@hotmail.com
Github:       https://github.com/yuyongpeng/
Date:         2019-07-31 14:44:55
LastEditors:  
LastEditTime: 2019-07-31 14:44:55
Description:  
"""
from pycontractsdk.contracts import Contract

# TODO: 这个方法不在使用，统一使用通用的父类
class Cport(Contract):
    """
    Cport 相关的协约操作
    """
    def __init__(self, provider, timeout=60, *args, **kwargs):
        super(Cport, self).__init__(provider, timeout, *args, **kwargs)

    def example(self, operator_address):
        """ 例子1 """
        contract = self.get_contract()
        value = contract.functions.getOperator(operator_address).call()
        return value

    def example2(self, operator_address):
        """ 例子2 """
        concise_contract = self.get_concise_contract()
        value = concise_contract.getOperator(operator_address)
        return value

    def change_owner(self, identity_address, new_owner_address):
        """
        调用Uport协约中的 changeOwner 方法
        :param identity_address: 参数1
        :param new_owner_address: 参数2
        :return:
        """
        contract = self.get_contract()
        uport_function = contract.functions.changeOwner(identity_address, new_owner_address)
        tf, tx_hash = self.upload_function(uport_function, self._private_key)
        # timeout = self.waitForTx(tx_hash)
        return tf, tx_hash

    def get_reward_pool(self):
        """
        获得协约里面的当日奖池的剩余
        """
        concise_contract = self.get_concise_contract()
        pool = int(concise_contract.getRewardPool() / 10000000000)
        return pool

    def set_operator(self, operator_address, value=1):
        """
        设置operator账号
        :param operator_address:
        :param value:
        :return:
        """
        contract = self.get_contract()
        function = contract.functions.setOperator(operator_address, value)
        tf, tx_hash = self.upload_function(function, self._private_key)
        return tf, tx_hash

    def get_operator(self, operator_address):
        """
        确认一个账号是否是operator账号
        :param operator_address:
        :return: 1:是，0:否
        """
        contract = self.get_contract()
        value = contract.functions.getOperator(operator_address).call()
        # concise_contract = self.get_concise_contract()
        # value = concise_contract.getOperator(operator_address)
        return value

    def change_contract_owner(self, new_owner_address):
        """
        变更owner账号（只有协约的拥有者能够调用）
        :param new_owner_address:
        :return:
        """
        contract = self.get_contract()
        function = contract.functions.changeContractOwner(new_owner_address)
        tf, tx_hash = self.upload_function(function, self._private_key)
        return tf, tx_hash

    def get_contract_owner(self):
        """
        获得协约的拥有者address
        :return: address  （hex）
        """
        concise_contract = self.get_concise_contract()
        value = concise_contract.getContractOwner()
        return value

    def set_delegate(self, attribute, delegate_address, value):
        """
        调用智能协约的：setDelegate 方法
        :param attribute:
        :param delegate_address:
        :param value:
        :return:
        """
        if not isinstance(value, int):
            raise ValueError('function:set_delegate(), value:[{0}] Incorrect parameter type'.format(value))
        contract = self.get_contract()
        function = contract.functions.setDelegate(attribute, delegate_address, value)
        tf, tx_hash = self.upload_function(function, self._private_key)
        return tf, tx_hash

    def get_delegate(self):
        """
        调用智能协约的 getDelegate 方法
        :return:
        """
        concise_contract = self.get_concise_contract()
        value = concise_contract.getDelegate()
        return value

    def identity_owner(self, identity_address):
        """
        调用智能协约的 identityOwner 的方法
        :param identity_address:
        :return:
        """
        contract = self.get_contract()
        function = contract.functions.identityOwner(identity_address)
        tf, tx_hash = self.upload_function(function, self._private_key)
        return tf, tx_hash

    def change_did_owner(self, identity_address, new_owner_address):
        """
        调用智能协约的 changeDIDOwner 方法
        :param identity_address:
        :param new_owner_address:
        :return:
        """
        contract = self.get_contract()
        function = contract.functions.changeDIDOwner(identity_address, new_owner_address)
        tf, tx_hash = self.upload_function(function, self._private_key)
        return tf, tx_hash

    def check_signature(self, identity_address, sigV, sigR, sigS, hash):
        """
        调用智能协约的 checkSignature 方法
        :param identity_address:
        :param sigV:
        :param sigR:
        :param sigS:
        :param hash:
        :return:
        """
        contract = self.get_contract()
        function = contract.functions.setAttributeSigned(identity_address, sigV, sigR, sigS, hash)
        tf, tx_hash = self.upload_function(function, self._private_key)
        return tf, tx_hash

    def set_attribute(self, identity_address, owner_address, name, value):
        """
        调用智能协约的 setAttribute() 方法
        :param identity_address:
        :param owner_address:
        :param name: bytes
        :param value: bytes
        :return:
        """
        contract = self.get_contract()
        function = getattr(contract.functions, 'setAttribute')(identity_address, owner_address, name, value)
        # function = contract.functions.setAttribute(identity_address, owner_address, name, value)
        tf, tx_hash = self.upload_function(function, self._private_key)
        # contract = self.get_concise_contract()
        # contract.functions.setAttribute(identity_address, owner_address, name, value).transact()
        return tf, tx_hash

    def set_attribute_signed(self, identity_address, sig_v, sig_r, sig_s, name, value):
        """
        调用智能协约的 setAttributeSigned() 方法
        :param identity_address:
        :param sig_v:
        :param sig_r:
        :param sig_s:
        :param name:
        :param value:
        :return:
        """
        contract = self.get_contract()
        function = contract.functions.setAttributeSigned(identity_address, sig_v, sig_r, sig_s, name, value)
        tf, tx_hash = self.upload_function(function, self._private_key)
        # tf, tx_hash = self.upload_function(function, self._owner_private_key)
        return tf, tx_hash


    def confirm_attribute(self, identity, name, value):
        """
        调用智能协约的 confirmAttribute 方法
        :param identity:
        :param name:
        :param value:
        :return:
        """
        contract = self.get_contract()
        function = contract.functions.confirmAttribute(identity, name, value)
        # TODO: onlyDelegate 才能调用，需要添加一个delegate的账号权限到属性中
        tf, tx_hash = self.upload_function(function, self._private_key)
        # tf, tx_hash = self.upload_function(function, self._operator_private_key)
        return tf, tx_hash