import unittest

import httpretty
import requests

from dli import __version__
from dli.client.dli_client import Session
from dli.client.exceptions import (
    DatalakeException,
    InsufficientPrivilegesException,
    UnAuthorisedAccessException
)


class SessionTestCase(unittest.TestCase):

    valid_token = "eyJ0eXAiOiJKV1QiLCJhbGciOiJIUzI1NiIsImlhdCI6MTUxMzMzMTUwOSwiZXhwIjo5NTEzMzM1MTA5fQ.e30.fjav6VOdXAnE6WgUwSxEbrNuiqQBSEalOd177F9UrCM"
    expired_token = "eyJ0eXAiOiJKV1QiLCJhbGciOiJIUzI1NiIsImlhdCI6MTUxMzMzMTUwOSwiZXhwIjoxNTEzMzM1MTA5fQ.e30.-vTTDvptpjPrG2PO1GBo1OOlBqvx6D_gPGnU7Tw-YII"

    def test_can_decode_valid_jwt_token(self):
        ctx = Session(
            "key",
            "root",
            None,
            self.valid_token
        )
        self.assertFalse(ctx.has_expired)

    def test_can_detect_token_is_expired(self):
        ctx = Session(
            "key",
            "root",
            None,
            self.expired_token
        )
        self.assertTrue(ctx.has_expired)

    def test_when_token_cant_be_decoded_then_we_assume_no_session_expiration(self):
        ctx = Session(
            "key",
            "root",
            None,
            "invalid.token"
        )
        self.assertFalse(ctx.has_expired)


class SessionRequestFactoryTestCase(unittest.TestCase):

    @httpretty.activate
    def test_response_403_raises_InsufficientPrivilegesException(self):
        response_text = 'Insufficient Privileges'
        httpretty.register_uri(httpretty.GET, 'http://dummy.com/test', status=403, body=response_text)

        session = Session(None, 'http://dummy.com', None, lambda: {})

        with self.assertRaises(InsufficientPrivilegesException):
            requests.Session().send(session.request_factory(method='GET', url='/test').prepare())

    @httpretty.activate
    def test_response_401_raises_UnAuthorisedAccessException(self):
        response_text = 'UnAuthorised Access'
        httpretty.register_uri(httpretty.GET, 'http://dummy.com/test', status=401, body=response_text)

        session = Session(None, 'http://dummy.com', None, lambda: {})

        with self.assertRaises(UnAuthorisedAccessException):
            requests.Session().send(session.request_factory(method='GET', url='/test').prepare())

    @httpretty.activate
    def test_response_500_raises_DatalakeException(self):
        response_text = 'Datalake server error'
        httpretty.register_uri(httpretty.GET, 'http://dummy.com/test', status=500, body=response_text)

        session = Session(None, 'http://dummy.com', None, lambda: {})

        with self.assertRaises(DatalakeException):
            requests.Session().send(session.request_factory(method='GET', url='/test').prepare())

    @httpretty.activate
    def test_sdk_version_is_included_in_header(self):
        httpretty.register_uri(httpretty.GET, 'http://dummy.com/test', status=200, body="response")
        session = Session(None, 'http://dummy.com', None, lambda: {})

        # issue a request
        requests.Session().send(session.request_factory(method='GET', url='/test').prepare())

        request = httpretty.last_request()
        self.assertTrue("X-Data-Lake-SDK-Version" in request.headers)
        self.assertEqual(request.headers["X-Data-Lake-SDK-Version"], str(__version__))
