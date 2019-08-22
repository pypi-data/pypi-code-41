import requests
from json import JSONDecodeError
from time import time
from difflib import SequenceMatcher

from .exceptions import ComagicException

VALID_ENDPOINTS = (
    "calls_report", "communications_report", "virtual_numbers", "available_virtual_numbers",
    "sip_line_virtual_numbers", "sip_lines", "sip_line_password", "scenarios", "media_files",
    "campaigns","campaign_available_phone_numbers","campaign_available_redirection_phone_numbers",
    "campaign_parameter_weights", "sites", "site_blocks", "call_legs_report", "goals_report",
    "chats_report", "chat_messages_report", "offline_messages_report", "visitor_sessions_report",
    "financial_call_legs_report", "tags", "employees", "customers", "campaign_daily_stat",
)

VALID_METHODS = (
    "get", "delete", "create", "update", "upload"
)

class _Session(object):
    API_URL = 'https://dataapi.comagic.ru/v2.0'

    def __init__(self, login="", password="", token=""):
        if (login and password) or token:
            self.login = login
            self.password = password
            self._session = requests.Session()
            self._session.headers.update({
                "Content-Type": "application/json"
            })
            self.access_token = self._create_access_token() if not token else token
        else:
            raise ValueError("miss auth params (login, passwod) or token")

    
    def _send_api_request(self, params, counter=0):
        if counter > 3:
            raise ComagicException({"code": -32001, "message": "Invalid login or password"})
        try:
            resp = self._session.post(self.API_URL, json=params).json()
        except (JSONDecodeError, requests.ConnectionError) as e:
            raise ComagicException({"code": 502, "message": f"{e}"})
        if "error" in resp:
            if resp['error']['code'] == -32001:
                counter += 1
                return self._send_api_request(params, counter)
            raise ComagicException(resp['error'])
        return resp['result']['data']


    def _create_access_token(self):
        params = {
			"jsonrpc": "2.0",
			"id": f"req_call{int(time())}",
			"method": "login.user",
			"params": {
				"login": self.login,
				"password": self.password
			}
		}
		
        resp = self._send_api_request(params)
        return resp['access_token']


    def _get_endpoint(self, method, endpoint, user_id=None, date_form="", date_to="", filter={}, data={}):
        default_params = {
			"jsonrpc": "2.0",
			"id": f"req_call{time()}",
			"method": f"{method}.{endpoint}",
            "limit": 10000,
			"params": {
				"access_token": self.access_token
			}
		}
        if date_form and date_to:
            default_params.update({"date_from": date_form, "date_till": date_to})
        if filter:
            default_params.update({"filter": filter})
        if user_id:
            default_params.update({"user_id": user_id})
        if data:
            default_params['params'].update(**data)
        return self._send_api_request(default_params)


class Comagic(object):
    def __init__(self, login='', password='', token=''):
        self.login = login
        self.password = password
        self._session = _Session(login, password, token)
        self.access_token = self._session.access_token

    def __getattr__(self, endpoint):
        if endpoint not in VALID_ENDPOINTS:
            mean_endpoitns = [e for e in VALID_ENDPOINTS if SequenceMatcher(None, endpoint, e).ratio() >= 0.8]
            raise ValueError(f"invalid enpoint - {endpoint}, mb you mean - {mean_endpoitns}")
        return _Request(self, endpoint)


    def __call__(self, endpoint, method_kwargs={}):
        return getattr(self, endpoint)(method_kwargs)



class _Request(object):
    __slots__ = ('_api', '_params')

    def __init__(self, api, method_name):
        self._api = api
        self._params = method_name


    def __getattr__(self, method_name):
        if method_name not in VALID_METHODS:
            raise ValueError(f"{method_name} - invalid method, must be in {VALID_METHODS}")
        return _Request(self._api, {'endpoint':self._params,'method': method_name})



    def __call__(self, user_id=None, date_from="", date_to="", filter={}, data={}):
        if not isinstance(filter, dict) or not isinstance(data, dict):
            raise ValueError("filter or data must be a dict")

        return self._api._session._get_endpoint(
            endpoint=self._params['endpoint'],
            method=self._params['method'],
            user_id=user_id,
            date_form=date_from,
            date_to=date_to,
            filter=filter,
            data={}
        )