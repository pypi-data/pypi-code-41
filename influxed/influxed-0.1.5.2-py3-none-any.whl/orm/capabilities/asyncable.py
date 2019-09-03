#!/usr/bin/env python3
# -*- coding:utf-8 -*-
"""
 File: asyncable.py
 File Created: Sunday, 24th February 2019 8:23:27 pm
 Author: ESR - Romeren (emilromer@hotmail.com)
 -----
 Copyright 2019 OpenSourced, OpenSourced
 -----
 Last Modified:
 Date	By	Comments
 -----
"""
import asyncio


class HandlePosibleAsync(object):
    """
        Class wrapper for asyncio.future objects. 
        Created to make chaining of processes easy and painless
    """
    def __init__(self, posible_future):
        self.posible_awaitable = posible_future

    def chain_function(self, function):
        if(isinstance(self.posible_awaitable, Asyncable)):
            self.posible_awaitable = Asyncable(self.posible_awaitable.return_(), function)
        else:
            self.posible_awaitable = Asyncable(
                posible_future=self.posible_awaitable,
                chaning_function=function
            )

    def return_(self):
        return self.posible_awaitable.return_()


class Asyncable(object):
    """
        Class wrapper for asyncio.future objects. 
        Created to make chaining of processes easy and painless
    """
    def __init__(self, posible_future, chaning_function):
        self.posible_future = posible_future
        self.chaning_function = chaning_function
    
    async def awaitable(self):
        res = await self.posible_future
        res = await self.handle_chain(res)
        return res

    async def list_awaitable(self):
        res = await asyncio.gather(*self.posible_future)
        res = await self.handle_chain(res)
        return res

    async def handle_chain(self, chain_res):
        res = self.chaning_function(chain_res)
        if(asyncio.iscoroutine(res)):
            res = await res
        elif(isinstance(res, (list, tuple) ) and all([asyncio.iscoroutine(x) for x in res])):
            res = await asyncio.gather(*res)
        return res

    def return_(self):
        if(asyncio.iscoroutine(self.posible_future)):
            return self.awaitable()
        if(isinstance(self.posible_future, (list, tuple) ) and len(self.posible_future) > 0 and all([asyncio.iscoroutine(x) for x in self.posible_future])):
            return self.list_awaitable()
        return self.chaning_function(self.posible_future)
        


