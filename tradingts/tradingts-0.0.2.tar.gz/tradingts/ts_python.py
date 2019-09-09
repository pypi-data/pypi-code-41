# -*- coding: utf-8 -*-
"""
Created on Wed Aug 28 14:34:05 2019

@author: TS
"""
import uuid
import queue
import time
import threading
import asyncio
import websockets
import sys                                                                  
import signal
import mmap
import contextlib
import time



#构建发单字符串
def buildSendInfo():
    Account = "410038111484"
    Id = str(uuid.uuid1())
    symbol = "600000.SH"
    Quantity = str(200)
    OrderAction = "Buy"
    Flag = "Limit"
    LimitPrice = str(10.09)
    LimitOrder = Flag+"|"+Account+"|"+symbol+"|"+Quantity+"|"+OrderAction+"|"+LimitPrice+"|"+Id
    _Account = "410038111484"
    _Id = str(uuid.uuid1())
    _Symbol = "000001.SZ"
    _Quantity = str(100)
    _OrderAction = "Sell"
    _Flag = "Market"
    MarketOrder = _Flag+"|"+_Account+"|"+_Symbol+"|"+_Quantity+"|"+_OrderAction+"|"+_Id
    content = LimitOrder #+ "&" + MarketOrder
    return content


#构建撤单字符串
def buildCancelInfo():
    Account = "410038111484"
    Id = str(uuid.uuid1())
    Flag = 'Cancel'
    CancelID = '你需要撤单的编号，在委托申报时由你唯一指定'
    content = Flag + "|" + Account + "|" + CancelID + "|" + Id
    return  content


#构建查询字符串
def buildQueryInfo():
    #
    Id1 = str(uuid.uuid1())
    AcctID = "410038111484"
    Flag1 = "Account"
    QueryAccount = Flag1 + "|" + AcctID + "|" + Id1 # 如果AccountID为空，返回所有
    #
    Id2 = str(uuid.uuid1())
    Acct2 = "410038111484"
    Symb2 = "000001.SZ"
    PositionID = "SL" + Acct2 + Symb2
    Flag2 = "Position"
    QueryPosition = Flag2 + "|" + PositionID + "|" + Id2 # 如果PositionID为空，返回所有
    #
    Id3 = str(uuid.uuid1())
    Flag3 = "Order"
    LocalId = "131234" # 已报委托的用户指定编号
    QueryOrder = Flag3 + "|" + LocalId + "|" + Id3 # 如果localID为空，返回所有
    #
    content = QueryAccount + "&" + QueryPosition+"&"+QueryOrder
    return content
##########################################################################################################


#下单函数，orders_str为下单内容
def DoSend(orders_str):
    with contextlib.closing(mmap.mmap(-1, 1024, tagname='OrderSendQ', access=mmap.ACCESS_WRITE)) as m:
        #这里写发单的内容
        for i in range(1, 3):
            print(i)
            m.seek(0)
            temp_str = bytes(orders_str, encoding = "utf8")
            m.write(temp_str)
            m.flush()
            time.sleep(0.09999)
            m.write(b" ")
            m.flush()


def DoCancel(cancel_str):
    with contextlib.closing(mmap.mmap(-1, 1024, tagname='OrderCancelQ', access=mmap.ACCESS_WRITE)) as m:
        #这里写发单的内容
        for i in range(1, 3):
            print(i)
            m.seek(0)
            temp_str = bytes(cancel_str, encoding = "utf8")
            m.write(temp_str)
            m.flush()
            time.sleep(0.09999)
            m.write(b" ")
            m.flush()


def DoQuery(query_str):
    with contextlib.closing(mmap.mmap(-1, 1024, tagname='InfoQueryQ', access=mmap.ACCESS_WRITE)) as m:
        #这里写发单的内容
        for i in range(1, 3):
            print(i)
            m.seek(0)
            temp_str = bytes(query_str, encoding = "utf8")
            m.write(temp_str)
            m.flush()
            time.sleep(0.09999)
            m.write(b" ")
            m.flush()

response_value = ""

async def get_ws():
    uri = "ws://localhost:12306/Ws"
    async with websockets.connect(uri) as websocket:
        greeting = await websocket.recv()
        global response_value
        response_value = greeting

def response():
    asyncio.get_event_loop().run_until_complete(get_ws())
    return response_value


def quit(signum, frame):
    print('')
    print('stop fusion')
    sys.exit()


def get_response():
    signal.signal(signal.SIGINT, quit)                                
    signal.signal(signal.SIGTERM, quit)
    while(True):
        #这里获取成交回报
        response_value = response() 
        print("get message : ", response_value)
        return response_value

if __name__ == "__main__":

    DoSend(buildSendInfo())
    DoCancel(buildCancelInfo())
    DoQuery(buildQueryInfo())