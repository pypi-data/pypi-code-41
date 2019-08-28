import os
import urllib
import binascii
import json
import requests
from django.test import LiveServerTestCase
from apiview.annotations import Bytes

class TestViews(LiveServerTestCase):

    def setUp(self):
        self.url = self.live_server_url

    def get_url(self, url):
        return urllib.parse.urljoin(self.live_server_url, url)
    
    def test01(self):
        url = self.get_url("/test/ping")
        response = requests.get(url)
        data = json.loads(response.content)
        assert data["result"] == "pong"

    def test02(self):
        url = self.get_url("/test/timestamp")
        response = requests.get(url)
        data = json.loads(response.content)
        assert isinstance(data["result"], int)

    def test03(self):
        url = self.get_url("/test/echo")
        params = {
            "msg": "hello world"
        }
        response = requests.get(url, params=params)
        data = json.loads(response.content)
        assert data["result"] == params["msg"]

    def test04(self):
        url = self.get_url("/test/getBooleanResult")
        params = {
            "value": "yes"
        }
        response = requests.get(url, params=params)
        data = json.loads(response.content)
        assert data["result"] is True

    def test05(self):
        url = self.get_url("/test/getBooleanResult")
        params = {
            "value": False
        }
        response = requests.get(url, params=params)
        data = json.loads(response.content)
        assert data["result"] is False

    def test06(self):
        url = self.get_url("/test/getIntegerResult")
        params = {
            "value": 123
        }
        response = requests.get(url, params=params)
        data = json.loads(response.content)
        assert data["result"] == 123


    def test07(self):
        url = self.get_url("/test/getIntegerResult")
        params = {
            "value": "123"
        }
        response = requests.get(url, params=params)
        data = json.loads(response.content)
        assert data["result"] == 123

    def test08(self):
        url = self.get_url("/test/getBytesResult")
        bts = os.urandom(32)
        params = {
            "value": binascii.hexlify(bts).decode(),
        }
        response = requests.get(url, params=params)
        data = json.loads(response.content)
        assert Bytes(data["result"]) == bts

