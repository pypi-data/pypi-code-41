# coding = utf8
import json

import requests


def send_msg(mobile, title, body, url="http://127.0.0.1:8001/v1/sms/send", user="znsy", pwd="ynkg2019"):
    """
    向短信网关发送SMS信息
    :param user:
    :param title:
    :param pwd:
    :param mobile:
    :param body:
    :param url:
    :return:
    """
    if title == '' or title is None:
        raise ValueError(u'短信标题不能为空！')

    if body == '' or body is None:
        raise ValueError(u'短信内容不能空!')

    response = requests.post(url=url, data={
        'user': user,
        'pwd': pwd,
        'number': mobile,
        'content': "【%s】%s" % (title, body)
    })
    result = json.loads(response.text)
    return result
