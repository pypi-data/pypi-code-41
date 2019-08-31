from wework.CorpApi import CorpApi, CORP_API_TYPE
from wework.AbstractApi import ApiException
from conf import TestConf

api = CorpApi(TestConf['CORP_ID'], TestConf['APPROVAL_APP_SECRET'])

if __name__ == '__main__':
    try:
        response = api.httpCall(CORP_API_TYPE['GET_APPROVAL_DATA'],
                                {
                                    "starttime": 1566871220,
                                    "endtime": 1566874224
                                })
        print(response)
    except ApiException as e:
        print(e.err_code, e.err_msg)
