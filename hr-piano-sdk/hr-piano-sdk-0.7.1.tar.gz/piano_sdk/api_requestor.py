import json
import error
import requests
import piano_sdk


class HTTPMethods(object):
    POST = 'post'
    GET = 'get'


class APIRequestor(object):

    def __init__(self, aid=None, token=None, api_base=None):
        self.aid = aid or piano_sdk.aid
        self.api_token = token or piano_sdk.api_token
        self.api_base = api_base or piano_sdk.api_base

    def _add_auth(self, payload):
        if payload is None:
            payload = {}

        payload = payload.copy()
        payload['api_token'] = self.api_token
        payload['aid'] = self.aid
        return payload

    def request(self, method, url, params=None, data=None, headers=None, json=None):
        if method == HTTPMethods.GET or json is not None:
            params = self._add_auth(params)
        else:
            data = self._add_auth(data)

        full_url = '{}/{}'.format(self.api_base, url)
        raw_response = requests.request(
            method=method, url=full_url, params=params, data=data, json=json, headers=headers
        )

        response = self._interpret_response(
            raw_response.content, raw_response.status_code, raw_response.headers
        )

        return response

    @staticmethod
    def _interpret_response(body, status, headers):
        try:
            json_response = json.loads(body)
        except Exception:
            raise error.APIError(
                'Invalid response body from API: {} (HTTP response code was {})'.format(
                    body, status
                ),
                body, status, headers)

        code = json_response.pop('code')
        if code != 0:
            message = json_response.get('message')
            if not message:
                message = json_response.get('validation_errors')
            raise error.PianoError(
                message='{} Code: {}'.format(message, code),
                json_body=json_response
            )

        return json_response
