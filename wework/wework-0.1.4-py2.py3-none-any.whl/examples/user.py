from wework.CorpApi import CorpApi, CORP_API_TYPE
from wework.AbstractApi import ApiException

from conf import TestConf

api = CorpApi(TestConf['CORP_ID'], TestConf['CONTACT_SYNC_SECRET'])

try:
    response = api.httpCall(
        CORP_API_TYPE['USER_CREATE'],
        {
            'userid': 'userid1',
            'name': 'zhangsanfeng',
            'mobile': '131488888888',
            'email': 'zhangsan@ipp.cas.cn',
            'department': 1,
        })
    print(response)
    response = api.httpCall(
        CORP_API_TYPE['USER_GET'],
        {
            'userid': 'userid1',
        })
    print(response)
    response = api.httpCall(
        CORP_API_TYPE['USER_DELETE'],
        {
            'userid': 'userid1',
        })
    print(response)
except ApiException as e:
    print(e.err_code, e.err_msg)
    response = api.httpCall(
        CORP_API_TYPE['USER_DELETE'],
        {
            'userid': 'userid1',
        })
    print(response)
