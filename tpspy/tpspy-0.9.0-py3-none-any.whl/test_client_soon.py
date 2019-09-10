# -*- coding: utf-8 -*-


import os
import time
import requests
import random
import string
import json
import copy
from tpspy.client import Client

TPS_SYS_ID = os.getenv("TPS_SYS_ID", '')
TPS_SYS_SECRET = os.getenv("TPS_SYS_SECRET", '')

client = Client(sys_id=TPS_SYS_ID, sys_secret=TPS_SYS_SECRET, tps_base_url="http://127.0.0.1:8000/")


# client = Client(sys_id=TPS_SYS_ID, sys_secret=TPS_SYS_SECRET, tps_base_url="https://tencent.qq.com/")


# client = Client(sys_id=TPS_SYS_ID, sys_secret=TPS_SYS_SECRET, tps_base_url="https://test.tencent.qq.com/")


def test_api():
    r = client.api_tapd_tencent(method="GET", path="bugs.json", params={
        "workspace_id": 10066461,
        "title": "QAPM"
    })
    print(r)
    assert isinstance(r, dict) and r.get("code") == 10000


def test_message(run_once=False):
    """
    测试消息服务是否正常
    :return:
    """

    def check_results(result, success=True):
        if not isinstance(result, dict):
            result = json.loads(result)
        if success and result.get('code', -1) != 10000:
            raise Exception("test_message find error, expect success. result: %s" % str(result))
        elif not success and result.get('code', -1) == 10000:
            raise Exception("test_message find error, expect fail. result: %s" % str(result))
        print("check_results, passed")

    # for soonflywang
    to = ["1356761908@qq.com", "soonflywang"]
    to_outer = "1356761908@qq.com"

    # for kangtian
    # to = ["", "", "kangtian"]
    # to_outer = ""

    # for all
    # to = ["", "", "kangtian", "soonflywang"]
    # to_outer = ""

    to_chat = '13294344628055079709'
    to_key = '489b78c9-1769-49c5-ae6e-6aff219429d6'  # webhook
    content = dict(
        title="快递到达通知",
        body="\n # Hi, 您的快递到了 ! <h1>这是H1<h1>",
        pic_url="https://p.qpic.cn/pic_wework/3685288192/c8cedbc46b2c0d0b3e67f273eace5834d49e2dec5885fd8b/0",
        detail_url="https://work.weixin.qq.com/api/doc#90000/90135/90248"
    )
    # r = client.message_chat_create("磁盘性能告警", "soonflywang", "soonflywang;cocoding")
    # print("MESSAGE_CHAT_CREATE ", r)
    # check_results(r) 11931442790810100946
    # r = client.message_send(msg_type=client.MessageChannel.WECHAT_WORK_GROUP_CHAT_TEXT, to='',
    #                         content=dict(
    #                             title="test",
    #                             body="test"
    #                         ))
    # print("WECHAT_WORK_GROUP_CHAT_TEXT, ", r)
    # check_results(r)
    # r = client.message_chat_info(chat_id='13118141292632216683')
    # print("MESSAGE_CHAT_INFO", r)
    # check_results(r)
    # return ''
    r = client.message_send(msg_type=client.MessageChannel.WECHAT_WORK_APP_PUSH_TEXT, to=to, content=content)
    print("WECHAT_WORK_APP_PUSH_TEXT, ", r)
    check_results(r)

    if run_once:
        return ''

    # user
    r = client.message_send(msg_type=client.MessageChannel.WECHAT, to=to, content=content)
    print("WECHAT, ", r)
    check_results(r)

    r = client.message_send(msg_type=client.MessageChannel.WECHAT_WORK_APP_PUSH_NEWS, to=to, content=content)
    print("WECHAT_WORK_APP_PUSH_NEWS, ", r)
    check_results(r)

    r = client.message_send(msg_type=client.MessageChannel.MAIL, to=to, content=content)
    print("MAIL, ", r)
    check_results(r)

    r = client.message_send(msg_type=client.MessageChannel.MAIL_OUTER, to=to_outer, content=content)
    print("MAIL_OUTER, , ", r)
    check_results(r)

    r = client.message_send(msg_type=client.MessageChannel.MAIL_OUTER, to=to, content=content)
    print("MAIL_OUTER, but send inner, should be error", r)
    check_results(r, success=False)

    r = client.message_send(msg_type=client.MessageChannel.WECHAT_WORK_APP_PUSH_TEXT, to=to, content=content)
    print("WECHAT_WORK_APP_PUSH_TEXT, ", r)
    check_results(r)

    r = client.message_send(msg_type=client.MessageChannel.WECHAT_WORK_APP_PUSH_CARD, to=to, content=content)
    print("WECHAT_WORK_APP_PUSH_CARD, ", r)
    check_results(r)

    # web hook
    r = client.message_send(msg_type=client.MessageChannel.WECHAT_WORK_GROUP_ROBOT_TEXT, to=to_key, content=content)
    print("WECHAT_WORK_GROUP_ROBOT_TEXT, ", r)
    check_results(r)

    r = client.message_send(msg_type=client.MessageChannel.WECHAT_WORK_GROUP_ROBOT_MD, to=to_key, content=content)
    print("WECHAT_WORK_GROUP_ROBOT_MD, ", r)
    check_results(r)

    # chat
    r = client.message_send(msg_type=client.MessageChannel.WECHAT_WORK_GROUP_CHAT_TEXT, to=to_chat, content=content)
    print("WECHAT_WORK_GROUP_CHAT_TEXT, ", r)
    check_results(r)

    r = client.message_send(msg_type=client.MessageChannel.WECHAT_WORK_GROUP_CHAT_CARD, to=to_chat, content=content)
    print("WECHAT_WORK_GROUP_CHAT_CARD, ", r)
    check_results(r)

    r = client.message_send(msg_type=client.MessageChannel.WECHAT_WORK_GROUP_CHAT_NEWS, to=to_chat, content=content)
    print("WECHAT_WORK_GROUP_CHAT_NEWS, ", r)
    check_results(r)

    # multi
    msg_types = ",".join([
        client.MessageChannel.WECHAT,
        client.MessageChannel.WECHAT_WORK_APP_PUSH_NEWS,
        client.MessageChannel.WECHAT_WORK_APP_PUSH_TEXT])
    r = client.message_send(msg_type=msg_types, to=to, content=content)
    print("MULTICHANNEL MSG, ", r)
    check_results(r)
    #
    r = client.message_chat_info(chat_id='11931442790810100946')
    print("MESSAGE_CHAT_INFO", r)
    check_results(r)

    # 短信发送的，目前不可用
    # r = client.message_send(msg_type=client.MessageChannel.SMS, to=to, content=content)
    # print("SMS, ", r)
    # check_results(r)

    # # 创建群聊的
    # r = client.message_chat_create("磁盘性能告警", "soonflywang", "soonflywang;cocoding")
    # print("MESSAGE_CHAT_CREATE ", r)
    # check_results(r)


