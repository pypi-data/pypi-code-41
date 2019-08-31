#!/usr/bin/env python
# -*- coding: utf8 -*-
"""
Author:       yuyongpeng@hotmail.com
Github:       https://github.com/yuyongpeng/
Date:         2019-07-31 14:45:25
LastEditors:  
LastEditTime: 2019-07-31 14:45:25
Description:  
"""
from pycontractsdk.contracts import Contract, keys
from web3.contract import ConciseContract


class StarCoin(Contract):
    """
    星钻 相关的协约操作
    """
    server_operator_private = ''        # 云端 python 上链的的账号
    contract_creater_private = ''       # 协约创建者的账号

    def __init__(self, provider, timeout=60, *args, **kwargs):
        super(StarCoin, self).__init__(provider, timeout, *args, **kwargs)
        self.server_operator_private = kwargs.pop('server_operator_private')
        self.contract_creater_private = kwargs.pop('contract_creater_private')

    def get_all_status(self):
        """ 获得 以太坊 和 协约 的当前状态 """
        print("_____________eth of contract {}_______________________________".format(self._contract_address))
        print("contract has {} eth".format(
            self.w3.eth.getBalance(self.w3.toChecksumAddress(self._contract_address))))
        # print out the parameters in imo one by one.
        # print("_____________print running state variables of contract {}______________".format(contract_address))
        # print("there are __ {} __ fans support star".format(contract.getDepositAmount()))
        print("contract nextDepositIndex is {}".format(self.call_concise_function('nextDepositIndex')))
        print("contract dailyLuckyNumber is {}".format(self.call_concise_function('dailyLuckyNumber')))

        print("contract current mask is {}".format(self.call_concise_function('getCurrentMask')))
        # print("account deposit amount is {}".format(contract.getDepositAmount(owner)))
        # print("account deposit index is {}".format(contract.getDepositIndex(owner)))

        print("------------print coin amount in seven pools--------------")
        # print("contract getOperatorPool is {}".format(self.call_concise_function('getOperatorPool') / 10 ** 10))
        # print("contract getRewardPool is {}".format(self.call_concise_function('getRewardPool') / 10 ** 10))
        # print("contract getAirDropPool is {}".format(self.call_concise_function('getAirDropPool') / 10 ** 10))
        # print("contract getCentralBank is {}".format(self.call_concise_function('getCentralBank') / 10 ** 10))
        # print("contract getDailyRewardPool is {}".format(self.call_concise_function('getDailyRewardPool') / 10 ** 10))

        print("contract getOperatorPool is \t {}".format(self.call_concise_function('getOperatorPool')))
        print("contract getRewardPool is \t {}".format(self.call_concise_function('getRewardPool')))
        print("contract getAirDropPool is \t {}".format(self.call_concise_function('getAirDropPool')))
        print("contract getCentralBank is \t {}".format(self.call_concise_function('getCentralBank')))
        print("contract getDailyRewardPool is \t {}".format(self.call_concise_function('getDailyRewardPool')))


        # check if one account is activated.
        print("------- 云端 python 程序账号的权限 ------------------------")
        server_operator_address = keys.privatekey_to_address(self.server_operator_private)
        print("account activate is \t {}".format(self.call_concise_function('getActivate', server_operator_address)))
        print("account state in account operator is \t {}".format(self.getAccountOperator(server_operator_address)))
        print("account state in operator pool is \t {}".format(
            self.call_concise_function('getStateOperatorPool', server_operator_address)))
        print("account state in reward pool is \t {}".format(
            self.call_concise_function('getStateRewardPool', server_operator_address)))
        print("account state in air drop pool is \t {}".format(
            self.call_concise_function('getStateAirDropPool', server_operator_address)))
        print("account state in central bank is \t {}".format(
            self.call_concise_function('getStateCentralBank', server_operator_address)))

        # check if one account is activated.
        print("------- 协约创建者 账号的权限 ------------------------")
        contract_creater_address = keys.privatekey_to_address(self.contract_creater_private)
        print("account activate is \t {}".format(self.call_concise_function('getActivate', contract_creater_address)))
        print("account state in account operator is \t {}".format(self.getAccountOperator(contract_creater_address)))
        print("account state in operator pool is \t {}".format(
            self.call_concise_function('getStateOperatorPool', contract_creater_address)))
        print("account state in reward pool is \t {}".format(
            self.call_concise_function('getStateRewardPool', contract_creater_address)))
        print("account state in air drop pool is \t {}".format(
            self.call_concise_function('getStateAirDropPool', contract_creater_address)))
        print("account state in central bank is \t {}".format(
            self.call_concise_function('getStateCentralBank', contract_creater_address)))

        print("------------------------------")
        print("reward scale is {}".format(self.call_concise_function('getRewardScale')))
        print("设备激活的时候给粉丝的eth数量: {}".format(self.call_concise_function('getInitEthForFans')))
        print("contract owner is {}".format(self.call_concise_function('owner')))
        print("当前预估每天产生的区块数量: {}".format(self.call_concise_function('getDailyBlockNumber')))
        print("总的押注的人数: {}".format(self.call_concise_function('getDepositAccount')))
        print("得到最近一次更新掩码的区块号: {}".format(self.call_concise_function('getLastUpdateMaskBlockNum')))
        print("最新的区块号: {}".format(self.last_block_number()))

    ####################################################################################################################
    ############################# 查询账号的权限 #########################################################################
    ####################################################################################################################
    def getStateOperatorPool(self, _account):
        """
        查询账号是否拥有 operator pool 的权限
        :param _account:    需要查询的账号
        :return:            0 未激活 1 激活 2 禁用
        """
        return self.call_concise_function('getStateOperatorPool', _account)

    def getStateRewardPool(self, _account):
        """
        查询账号是否拥有 reward pool 的权限
        :param _account:    需要查询的账号
        :return:            0 未激活 1 激活 2 禁用
        """
        return self.call_concise_function('getStateRewardPool', _account)

    def getStateAirDropPool(self, _account):
        """
        查询账号是否拥有 air drop pool 的权限
        :param _account:    需要查询的账号
        :return:            0 未激活 1 激活 2 禁用
        """
        return self.call_concise_function('getStateAirDropPool', _account)

    def getStateCentralBank(self, _account):
        """
        查询账号是否拥有 central bank 的权限
        :param _account:    需要查询的账号
        :return:            0 未激活 1 激活 2 禁用
        """
        return self.call_concise_function('getStateCentralBank', _account)

    def getAccountOperator(self, _account):
        """
        查询账号是否拥有 账号管理 的权限
        :param _account:    需要查询的账号
        :return:            0 未激活 1 激活 2 禁用
        """
        return self.call_concise_function('getAccountOperator', _account)

    ####################################################################################################################
    ############################# 得到每个币池的数 #######################################################################
    ####################################################################################################################
    def getOperatorPool(self):
        """
        查询 operator pool 的 钱数
        :return:   token 数量： 20 * 10 ** 10
        """
        return self.call_concise_function('getOperatorPool')

    def getRewardPool(self):
        """
        查询 reward pool 的 钱数
        :return:   token 数量： 20 * 10 ** 10
        """
        return self.call_concise_function('getRewardPool')

    def getAirDropPool(self):
        """
        查询 airDrop pool 的 钱数
        :return:   token 数量： 20 * 10 ** 10
        """
        return self.call_concise_function('getAirDropPool')

    def getCentralBank(self):
        """
        查询 centralBank pool 的 钱数
        :return:   token 数量： 20 * 10 ** 10
        """
        return self.call_concise_function('getCentralBank')

    def getDailyRewardPool(self):
        """
        查询 daily reward pool 的 钱数
        :return:   token 数量： 20 * 10 ** 10
        """
        return self.call_concise_function('getDailyRewardPool')

    ####################################################################################################################
    ############################# 获得一些设置的信息 ######################################################################
    ####################################################################################################################
    def getInitStarCoin(self):
        """
        激活的时候给粉丝的明星币数量
        :return:
        """
        return self.call_concise_function('getInitStarCoin')

    def getInitEthForFans(self):
        """
        得到激活的时候给粉丝的eth数量
        :return:
        """
        return self.call_concise_function('getInitEthForFans')

    def getDailyBlockNumber(self):
        """
        当前预估每天产生的区块数量
        :return:
        """
        return self.call_concise_function('getDailyBlockNumber')

    def getDepositAccount(self):
        """
        得到现在投注的总人数
        :return:
        """
        return self.call_concise_function('getDepositAccount')

    def getLastUpdateMaskBlockNum(self):
        """
        得到最近一次更新掩码的区块号
        :return:
        """
        return self.call_concise_function('getLastUpdateMaskBlockNum')

    def getDepositAmount(self, eth_address):
        """
        得到账号投注金额
        :param eth_address:     矿机的 address
        :return:
        """
        return self.call_concise_function('getDepositAmount', eth_address)

    def getDepositIndex(self, eth_address):
        """
        得到账号序号
        :param eth_address:     矿机的 address
        :return:
        """
        return self.call_concise_function('getDepositIndex', eth_address)

    def getCurrentMask(self):
        """
        得到现在掩码
        :return:
        """
        return self.call_concise_function('getCurrentMask')

    def getDailyLuckyNumber(self):
        """
        得到每天获得奖励的人数
        :return:
        """
        return self.call_concise_function('getDailyLuckyNumber')

    def getActivate(self, _account):
        """
        查询账户激活状态
        :param _account:    需要查询状态的账户
        :return:            0 未激活 1 激活 2 禁用 3 转移
        """
        return self.call_concise_function('getActivate', _account)

    def balanceOf(self, eth_address):
        """
        查询 矿机 的 token 数量 ，
        这个方法是在 https://github.com/OpenZeppelin/openzeppelin-contracts/blob/v1.12.0/contracts/token/ERC20/BasicToken.sol
        :param eth_address:    矿机的address
        :return:
        """
        return self.call_concise_function('balanceOf', eth_address)


    ####################################################################################################################
    ############################# 设置账号的权限 #########################################################################
    ####################################################################################################################
    def setOpsForAirDropPool(self, _account, _status):
        """
        只有创建协约的账号才有权限调用
        设置 "空投管理" 账号, 有了这个权限就能 激活账号
        :param _account:    空投管理账号 address
        :param _status:     0 未激活 1 激活 2 禁用
        :return:
        """
        print()
        print("---------------------------------------")
        print(" 设置 '空投' 管理账号 ")
        print("Before : 空投账号 {} status {}".format(_account, self.getStateAirDropPool(_account)))
        self.call_function_wait('setOpsForAirDropPool', _account, _status)
        print("After : 空投账号 {} status {}".format(_account, self.getStateAirDropPool(_account)))
        print("---------------------------------------")

    def setOpsForAirDropPool(self, _account, _status):
        """
        只有创建协约的账号才有权限调用
        设置 "空投管理" 账号, 有了这个权限就能 激活账号
        :param _account:    空投管理账号 address
        :param _status:     0 未激活 1 激活 2 禁用
        :return:
        """
        print()
        print("---------------------------------------")
        print(" 设置 '空投' 管理账号 ")
        print("Before : 空投账号 {} status {}".format(_account, self.getStateAirDropPool(_account)))
        self.call_function_wait('setOpsForAirDropPool', _account, _status)
        print("After : 空投账号 {} status {}".format(_account, self.getStateAirDropPool(_account)))
        print("---------------------------------------")

    def setOpsForRewardPool(self, _account, _status):
        """
        只有创建协约的账号才有权限调用
        设置 "矿池管理账号" , 有了这个权限就能 从矿池打钱到每日挖矿池
        :param _account:    空投管理账号 address
        :param _status:     0 未激活 1 激活 2 禁用
        :return:
        """
        print()
        print("---------------------------------------")
        print(" 设置 矿池 管理账号 ")
        print("Before : 空投账号 {} status {}".format(_account, self.getStateRewardPool(_account)))
        self.call_function_wait('setOpsForRewardPool', _account, _status)
        print("After : 空投账号 {} status {}".format(_account, self.getStateRewardPool(_account)))
        print("---------------------------------------")

    def setOpsForCentralBank(self, _account, _status):
        """
        只有创建协约的账号才有权限调用
        设置 "中央银行管理账号" , 有了这个权限就能 从中央银行打钱到个人投注，从中央银行打钱到每日奖池，从中央银行转钱给个人
        :param _account:    运营账号 address
        :param _status:     0 未激活 1 激活 2 禁用
        :return:
        """
        print()
        print("---------------------------------------")
        print(" 设置 '中央银行' 管理账号 ")
        print("Before : 中央银行管理账号 {} status {}".format(_account, self.getStateCentralBank(_account)))
        self.call_function_wait('setOpsForCentralBank', _account, _status)
        print("After : 中央银行管理账号 {} status {}".format(_account, self.getStateCentralBank(_account)))
        print("---------------------------------------")

    def setOpsForOperatorPool(self, _account, _status):
        """
        只有创建协约的账号才有权限调用
        设置 "运营 operator" 账号, 有了这个权限就能 从运营账号转钱
        :param _account:    运营账号 address
        :param _status:     0 未激活 1 激活 2 禁用
        :return:
        """
        print()
        print("---------------------------------------")
        print(" 设置 '运营' 管理账号 ")
        print("Before : 运营账号 {} status {}".format(_account, self.getStateOperatorPool(_account)))
        # self.w3.eth.functions.setOpsForOperatorPool( _account, _status)
        self.call_function_wait('setOpsForOperatorPool', _account, _status)
        print("After : 运营账号 {} status {}".format(_account, self.getStateOperatorPool(_account)))
        print("---------------------------------------")

    def setAccountOperator(self, _account, _status):
        """
        只有创建协约的账号才有权限调用
        设置 账号管理 账号, 有了这个权限就能 "设置奖励系数" "设置账户的激活状态"
        :param _account:    管理员账号 address
        :param _status:     0 未激活 1 激活 2 禁用
        :return:
        """
        # 权限判断 只有协约所有者才能调用

        print()
        print("---------------------------------------")
        print(" 设置 '账号管理' 账号 ")
        print("Before : {} status {}".format(_account, self.getAccountOperator(_account)))
        self.call_function_wait('setAccountOperator', _account, _status)
        print("After : {} status {}".format(_account, self.getAccountOperator(_account)))
        print("---------------------------------------")

    ####################################################################################################################
    ############################# 一些参数的设置 #########################################################################
    ####################################################################################################################
    def setRewardScale(self, _rewardScale):
        """
        设置奖励系数, 只有 设置了setAccountOperator的用才能调用
        :param _rewardScale:        系数值
        :param accountOperator:     默认使用 server 端 上链的operator账号
        :return:
        """
        print()
        print("---------------------------------------")
        # 发起交易的用户必须有 onlyAccountOperator 权限才能调用
        private_key_address = keys.privatekey_to_address(self._private_key)
        role = self.getAccountOperator(private_key_address)
        if role != 1:
            print("发起交易者：{}  没有权限调用 setRewardScal() 方法".format(self._private_key))
            self.get_account_role(private_key_address)
            return None

        print("Before : 奖励系数值为： {}".format(self.call_concise_function('getRewardScale')))
        self.call_function_wait('setRewardScale', _rewardScale)
        print("After : 奖励系数值为： {}".format(self.call_concise_function('getRewardScale')))
        print("---------------------------------------")

    def setActivate(self, _account, _status):
        """
        修改用户的激活状态， 只有 设置了setAccountOperator的用才能调用
        :param _account:            需要激活的矿机 address
        :param _status:             0 未激活 1 激活 2 禁用 3 转移
        :return:
        """
        print()
        print("---------------------------------------")
        # 发起交易的用户必须有 onlyAccountOperator 权限才能调用
        private_key_address = keys.privatekey_to_address(self._private_key)
        role = self.getAccountOperator(private_key_address)
        if role != 1:
            print("发起交易者：{}  没有权限调用 setRewardScal() 方法".format(self._private_key))
            self.get_account_role(private_key_address)
            return None

        print("Before : 用户的激活状态为： {}".format(self.getActivate(_account)))
        self.call_function_wait('setActivate', _account, _status)
        print("After : 用户的激活状态为： {}".format(self.getActivate(_account)))
        print("---------------------------------------")

    def setInitStarCoin(self, _amount):
        """
        修改激活时给矿机的明星币数量， 只有 设置了setAccountOperator的用才能调用
        :param _amount:             明星币数量 （默认值：1500 * 10 ** 10;）
        :return:
        """
        print()
        print("---------------------------------------")
        # 发起交易的用户必须有 onlyAccountOperator 权限才能调用
        private_key_address = keys.privatekey_to_address(self._private_key)
        role = self.getAccountOperator(private_key_address)
        if role != 1:
            print("发起交易者：{}  没有权限调用 setRewardScal() 方法".format(self._private_key))
            self.get_account_role(private_key_address)
            return None
        print("Before : 激活时给矿机的明星币数量为： {}".format(self.call_concise_function('getInitStarCoin')))
        self.call_function_wait('setInitStarCoin', _amount)
        print("After : 激活时给矿机的明星币数量为： {}".format(self.call_concise_function('getInitStarCoin')))
        print("---------------------------------------")

    def setDailyLuckyNumber(self, _dailyLuckyNumber):
        """
        修改每天得到奖励人数
        :param _dailyLuckyNumber:   每天获奖人数
        :return:
        """
        print()
        print("---------------------------------------")
        print("Before : 每天得到奖励人数为： {}".format(self.call_concise_function('getDailyLuckyNumber')))
        self.call_function_wait('setDailyLuckyNumber', _dailyLuckyNumber)
        print("After : 每天得到奖励人数为： {}".format(self.call_concise_function('getDailyLuckyNumber')))
        print("---------------------------------------")

    def setInitEthForFans(self, _initEthForFans):
        """
        设置激活的时候给粉丝的eth数量
        :param _initEthForFans:   给矿机的 eth 数量
        :return:
        """
        print()
        print("---------------------------------------")
        print("Before : 激活的时候给粉丝的eth数量为： {}".format(self.call_concise_function('getInitEthForFans')))
        self.call_function_wait('setInitEthForFans', _initEthForFans)
        print("After : 激活的时候给粉丝的eth数量为： {}".format(self.call_concise_function('getInitEthForFans')))
        print("---------------------------------------")

    def setDailyBlockNumber(self, _initEthForFans):
        """
        设置每天产生的区块数量
        :param _initEthForFans:   每天产生的区块数量
        :return:
        """
        print()
        print("---------------------------------------")
        print("Before : 每天产生的区块数量： {}".format(self.call_concise_function('getDailyBlockNumber')))
        self.call_function_wait('setDailyBlockNumber', _initEthForFans)
        print("After : 每天产生的区块数量： {}".format(self.call_concise_function('getDailyBlockNumber')))
        print("---------------------------------------")

    def accountActivate(self, _account):
        """
        激活一个账号   （onlyOpsForAirDropPool）
        :param _account:   矿机的address
        :return:
        """
        print()
        print("---------------------------------------")
        # 发起交易的用户必须有 onlyOpsForAirDropPool 权限才能调用
        private_key_address = keys.privatekey_to_address(self._private_key)
        role = self.getStateAirDropPool(private_key_address)
        if role != 1:
            print("发起交易者：{}  没有权限调用 accountActivate() 方法".format(self._private_key))
            self.get_account_role(private_key_address)
            return None
        print("Before : 账户的激活状态为: {}".format(self.getActivate(_account)))
        self.call_function_wait('accountActivate', _account)
        print("After : 账户的激活状态为： {}".format(self.getActivate(_account)))
        print("---------------------------------------")


    def centralBankToDeposit(self, _account, _tokenAmount):
        """
        从中央银行打钱到个人投注池  onlyOpsForCentralBank
        :param _account:        接收者的address
        :param _tokenAmount:    押注的钱数 10 * 10 ** 10
        :return:
        """
        print()
        print("---------------------------------------")
        # 发起交易的用户必须有 onlyOpsForCentralBank 权限才能调用
        private_key_address = keys.privatekey_to_address(self._private_key)
        role = self.getStateCentralBank(private_key_address)
        if role != 1:
            print("发起交易者：{}  没有权限调用 centralBankToDeposit() 方法".format(self._private_key))
            self.get_account_role(private_key_address)
            return None

        _account_checksum = keys.to_check_sum_address(_account)
        print("Before : 中央银行的钱数为: {}".format(self.getCentralBank()))
        print("Before : 个人投注池的钱数: {}".format(self.getDepositAmount(_account_checksum)))
        self.call_function_wait('centralBankToDeposit', _account_checksum, _tokenAmount)
        print("After : 中央银行的钱数为: {}".format(self.getCentralBank()))
        print("After : 个人投注池的钱数: {}".format(self.getDepositAmount(_account_checksum)))
        print("---------------------------------------")

    def centralBankToDailyRewardPoll(self, _tokenAmount):
        """
        从中央银行打钱到 当日奖池  onlyOpsForCentralBank
        :param _tokenAmount:    钱数 10 * 10 ** 10
        :return:
        """
        print()
        print("---------------------------------------")
        # 发起交易的用户必须有 onlyOpsForCentralBank 权限才能调用
        private_key_address = keys.privatekey_to_address(self._private_key)
        role = self.getStateCentralBank(private_key_address)
        if role != 1:
            print("发起交易者：{}  没有权限调用 centralBankToDailyRewardPoll() 方法".format(self._private_key))
            self.get_account_role(private_key_address)
            return None
        print("Before : 中央银行的钱数为: {}".format(self.getCentralBank()))
        print("Before : 当日奖池的钱数: {}".format(self.getDailyRewardPool()))
        self.call_function_wait('centralBankToDailyRewardPoll', _tokenAmount)
        print("After : 中央银行的钱数为: {}".format(self.getCentralBank()))
        print("After : 当日奖池的钱数: {}".format(self.getDailyRewardPool()))
        print("---------------------------------------")

    def allocateDailyRewardPool(self, _tokenAmount):
        """
        从挖矿总池子 ->  每天挖矿池
        :param _tokenAmount:   token 数量  1 * 10 ** 10
        :return:
        """
        print()
        print("---------------------------------------")
        # 发起交易的用户必须有 onlyOpsForRewardPool 权限才能调用
        private_key_address = keys.privatekey_to_address(self._private_key)
        role = self.getStateRewardPool(private_key_address)
        if role != 1:
            print("发起交易者：{}  没有权限调用 centralBankToDailyRewardPoll() 方法".format(self._private_key))
            self.get_account_role(private_key_address)
            return None
        print("Before : 挖矿总池的钱数为: {}".format(self.getRewardPool()))
        print("Before : 当日奖池的钱数: {}".format(self.getDailyRewardPool()))
        self.call_function_wait('allocateDailyRewardPool', _tokenAmount)
        print("After : 挖矿总池的钱数为: {}".format(self.getRewardPool()))
        print("After : 当日奖池的钱数: {}".format(self.getDailyRewardPool()))
        print("---------------------------------------")

    def transferFromRewardPool(self, _account, _tokenAmount):
        """
        从 rewardPool池 -> 个人账号   需要 onlyOpsForRewardPool 权限
        :param _account:        接收者的 address
        :param _tokenAmount:    钱数  1 * 10 * 10
        :return:
        """
        print()
        print("---------------------------------------")
        # 发起交易的用户必须有 onlyOpsForRewardPool 权限才能调用
        private_key_address = keys.privatekey_to_address(self._private_key)
        role = self.getStateRewardPool(private_key_address)
        if role != 1:
            print("发起交易者：{}  没有权限调用 transferFromOperatorPool() 方法".format(self._private_key))
            self.get_account_role(private_key_address)
            return None
        _account_checksum = keys.to_check_sum_address(_account)
        print("Before : rewardPool池的钱数为: {}".format(self.getRewardPool()))
        print("Before : 个人账号的钱数: {}".format(self.balanceOf(_account_checksum)))
        self.call_function_wait('transferFromRewardPool', _account, _tokenAmount)
        print("After : rewardPool池的钱数为: {}".format(self.getRewardPool()))
        print("After : 个人账号的钱数: {}".format(self.balanceOf(_account_checksum)))


    def transferFromOperatorPool(self, _account, _tokenAmount):
        """
        从 运营池 -> 个人账号   需要 onlyOpsForOperatorPool 权限
        :param _account:        接收者的 address
        :param _tokenAmount:    钱数  1 * 10 * 10
        :return:
        """
        print()
        print("---------------------------------------")
        # 发起交易的用户必须有 onlyOpsForOperatorPool 权限才能调用
        private_key_address = keys.privatekey_to_address(self._private_key)
        role = self.getStateOperatorPool(private_key_address)
        if role != 1:
            print("发起交易者：{}  没有权限调用 transferFromOperatorPool() 方法".format(self._private_key))
            self.get_account_role(private_key_address)
            return None
        _account_checksum = keys.to_check_sum_address(_account)
        print("Before : 运营池的钱数为: {}".format(self.getOperatorPool()))
        print("Before : 个人账号的钱数: {}".format(self.balanceOf(_account_checksum)))
        self.call_function_wait('transferFromOperatorPool', _account, _tokenAmount)
        print("After : 运营池的钱数为: {}".format(self.getOperatorPool()))
        print("After : 个人账号的钱数: {}".format(self.balanceOf(_account_checksum)))

    def transferFromCentralBank(self, _account, _tokenAmount):
        """
        中央银行 -> 个人账号   需要 onlyOpsForCentralBank 权限
        :param _account:        接收者的 address
        :param _tokenAmount:    钱数  1 * 10 * 10
        :return:
        """
        print()
        print("---------------------------------------")
        # 发起交易的用户必须有 onlyOpsForCentralBank 权限才能调用
        private_key_address = keys.privatekey_to_address(self._private_key)
        role = self.getStateCentralBank(private_key_address)
        if role != 1:
            print("发起交易者：{}  没有权限调用 transferFromCentralBank() 方法".format(self._private_key))
            self.get_account_role(private_key_address)
            return None
        _account_checksum = keys.to_check_sum_address(_account)
        print("Before : 中央银行的钱数为: {}".format(self.getCentralBank()))
        print("Before : 个人账号的钱数: {}".format(self.balanceOf(_account_checksum)))
        self.call_function_wait('transferFromCentralBank', _account, _tokenAmount)
        print("After : 中央银行的钱数为: {}".format(self.getCentralBank()))
        print("After : 个人账号的钱数: {}".format(self.balanceOf(_account_checksum)))


    def depositToOperatorPool(self, _amount):
        """
        个人账户 -> 运营池
        :param _amount:  token数量  1 * 10 ** 10
        :return:
        """
        print()
        print("---------------------------------------")
        # 获得发起交易者的账号
        private_key_address = keys.privatekey_to_address(self._private_key)
        print("Before : 个人账号的钱数: {}".format(self.balanceOf(private_key_address)))
        print("Before : 运营池的钱数为: {}".format(self.getOperatorPool()))
        self.call_function_wait('depositToOperatorPool', _amount)
        print("After : 个人账号的钱数: {}".format(self.balanceOf(private_key_address)))
        print("After : 运营池的钱数为: {}".format(self.getOperatorPool()))

    def depositToRewardPool(self, _amount):
        """
        个人账户  ->  总奖池
        :param _amount:
        :return:
        """
        print()
        print("---------------------------------------")
        # 获得发起交易者的账号
        private_key_address = keys.privatekey_to_address(self._private_key)
        print("Before : 个人账号的钱数: {}".format(self.balanceOf(private_key_address)))
        print("Before : 总奖池的钱数为: {}".format(self.getRewardPool()))
        self.call_function_wait('depositToRewardPool', _amount)
        print("After : 个人账号的钱数: {}".format(self.balanceOf(private_key_address)))
        print("After : 总奖池的钱数为: {}".format(self.getRewardPool()))


    def depositToAirDropPool(self, _amount):
        """
        个人账户  ->  空投池
        :param _amount:
        :return:
        """
        print()
        print("---------------------------------------")
        # 获得发起交易者的账号
        private_key_address = keys.privatekey_to_address(self._private_key)
        print("Before : 个人账号的钱数: {}".format(self.balanceOf(private_key_address)))
        print("Before : 空投池的钱数为: {}".format(self.getAirDropPool()))
        self.call_function_wait('depositToAirDropPool', _amount)
        print("After : 个人账号的钱数: {}".format(self.balanceOf(private_key_address)))
        print("After : 空投池的钱数为: {}".format(self.getAirDropPool()))


    def depositToCentralBank(self, _amount):
        """
        个人账户  ->  中央银行
        :param _amount:
        :return:
        """
        print()
        print("---------------------------------------")
        # 获得发起交易者的账号
        private_key_address = keys.privatekey_to_address(self._private_key)
        print("Before : 个人账号的钱数: {}".format(self.balanceOf(private_key_address)))
        print("Before : 中央银行的钱数为: {}".format(self.getCentralBank()))
        self.call_function_wait('depositToCentralBank', _amount)
        print("After : 个人账号的钱数: {}".format(self.balanceOf(private_key_address)))
        print("After : 中央银行的钱数为: {}".format(self.getCentralBank()))


    def heartbeat(self, win_number):
        """
        矿机挖矿  必须是激活账户才能调用
        :param win_number:
        :return:
        """
        print()
        print("---------------------------------------")
        # 发起交易的用户必须是 激活的账户 才能调用
        private_key_address = keys.privatekey_to_address(self._private_key)
        role = self.getActivate(private_key_address)
        if role != 1:
            print("发起交易者：{}  没有权限调用 heartbeat() 方法".format(self._private_key))
            self.get_account_role(private_key_address)
            return None
        self.call_function_wait('heartbeat', win_number)
        print("---------------------------------------")


    ####################################################################################################################
    ############################# 获得用户的权限信息 ######################################################################
    ####################################################################################################################

    def get_account_role(self, address):
        """
        获得账号的权限信息
        :param address:     需要查询的账号( public_key or private_key)
        :return:
        """
        # if keys.is_privatekey():
        #     checksum_address = keys.privatekey_to_address(address)
        # else:
        #     checksum_address = keys.to_check_sum_address(address)
        checksum_address = keys.to_check_sum_address(address)
        airDropPool_role = self.getStateAirDropPool(checksum_address)
        centralBankPool_role = self.getStateCentralBank(checksum_address)
        operatorPool_role = self.getStateOperatorPool(checksum_address)
        rewardPool_role = self.getStateRewardPool(checksum_address)
        accountOperator_role = self.getAccountOperator(checksum_address)
        print("账号：{}  拥有的权限：".format(checksum_address))
        print("airDropPool_role: {}".format(airDropPool_role))
        print("centralBankPool_role: {}".format(centralBankPool_role))
        print("operatorPool_role: {}".format(operatorPool_role))
        print("rewardPool_role: {}".format(rewardPool_role))
        print("accountOperator_role: {}".format(accountOperator_role))










































