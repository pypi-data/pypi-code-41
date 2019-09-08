import json
import requests
from datetime import datetime, timedelta
import os
import websocket

AUTHENTICATION_HOST = 'https://api.authentication.husqvarnagroup.dev/v1/oauth2/token'
SMART_HOST_LOCATION = 'https://api.smart.gardena.dev/v1/locations'
SMART_HOST_WEBSOCKET = 'https://api.smart.gardena.dev/v1/websocket'

class Gardena(object):
    """Class to take care of cummunication with Gardena Smart system"""
    def __init__(self, email_address=None, password=None, api_key=None):
        if email_address ==None or password==None:
            raise ValueError('Please provide, email, password')
        self.debug=True
        self.s = requests.session()
        self.email_address = email_address
        self.password = password
        self.api_key = api_key
        self.update()

    def update(self):
        self.update_authtokens()
        self.get_locations()

    def update_authtokens(self):
        """Get authentication token from servers"""
        payload = {'grant_type': 'password', 'username': self.email_address, 'password': self.password,
               'client_id': self.api_key}

        print("Logging into authentication system...")
        r = requests.post(AUTHENTICATION_HOST, data=payload)
        assert r.status_code == 200, r
        auth_token = r.json()["access_token"]
        self.authToken = r.json()["access_token"]

    def get_locations(self):
        print("Getting locationid...")
        headers = {
            "Content-Type": "application/vnd.api+json",
            "x-api-key": self.api_key,
            "Authorization-Provider": "husqvarna",
            "Authorization": "Bearer " + self.authToken
        }

        r = requests.get(SMART_HOST_LOCATION, headers=headers)
        assert r.status_code == 200, r
        assert len(r.json()["data"]) > 0, 'location missing - user has not setup system'

        self.locationId = r.json()["data"][0]["id"]

    def get_websocket_url(self):
        print("Getting websocketurl...")
        payload = {
            "data": {
                "type": "WEBSOCKET",
                "attributes": {
                    "locationId": self.locationId
                },
                "id": "does-not-matter"
            }
        }
        headers = {
            "Content-Type": "application/vnd.api+json",
            "x-api-key": self.api_key,
            "Authorization-Provider": "husqvarna",
            "Authorization": "Bearer " + self.authToken
        }
        print("Logged in (%s), getting WebSocket ID..." % self.authToken)
        r = requests.post(SMART_HOST_WEBSOCKET, json=payload, headers=headers)

        assert r.status_code == 201, r
        print("WebSocket ID obtained, connecting...")
        response = r.json()
        self.websocket_url = response["data"]["attributes"]["url"]

    def debug_print(self, string):
        if self.debug:
            print(string)
