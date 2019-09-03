import datetime
import json
from typing import List, Dict, Union

import requests
from requests import Response


class BotmanApi:
    def __init__(self, base_url: str, token: str):
        self.base_url = base_url + "{path}"
        self.token = token
        self.last_response = None

    def _headers(self) -> dict:
        return {"X-API-KEY": self.token}

    def _parse_response(self, response: Response):
        if "application/json" in response.headers.get('content-type', "") and response.content:
            content = json.loads(response.content.decode('utf-8'))
            return content
        else:
            return {}

    def _post(self, endpoint: str, data: dict = None) -> dict:
        response = requests.post(endpoint, json=data, headers=self._headers(), verify=False, timeout=5)
        self.last_response = response
        result = self._parse_response(response)
        return result

    def _get(self, endpoint: str, params: dict = None) -> dict:
        try:
            response = requests.get(endpoint, params=params, headers=self._headers(), verify=False, timeout=5)
            self.last_response = response
            result = self._parse_response(response)
            return result
        except (requests.exceptions.ConnectionError, requests.exceptions.Timeout):
            return {}

    def get_bot_status(self) -> bool:
        endpoint = self.base_url.format(path='bot/status')
        content = self._get(endpoint)
        if content.get('success', False):
            return content['data']['status']
        else:
            return False

    def get_api_status(self) -> bool:
        endpoint = self.base_url.format(path='status')
        content = self._get(endpoint)
        if content.get('success', False):
            return content['data']['status']
        else:
            return False

    def start_bot(self) -> bool:
        endpoint = self.base_url.format(path='bot/start')
        content = self._post(endpoint)
        return content.get('success', False)

    def stop_bot(self) -> bool:
        endpoint = self.base_url.format(path='bot/stop')
        content = self._post(endpoint)
        return content.get('success', False)

    def restart_bot(self) -> bool:
        endpoint = self.base_url.format(path='bot/restart')
        content = self._post(endpoint)
        return content.get('success', False)

    def get_data(self, table: str, columns: List[str] = None, limit: int = 300, offset: int = 0, ordering: int = 1) -> List[Dict]:
        endpoint = self.base_url.format(path=f'bot/data/{table}')

        params = {
            "columns": ", ".join(columns) if columns else None,
            "limit": limit,
            "offset": offset,
            "ordering": ordering
        }
        content = self._get(endpoint, params=params)
        if content.get('success', False):
            return content['data']
        else:
            return []

    def get_specific_data(self, table: str, data_id: Union[int, str], columns: List[str] = None) -> dict:
        endpoint = self.base_url.format(path=f'bot/data/{table}/{data_id}')

        params = {
            "columns": ", ".join(columns) if columns else None,
        }
        content = self._get(endpoint, params=params)
        if content.get('success', False):
            return content['data']
        else:
            return {}

    def count_data(self, table: str) -> int:
        endpoint = self.base_url.format(path=f'bot/data/{table}/count')

        content = self._get(endpoint, params={})
        if content.get('success', False):
            return content['data']
        else:
            return -1

    def distribution(self, text: str, when: datetime.datetime = None) -> bool:
        endpoint = self.base_url.format(path='bot/distribution')
        data = {
            "text": text,
        }
        if when:
            data.update(when=when.isoformat())

        content = self._post(endpoint, data=data)
        return content.get('success', False)

    def send_message(self, chat_id: Union[int, str], text: str) -> bool:
        endpoint = self.base_url.format(path='bot/messages/send')
        data = {
            "chat_id": chat_id,
            "text": text,
        }

        content = self._post(endpoint, data=data)
        return content.get('success', False)
