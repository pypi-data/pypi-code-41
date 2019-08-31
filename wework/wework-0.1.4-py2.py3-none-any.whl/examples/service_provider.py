from wework.AbstractApi import ApiException
from wework.ServiceProviderApi import ServiceProviderApi, SERVICE_PROVIDER_API_TYPE
from .conf import *

api = ServiceProviderApi('CORPID', 'PROVIDER_SECRET')

try :
    response = api.httpCall(
            SERVICE_PROVIDER_API_TYPE['GET_LOGIN_INFO'],
            { 
                'auth_code' : 'XXXXXXX',
            })
    print(response)
except ApiException as e :
    print(e.err_code, e.err_msg)