def test_metrics_resource_flow_upload():
    resp = client.metrics_resource_flow_upload(data=[
        {
            "time_start": float(time.time()),
            "time_end": float(time.time()) + 5,
            "namespace": "athena",
            "resource": "uba.ui_action",
            "stage": "entrance_init",
            "state": "ok",
            "value": 1,

        },
    ])
    print("resp.text: ", resp)


def test_metrics_resource_flow_get():
    resp = client.metrics_resource_flow_get(params={
        "filter": {
            "time_start__range": ["2019-03-06", "2019-03-07"],
            "sys_id": "qapm",
            "namespace": "tencent_qq",
            "category": "2",
        },
        "aggregate": True,
        "aggr": {
            "group_by": ['namespace', 'resource'],
            "aggr_by": "value",
            "aggr_func": "sum"
        }
    })
    print("resp.text: ", resp)


def test_metrics_upload():
    resp = client.metrics_upload(data=[
        {
            "name": "test_kb_sec",
            "time_start": float(time.time()),
            "d1": "cluster_a",
            "value": 1.3,
        },
    ])
    print("resp.text: ", resp)


def test_send_message():
    s = """{"content":{"body":"你有一份邮件等待查收！","detail_url":"https://work.weixin.qq.com","pic_url":"https://p.qpic.cn","title":"test01"},"to":["weisong","weisong"],"type":"WECHAT_WORK_APP_PUSH_TEXT,MAIL"}""".encode(
        "utf8")
    resp = requests.post(client.tps_base_url + "api/v1/message/send", data=s, headers=client.get_headers)
    print(resp.text)


def test_audit():
    f = {"identify": "1232323212dssdsd232", "category": "API_ACCESS", "time": "2019-02-26 22:23:02.829000",
         "who": "soon",
         "success": True, "code": "200", "protocol": "_ACCESS", "data": {"data": "test"}, "value": 1,
         "code_msg": "success",
         "dimension1": "tps_api", "dimension2": None, "dimension3": None, "dimension4": None, "dimension5": None}
    f_list = []
    for i in range(0, 1):
        f_temp = copy.deepcopy(f)
        f_temp['identify'] = ''.join(random.sample(string.ascii_letters + string.digits, 8))
        f_list.append(f_temp)
    print(client.audit_add_event(f_list))


def test_tapd_outer():
    try:
        from urllib.parse import urljoin
    except ImportError:
        from urlparse import urljoin
    f = {
        'workspace_id': 22075271,
        'title': '121212',
        'reporter': 'allan',
        'current_owner': 'allan',
        'description': 'asas',
        'api_user': '', 'api_pwd': ''
    }
    data = dict(
        type='TAPD_OUTER',
        to='allan',
        content=dict(
            title='测试',
            body='测试测试测试测试'
        ),
        ctx=f
    )
    print(json.dumps(data))
    url = urljoin(client.tps_base_url, "api/v1/message/send")
    resp = requests.get(url, json=data, headers=client.auth_headers)
    return resp.json()


def test_tapd():
    try:
        from urllib.parse import urljoin
    except ImportError:
        from urlparse import urljoin
    f = {
        'workspace_id': 20393802,
        'title': 'API TEST2',
        'reporter': 'kangtian',
        'current_owner': 'kangtian',
        'description': '1212121212'
    }
    data = dict(
        type='TAPD',
        to='kangtian',
        content=dict(
            title='API TEST',
            body='1212'
        ),
        ctx=f
    )
    print(json.dumps(data))
    url = urljoin(client.tps_base_url, "api/v1/message/send")
    resp = requests.get(url, json=data, headers=client.auth_headers)
    return resp.json()


if __name__ == "__main__":
    # print(test_tapd_outer())
    # test_api()
    test_message(run_once=False)
    # test_audit()
    # test_metrics_resource_flow_upload()
    # test_metrics_resource_flow_get()
    # test_metrics_upload()
    # test_send_message()
