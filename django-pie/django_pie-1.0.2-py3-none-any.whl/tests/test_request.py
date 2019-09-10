# coding: utf-8
import json

from django.test import TestCase
from django.http.request import HttpRequest

from django_pie.decorator import test_print
from django_pie.request import request_get, RequestException, request_post, request_data, request_headers


class TestRequest(TestCase):
    def setUp(self):
        pass

    @test_print
    def test_request_get_post(self):
        params = {
            'foo': 'bar',
            'p1': 2,
        }
        request = HttpRequest()
        request.GET = params
        request.POST = params
        foo = request_get(request, 'foo')
        self.assertEqual(foo, params['foo'])
        foo = request_post(request, 'foo')
        self.assertEqual(foo, params['foo'])

        result = True
        try:
            p1 = request_get(request, 'p1', min_value=1, max_value=1)
            result = False
        except RequestException:
            self.assertEqual(result, True)

        try:
            result = True
            request_get(request, 'p2', required=False)
            result = False
        except RequestException:
            pass
        self.assertEqual(result, False)

        try:
            result = True
            request_get(request, 'p2')
            result = False
        except RequestException:
            self.assertEqual(result, True)

    @test_print
    def test_request_data(self):
        request = HttpRequest()
        params = {
            'foo': 'bar',
            'p1': 2,
        }
        request._body = json.dumps(params)
        foo = request_data(request, 'foo')
        self.assertEqual(foo, params['foo'])

    @test_print
    def test_request_headers(self):
        request = HttpRequest()
        params = {
            'HTTP_FOO': 'bar',
            'HTTP_P1': 2,
            'CONTENT_TYPE': 'json',
        }
        request.META = params
        foo = request_headers(request, 'foo')
        self.assertEqual(foo, params['HTTP_FOO'])
        content_type = request_headers(request, 'content-type')
        self.assertEqual(content_type, params['CONTENT_TYPE'])
