import random

from wework.CorpApi import CorpApi, CORP_API_TYPE
from wework.AbstractApi import ApiException

from conf import TestConf

api = CorpApi(TestConf['CORP_ID'], TestConf['APP_SECRET'])

try:
    response = api.httpCall(
        CORP_API_TYPE['MESSAGE_SEND'],
        {
            "touser": "ZhuShengBen",
            "agentid": 1000002,
            'msgtype': 'text',
            'climsgid': 'climsgidclimsgid_%f' % (random.random()),
            'text': {
                'content': '方法论',
            },
            'safe': 0,
        })
    print(response)
except ApiException as e:
    print(e.err_code, e.err_msg)
