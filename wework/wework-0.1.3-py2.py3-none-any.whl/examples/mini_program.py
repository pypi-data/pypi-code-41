from wework.AbstractApi import ApiException
from wework.CorpApi import CorpApi, CORP_API_TYPE

from conf import TestConf

api = CorpApi(TestConf['CORP_ID'], TestConf['APP_SECRET'])

try:
    response = api.httpCall(
        CORP_API_TYPE['MINIPROGRAM_CODE_TO_SESSION_KEY'],
        {
            "js_code": "sVqtL3itg0L30LTGJtZ_isKC0efG5FqGw470fVp8Dpw",
            "grant_type": "authorization_code"
        })
    print(response)
except ApiException as e:
    print(e.err_code, e.err_msg)
