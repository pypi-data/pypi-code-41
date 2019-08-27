from simple_rest_client.api import API
from simple_rest_client.resource import Resource
from vgscli.keyring_token_util import KeyringTokenUtil

token_util = KeyringTokenUtil()
CLIENT_ID = 'vgs-cli-public'
SCOPE = 'openid'

env_url = {
    'dev': 'https://auth.verygoodsecurity.io',
    'sandbox': 'https://auth.verygoodsecurity.com',
    'live': 'https://auth.verygoodsecurity.com'
    }

class AuthResource(Resource):
    actions = {
        'token': {'method': 'POST', 'url': 'auth/realms/vgs/protocol/openid-connect/token'}
    }


def create_api(environment):
    api = API(
        api_root_url=env_url[environment],
        params={},  # default params
        headers={
        },  # default headers
        timeout=50,  # default timeout in seconds
        append_slash=False  # append slash to final url
    )
    api.add_resource(resource_name='auth', resource_class=AuthResource)
    return api


def get_token(api, code, code_verifier, callback_url):
    payload = {'code': code,
               'grant_type': 'authorization_code',
               'code_verifier': str(code_verifier),
               'client_id': 'vgs-cli-public',
               'redirect_uri': callback_url}
    return api.auth.token(body=payload)


def refresh_token(api):
    payload = {'refresh_token': token_util.get_refresh_token(),
               'grant_type': 'refresh_token',
               'client_id': CLIENT_ID}

    return api.auth.token(body=payload)
