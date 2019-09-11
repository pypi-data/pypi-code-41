import hashlib
import hmac

import requests


class HTTPTokenAuth(requests.auth.AuthBase):
    def __init__(self, token):
        self.token = token

    def __call__(self, r):
        r.headers['Authorization'] = f'Token {self.token}'
        return r


class NotiflyClient:
    def __init__(self, host, app_id, app_secret):
        self.host = host
        self.app_id = app_id
        self.app_secret = app_secret

    def _post(self, endpoint, payload, token=None):
        url = f'{self.host}{endpoint}'
        if token is None:
            return requests.post(url, json=payload)

        return requests.post(url, json=payload, auth=HTTPTokenAuth(token))

    def send_notification(self, user_id, notification_type, metadata={}):
        return self._post(
            '/api/notification',
            {
                'type': notification_type,
                'userId': str(user_id),
                'appId': self.app_id,
                'appSecret': self.app_secret,
                'metadata': metadata,
            },
        )

    def create_user(self, user_id, email):
        return self._post(
            '/api/user',
            {
                'appId': self.app_id,
                'appSecret': self.app_secret,
                'userId': str(user_id),
                'email': email,
            },
        )
