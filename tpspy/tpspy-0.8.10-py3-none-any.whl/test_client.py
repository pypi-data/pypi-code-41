# -*- coding: utf-8 -*-

import os
import time
import requests
import json

from tpspy.permission.permission import ClientPermission

from tpspy.client import Client

TPS_SYS_ID = os.getenv("TPS_SYS_ID", '')
TPS_SYS_SECRET = os.getenv("TPS_SYS_SECRET", '')


# client = Client(sys_id=TPS_SYS_ID, sys_secret=TPS_SYS_SECRET, tps_base_url="http://127.0.0.1:30180/")
client = Client(sys_id=TPS_SYS_ID, sys_secret=TPS_SYS_SECRET, tps_base_url="https://tencent.qq.com/")
# client = Client(sys_id=TPS_SYS_ID, sys_secret=TPS_SYS_SECRET, tps_base_url="https://test.tencent.qq.com/")
# client = Client(sys_id=TPS_SYS_ID, sys_secret=TPS_SYS_SECRET, tps_base_url="http://59.36.120.236/")
# client = Client(sys_id=TPS_SYS_ID, sys_secret=TPS_SYS_SECRET, tps_base_url="http://tmf.ip:8081/tps/")
# client = Client(sys_id=TPS_SYS_ID, sys_secret=TPS_SYS_SECRET, tps_base_url="http://mbank.95559.com.cn:30025/tps/")


def test_api():
    r = client.api_tapd_tencent(method="GET", path="bugs.json", params={
        "workspace_id": 20393802,
        "title": "QAPM"
    })
    print(r)
    assert isinstance(r, dict) and r.get("code") == 10000


def test_marker_api():
    r = client.api_marker_tencent(method="POST", path="problem", data={
        'title': '卡顿怎么破？',
        'description': 'UI卡顿',
        'username': 'cjzhan',
        'tag_names': '磁盘'
    }, api_token=" ", api_appkey=" ")
    print(r)
    assert isinstance(r, dict) and r.get("code") ==10000


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
    # to = ["1356761908@qq.com", "soonflywang"]
    # to_outer = "1356761908@qq.com"

    # for kangtian
    to = ["kangtian"]
    to_outer = "1356761908@qq.com"

    # for all
    # to = ["", "", "kangtian", "soonflywang"]
    # to_outer = ""

    to_chat = '13294344628055079709'
    to_key = '489b78c9-1769-49c5-ae6e-6aff219429d6'  # webhook
    content = dict(
        title="快递到达通知",
        body="\n # Hi, 您的快递到了呀 ! <h1>这是H1<h1>",
        pic_url="https://p.qpic.cn/pic_wework/3685288192/c8cedbc46b2c0d0b3e67f273eace5834d49e2dec5885fd8b/0",
        detail_url="https://work.weixin.qq.com/api/doc#90000/90135/90248"
    )
    ctx = {
        'workspace_id': 20393802,
        'title': 'test 1',
        'reporter': 'kangtian',
        'current_owner': 'kangtian',
        'description': 'Just a test',
        'api_user': '', 'api_pwd': ''
    }

    r = client.message_send(msg_type=client.MessageChannel.TIPS, to=to, content=content)
    print("TIPS, ", r)
    check_results(r)

    if run_once:
        return ''

    # 消息提醒
    r = client.message_send(msg_type=client.MessageChannel.TIPS, to=to, content=content)
    print("TIPS, ", r)
    check_results(r)

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
    r = client.message_chat_info(chat_id=to_chat)
    print("MESSAGE_CHAT_INFO", r)
    check_results(r)

    # TAPD， 目前没有日常的测试环境，先注释掉
    r = client.message_send(msg_type=client.MessageChannel.TAPD, to=to, content=content, ctx=ctx)
    print("TAPD, ", r)
    check_results(r)
    #
    # r = client.message_send(msg_type=client.MessageChannel.TAPD_OUTER, to=to, content=content, ctx=ctx)
    # print("TAPD_OUTER, ", r)
    # check_results(r)

    # 短信发送的，目前不可用
    # r = client.message_send(msg_type=client.MessageChannel.SMS, to=to, content=content)
    # print("SMS, ", r)
    # check_results(r)

    # # 创建群聊的
    # # r = client.message_chat_create("test", "soonflywang", "soonflywang;kangtian")
    # # print("MESSAGE_CHAT_CREATE ", r)
    # # check_results(r)


def test_metrics_resource_flow_upload():
    resp = client.metrics_resource_flow_upload(data=[
        {
            "time_start": float(time.time()),
            "time_end": float(time.time()) + 5,
            "namespace": "tps",
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
            "time_start__range": ["2019-07-24", "2019-08-29"],
            "sys_id": "tps",
        },
        "aggregate": True,
        "aggr": {
            "group_by": ['time_hour', 'resource'],
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


def test_metrics_get():
    resp = client.metrics_get(params={
        "filter": {
            "time_start__range": ["2019-07-10", "2019-07-13"],
            "sys_id": "tps",
            "name": "entrance_file_cnt",
            "period": "3600seconds",
        },
        "use_rollup": True,
        "aggregate": True,
        "aggr": {
            "group_by": ['time_hour', 'name'],
            "aggr_by": "value",
            "aggr_func": "sum"
        }
    })
    print("resp.text: ", resp)


def test_send_message():
    s = """{"content":{"body":"你有一份邮件等待查收！","detail_url":"https://work.weixin.qq.com","pic_url":"https://p.qpic.cn","title":"test01"},"to":["weisong","weisong"],"type":"WECHAT_WORK_APP_PUSH_TEXT,MAIL"}""".encode(
        "utf8")
    resp = requests.post(client.tps_base_url + "api/v1/message/send", data=s, headers=client.get_headers)
    print(resp.text)


def test_audit_events_upload():
    resp = client.audit_events_upload(data=[
        {
            "identify": "43bc7050-0b37-4c4d-9dc6-01a324c10d81",
            "category": "API_ACCESS",
            "time": "2019-07-21 13:39:22",
            "who": "",
            "success": True,
            "code": "99990",
            "protocol": "_ACCESS",
            "data": {"hello": "1"},
            "value": 1,
        },
    ])
    print("resp.text: ", resp)


def test_auth_add_user():
    permission = ClientPermission(sys_id=TPS_SYS_ID, sys_secret=TPS_SYS_SECRET, tps_base_url="https://tencent.qq.com/")
    bok, msg = permission.add_user("demo", "wode", "WECHAT")
    print(msg)


if __name__ == "__main__":
    # test_api()
    test_message(run_once=False)
    test_metrics_resource_flow_upload()
    test_metrics_resource_flow_get()
    test_metrics_upload()
    # test_auth_add_user()
    # test_send_message()
    # test_metrics_get()
    # test_audit_events_upload()
