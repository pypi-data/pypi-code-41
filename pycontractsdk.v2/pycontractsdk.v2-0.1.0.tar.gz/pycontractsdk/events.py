#! /usr/bin/env python
# -*- coding: utf8 -*-


import asyncio
from pycontractsdk.contracts import *
from pycontractsdk.mycontracts.cport import Cport
from pycontractsdk.contracts import Contract


async def eventlog_loop(event_filter, poll_interval, func):
    """

    :param event_filter:
    :param poll_interval:
    :param func:
    :return:
    """
    while True:
        for event in event_filter.get_new_entries():
            func(event)
        await asyncio.sleep(poll_interval)


def filter_event_async(provider, contract_address, abi, event_name, function, from_block=None, to_block='latest', timeout=2):
    """
    获得 event 的log
    :param provider: 具体连接的哪个server
    :param contract_address: 只能协约的address
    :param abi:
    :param event_name: 事件的名称，必须和abi中声明的一样
    :param function: 处理事件的函数
    :param from_block: 从哪个块开始
    :param to_block: 到哪个块结束
    :return: 获得的数据
    """
    cport = Cport(provider=provider, timeout=60, contract_address=contract_address, abi=abi)
    contract = cport.get_contract()
    event_filter = contract.events[event_name].createFilter(fromBlock=from_block, toBlock=to_block)
    loop = asyncio.get_event_loop()
    loop.run_until_complete(
        asyncio.gather(eventlog_loop(event_filter, timeout, function))
    )
    loop.close()


def filter_event(provider, contract_address, abi, event_name, function=None, from_block=None, to_block='latest'):
    """
    获得 event 的log
    :param provider: 具体连接的哪个server
    :param contract_address: 智能协约的address
    :param abi:
    :param event_name: 事件的名称，必须和abi中声明的一样
    :param function: 获得event之后执行的回调 (如果没有传递回调函数，就直接返回查询到的数据)
    :param from_block: 从哪个块开始
    :param to_block: 到哪个块结束
    :return: 获得的数据
    """
    cport = Cport(provider=provider, timeout=60, contract_address=contract_address, abi=abi)
    contract = cport.get_contract()
    # contract = cport.get_concise_contract()
    event_filter = contract.events[event_name].createFilter(fromBlock=from_block, toBlock=to_block)
    entries = event_filter.get_all_entries()
    print('fromBlock={}, toBlock={}'.format(from_block, to_block))
    if function is None:
        return entries
        # raise ValueError('必须设置handle function')
    function(entries)


def get_event_filter(provider, contract_address, abi, event_name, from_block=None, to_block='latest'):
    """
    获得 event_filter 对象
    :param provider: 具体连接的哪个server
    :param contract_address: 只能协约的address
    :param abi:
    :param event_name: 事件的名称，必须和abi中声明的一样
    :param from_block: 从哪个块开始
    :param to_block: 到哪个块结束
    :return: 获得的数据
    """
    cport = Cport(provider=provider, timeout=60, contract_address=contract_address, abi=abi)
    contract = cport.get_contract()
    event_filter = contract.events[event_name].createFilter(fromBlock=from_block, toBlock=to_block)
    return event_filter


class Event(Contract):
    def __init__(self, provider, timeout=60, *args, **kwargs):
        super(Event, self).__init__(provider, timeout, *args, **kwargs)

    def get_event(self, event_name, from_block, to_block):
        """
        获得 event 数据
        :param event_name:
        :param from_block:
        :param to_block:
        :return:
        """
        contract = self.get_contract()
        event_filter = contract.events[event_name].createFilter(fromBlock=from_block, toBlock=to_block)
        entries = event_filter.get_all_entries()
        return entries














