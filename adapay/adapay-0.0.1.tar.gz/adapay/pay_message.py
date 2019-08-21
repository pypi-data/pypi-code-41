#!/usr/bin/env python
import threading
import time
import uuid

from paho.mqtt import client as mqtt

import adapay
from adapay.api.api_request import ApiRequestor
from adapay.utils.log_util import log_info


# 2019.7.30 create by jun.hu
class AdapayMessage:
    # 实例 ID，购买后从产品控制台获取
    instance_id = ''
    # 账号AccessKey 从阿里云账号控制台获取
    access_key = ''
    # MQTT GroupID,创建实例后从 MQTT 控制台创建
    group_id = ''
    # MQTT ClientID，由 GroupID 和后缀组成，需要保证全局唯一
    client_id = ''
    # Topic， 其中第一级父级 Topic 需要从控制台创建
    topic = ''
    # MQTT 接入点域名，实例初始化之后从控制台获取
    broker_url = ''

    # 长连接建立结果回调方法
    connect_callback = None
    # 建立监听成功回调
    subscribe_callback = None
    # 收到消息回调方法
    message_received = None

    @staticmethod
    def init():
        AdapayMessage.instance_id = 'post-cn-459180sgc02'
        # AdapayMessage.instance_id = 'post-cn-0pp18zowf0m'

        AdapayMessage.access_key = 'LTAILQZEm73RcxhY'
        # AdapayMessage.access_key = 'LTAIOP5RkeiuXieW'

        AdapayMessage.group_id = 'GID_CRHS_ASYN'

        AdapayMessage.client_id = AdapayMessage.group_id + '@@@' + str(
            hash(adapay.api_key + (str(uuid.uuid1()))))

        AdapayMessage.topic = 'topic_crhs_sender/' + adapay.api_key

        AdapayMessage.broker_url = 'post-cn-459180sgc02.mqtt.aliyuncs.com'
        # AdapayMessage.broker_url = 'post-cn-0pp18zowf0m.mqtt.aliyuncs.com'

    @staticmethod
    def on_log(client, userdata, level, buf):
        log_info(buf)

    @staticmethod
    def on_connect(client, userdata, flags, resp_code):
        """
        建立长连接成功回调
        """
        log_info('connected with result code ' + str(resp_code))

        # 如果这里返回非0，表示长连接成功但是代码有异常
        if AdapayMessage.connect_callback is not None:
            AdapayMessage.connect_callback(resp_code)

        if resp_code == 0:
            client.subscribe(AdapayMessage.topic, 0)

    @staticmethod
    def on_disconnect(client, userdata, resp_code):
        """
        :param resp_code:
         长连接链接失败回调
        1	伪造 Token，不可解析
        2	Token 已经过期
        3	Token 已经被吊销
        4	资源和 Token 不匹配
        5	权限类型和 Token 不匹配
        8	签名不合法
        -1	帐号权限不合法

        :return:
        """
        log_info('unexpected disconnection %s' % resp_code)

        if AdapayMessage.connect_callback is not None:
            AdapayMessage.connect_callback(resp_code)

    @staticmethod
    def on_subscribe(client, userdata, mid, granted_qos):
        """
        订阅成功回调
        """
        log_info('on_subscribe')
        if AdapayMessage.subscribe_callback is not None:
            AdapayMessage.subscribe_callback(0)

    @staticmethod
    def on_unsubscribe(client, userdata, mid):
        """
        订阅成功回调
        """
        log_info('on_unsubscribe')
        if AdapayMessage.subscribe_callback is not None:
            AdapayMessage.subscribe_callback(-1)

    @staticmethod
    def on_message(client, userdata, messages):
        """
        订阅成功回调
        """
        log_info('on_msg_receive:' + str(messages.payload))
        if AdapayMessage.message_received is not None:
            AdapayMessage.message_received(messages)

    @staticmethod
    def execute():
        # 初始化的时候获取 client
        client = mqtt.Client(AdapayMessage.client_id, protocol=mqtt.MQTTv311, clean_session=True)
        client.on_log = AdapayMessage.on_log
        client.on_connect = AdapayMessage.on_connect
        client.on_disconnect = AdapayMessage.on_disconnect
        client.on_subscribe = AdapayMessage.on_subscribe
        client.on_unsubscribe = AdapayMessage.on_unsubscribe
        client.on_message = AdapayMessage.on_message

        # 签名模式下的设置方法，参考文档
        # https://help.aliyun.com/document_detail/48271.html?spm=a2c4g.11186623.6.553.217831c3BSFry7
        user_name = 'Token|' + AdapayMessage.access_key + '|' + AdapayMessage.instance_id
        token = AdapayMessage._request_token()
        password = 'R|' + token
        client.username_pw_set(user_name, password)
        client.connect(AdapayMessage.broker_url, 1883, 60)
        client.loop_forever()

    @staticmethod
    def _request_token():
        # todo 超时时间 取消token 是都不需要调用
        expire_time = int(round(time.time() * 1000)) + 1000000
        data = ApiRequestor.request(adapay.base_url + '/v1/token/apply', 'post', {'expire_time': expire_time})

        if 'succeeded' != data.get('status'):
            log_info('token request failed')

        return data.get('token', '')

    @staticmethod
    def subscribe(on_message_received):
        AdapayMessage.on_message_received = on_message_received
        mqtt_thread = threading.Thread(target=AdapayMessage.execute)
        mqtt_thread.start()


if __name__ == '__main__':
    import logging
    import os
    from fishbase import set_log_stdout

    adapay.log_level = logging.INFO
    set_log_stdout()
    # sep = os.sep
    # dirname, filename = os.path.split(os.path.abspath(__file__))
    # adapay.base_url = 'http://api.payun.cloud'
    # adapay.api_key = 'api_test_929e9757-e3d3-4575-a823-b0e83ce686c2'
    # adapay.api_key = 'api_live_3128984e-7c0f-4799-8c45-90e673870cb5'
    # adapay.private_key_path = 'D:\project\py_project\configuration_center_server\\application\\api\\rule\\release_private_key.pem'
    # adapay.public_key_path = 'D:\project\py_project\configuration_center_server\\application\\api\\rule\\release_public_key.pem'
    # app_id = 'app_P000002052092068'

    adapay.base_url = 'http://api-test.payun.cloud'
    adapay.private_key_path = 'D:\project\py_project\configuration_center_server\\application\\api\\rule\\test_private_key.pem'
    adapay.public_key_path = 'D:\project\py_project\configuration_center_server\\application\\api\\rule\\test_public_key.pem'

    adapay.api_key = 'api_test_ae8becb6-fe94-4edb-9cea-57028104d9fe'
    # adapay.api_key = 'api_live_4dde9234-f010-45a9-bc31-a8537aa118eb'

    AdapayMessage.init()


    def my_on_message(arg1, arg2, arg3):
        print('on_message_receive!' + arg3.topic + ' !' + str(arg3.payload))


    msg = AdapayMessage.subscribe(my_on_message)
    # msg.execute(my_on_message)
