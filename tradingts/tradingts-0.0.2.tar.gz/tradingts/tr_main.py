# -*- coding: utf-8 -*-
"""
Created on Wed Aug 28 14:34:05 2019

@author: TS
"""

import os
import logging
import tornado.web
import tornado.websocket as websocket
import tornado.ioloop
import tornado.options
import time
import queue
import threading
import json
import uuid
from tornado.options import define, options
import mmap
import contextlib
import time


define("port", default=12306, help="run on the given port", type=int)
global content_1

class Application(tornado.web.Application):
    def __init__(self):
        handlers = [
            (r"/", First_Handler),
            (r"/ConnectRequest", Connect_Handler),
            (r"/HeartBeat", HeartBeat_Handler),
            (r"/TaskRequest", Task_Handler),
            (r"/Ws", MyWebSocketHandler),
        ]
        settings = dict(debug=True)
        tornado.web.Application.__init__(self, handlers, **settings)


###############################################################################
class First_Handler(tornado.web.RequestHandler):
    def get(self):
        print("get data from ts")
        self.write("RecvConnFromTS")
        
    def post(self):
        print(self.request.body.decode('utf-8'))
        self.write("RecvConnFromTS")
        MyWebSocketHandler.send_demand_updates(self.request.body.decode('utf-8'))
###############################################################################


class MyWebSocketHandler(websocket.WebSocketHandler):

    # 保存连接的用户，用于后续推送消息
    connect_users = set()

    def open(self):
        #print("WebSocket opened")
        # 打开连接时将用户保存到connect_users中
        self.connect_users.add(self)

    def on_message(self, message):
        print('收到的信息为：' + message)

    def on_close(self):
        #print("WebSocket closed")
        # 关闭连接时将用户从connect_users中移除
        self.connect_users.remove(self)

    def check_origin(self, origin):
        # 此处用于跨域访问
        return True
    
    
    @classmethod
    def send_demand_updates(cls, message):
        # 使用@classmethod可以使类方法在调用的时候不用进行实例化
        # 给所有用户推送消息（此处可以根据需要，修改为给指定用户进行推送消息）
        for user in cls.connect_users:
            user.write_message(message)


###########
# Connect #
################################################################################
class Connect_Handler(tornado.web.RequestHandler):
    def get(self):
        print(time.strftime("%H:%M:%S ", time.localtime()) + "收到TS连接请求")
        self.write("RecvConnFromTS")
###############################################################################


#############
# HeartBeat #
###############################################################################
class HeartBeat_Handler(tornado.web.RequestHandler):
    def get(self):
        print(time.strftime("%H:%M:%S ", time.localtime()) +"收到TS心跳请求")
        self.write("ServerIsAlive")
###############################################################################


##########
# Task #
###############################################################################
class Task_Handler(tornado.web.RequestHandler):
    content_1 = ""
    def get(self):
        #print(time.strftime("%H:%M:%S ", time.localtime())+ "收到TaskRequest")
        #这里将下单内容，查询内容，撤单内容等作为Response返回给TS客户端
        with contextlib.closing(mmap.mmap(-1, 1024, tagname='OrderSendQ', access=mmap.ACCESS_WRITE)) as m:
            OrderSendQ = str(m.read(1024).replace(b'\x00', b''), encoding = "utf-8")

        with contextlib.closing(mmap.mmap(-1, 1024, tagname='OrderCancelQ', access=mmap.ACCESS_WRITE)) as m:
            OrderCancelQ = str(m.read(1024).replace(b'\x00', b''), encoding = "utf-8")

        with contextlib.closing(mmap.mmap(-1, 1024, tagname='InfoQueryQ', access=mmap.ACCESS_WRITE)) as m:
            InfoQueryQ = str(m.read(1024).replace(b'\x00', b''), encoding = "utf-8")
            
        if len(OrderSendQ)>0 or len(OrderCancelQ)>0 or len(InfoQueryQ)>0:
            content=buildJsonFromString(OrderSendQ,OrderCancelQ,InfoQueryQ)

            self.write(content)
            self.flush()
            self.write(" ")
            self.flush()
            #s1 =  str(m.read(1024).replace(b'\x00', b''), encoding = "utf-8")
            #content_1 = content


def buildStringFromQueue(myQueue):
    result = ''
    while(not myQueue.empty()):
        item=myQueue.get(True, timeout=0.1)
        result += item+'&'
    return result

def buildJsonFromString(sendInfo, cancelInfo, queryInfo):
    dict ={}
    if len(sendInfo)>0:
        dict['DoSend'] = sendInfo
    if len(cancelInfo)>0:
        dict['DoCancel'] = cancelInfo
    if len(queryInfo)>0:
        dict['DoQuery'] = queryInfo
    result = json.dumps(dict)
    return result
###############################################################################


################
# start Server #
###############################################################
def startServer():
    tornado.options.parse_command_line()
    app = Application()
    app.listen(options.port)
    tornado.ioloop.IOLoop.instance().start()
    print(time.strftime("%H:%M:%S ", time.localtime()) + "server start now")
#################################################################


#########
#set Log#
########################################################################################################
def log_fun():
    logger = logging.getLogger()
    logger.setLevel(logging.INFO)

    logpath = os.path.dirname(os.getcwd()) +"/"+time.strftime('%Y%m%d',time.localtime(time.time()))+'.log'
    fh = logging.FileHandler(logpath,mode='w')
    fh.setLevel(logging.DEBUG)
    fh.setFormatter(logging.Formatter("%(asctime)s - %(filename)s[line:%(lineno)d] - %(levelname)s: %(message)s"))
    logger.addHandler(fh)

OrderSendQ = queue.Queue()  # 存储下单指令
OrderCancelQ = queue.Queue()  # 存储撤单指令
InfoQueryQ = queue.Queue()  # 存储查询指令

def main_fun():
    try:
        startServer()
    except Exception as ex:
        print("stop by : ", ex)

#######
if __name__ == "__main__":
    log_fun()
    main_fun()