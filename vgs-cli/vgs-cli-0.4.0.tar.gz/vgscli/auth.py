import json
import sys
import jwt
import requests
import getpass

from calendar import timegm
from vgscli.auth_server import AuthServer
from datetime import datetime
from jwt import DecodeError
from vgscli.utils import eprint, to_json
from vgscli.keyring_token_util import KeyringTokenUtil

token_util = KeyringTokenUtil()
TOKEN_FILE_NAME = 'vgs_token'


def handshake(config, environment):
    try:
        auth_server = AuthServer(environment)
        if config == {}:
            token_util.validate_refresh_token()
            if not token_util.validate_access_token():
                auth_server.refresh_authentication()
        else:
            token_util.validate_access_token()
    except Exception as e:
        raise AuthenticateException("Authentication error occurred:" + e.args[0])


def login(config, environment):
    try:
        auth_server = AuthServer(environment)
        # For now we keep old approach with config.yaml working. In case of emergency we need to have alternative way of authentication for now.
        if config == {}:
            return auth_server.authenticate(environment)
        else:
            return __get_access_token(config)
    except Exception as e:
        raise AuthenticateException("Authentication error occurred:" + e.args[0])


def logout():
    token_util.clear_tokens()
    token_util.remove_encryption_secret()


def __get_access_token(config):
    if __can_login_auth0(config):
        username = __enter_username()
        password = __enter_password()
        auth0_access_token = __login_auth0_username_password(config, username, password)
        return __token_exchange(config, auth0_access_token)

    eprint("Please set up config.yaml file, see https://www.verygoodsecurity.com/docs/api/1/cli", fatal=True)


def __login_auth0_username_password(config, username, password):
    login_data = {
        "client_id": config.get("auth0_client_id"),
        "client_secret": config.get("auth0_client_secret"),
        "grant_type": "http://auth0.com/oauth/grant-type/password-realm",
        "username": username,
        "password": password,
        "scope": "openid",
        "realm": "Username-Password-Authentication"
    }
    login_headers = {
        "Content-Type": "application/json"
    }
    token_response = requests.post(config.get("auth0_url"), headers=login_headers, data=json.dumps(login_data))
    parsed_response = to_json(token_response)

    if "mfa_token" in parsed_response:
        print('Please enter your MFA code:', file=sys.stderr)
        mfa = input('')
        mfa_token = parsed_response["mfa_token"]
        mfa_data = {
            "client_id": config.get("auth0_client_id"),
            "client_secret": config.get("auth0_client_secret"),
            "grant_type": "http://auth0.com/oauth/grant-type/mfa-otp",
            "username": username,
            "password": password,
            "scope": "openid",
            "realm": "Username-Password-Authentication",
            "otp": mfa,
            "mfa_token": mfa_token
        }
        mfa_headers = {
            "Content-Type": "application/json"
        }

        token_response = requests.post(config.get("auth0_url"), headers=mfa_headers, data=json.dumps(mfa_data))
    elif "error" in parsed_response:
        print("Unexpected error: {}, {}".format(
            parsed_response["error"],
            parsed_response.get("error_description", "")
        ),
            file=sys.stderr
        )
        sys.exit(1)

    parsed = to_json(token_response)
    if 'error' in parsed:
        raise Exception(parsed['error_description'])
    return parsed['access_token']


def __can_login_auth0(config):
    config_elements = [
        config.get("auth0_url"),
        config.get("auth0_client_id"),
        config.get("auth0_client_secret"),

        config.get("kc_server_url"),
        config.get("kc_realm"),
        config.get("kc_client_id"),
        config.get("kc_client_secret"),
        config.get("kc_oidc_provider_alias"),
    ]
    return None not in config_elements


def __token_exchange(config, auth0_access_token):
    token_exchange_url = __get_token_exchange_url(config)
    data = {
        'grant_type': 'urn:ietf:params:oauth:grant-type:token-exchange',
        'subject_token': auth0_access_token,
        'subject_issuer': config.get("kc_oidc_provider_alias"),
        'subject_token_type': 'urn:ietf:params:oauth:token-type:access_token',
        'audience': config.get("kc_client_id")
    }
    response = requests.post(token_exchange_url, data=data,
                             auth=(config.get("kc_client_id"), config.get("kc_client_secret")))
    __store_tokens(response)
    return __parse_access_token(response)


def __get_token_exchange_url(config):
    return config.get("kc_server_url") + '/realms/' + config.get(
        "kc_realm") + '/protocol/openid-connect/token'


def __parse_access_token(response):
    parsed = to_json(response)
    if 'error' in parsed:
        raise Exception(parsed['error_description'])
    return parsed['access_token']


def __store_tokens(response):
    parsed = to_json(response)
    if 'error' in parsed:
        raise Exception(parsed['error_description'])
    token_util.put_tokens(parsed)


def __enter_username():
    eprint('Enter your username: ')
    try:
        username = input('')
    except EOFError:
        eprint('Please use "vgs authenticate" before providing input file stream', fatal=True)
    return username


def __enter_password():
    return getpass.getpass('Enter your password: ')


def __valid_expiration(token):
    decoded_token = jwt.decode(token, verify=False)
    now = timegm(__current_time())

    try:
        exp = int(decoded_token['exp'])
    except ValueError:
        raise DecodeError('Expiration Time claim (exp) must be an'
                          ' integer.')

    if exp < now:
        eprint('Credentials are expired. Please re-enter.')
        return False

    return True


def __current_time():
    return datetime.utcnow().utctimetuple()


class AuthenticateException(Exception):
    def __init__(self, arg):
        self.message = arg
