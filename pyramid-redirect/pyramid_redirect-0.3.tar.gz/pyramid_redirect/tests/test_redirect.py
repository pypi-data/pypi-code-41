# -*- coding: utf-8 -*-

# This software is distributed under the FreeBSD License.
# See the accompanying file LICENSE for details.
#
# Copyright 2012 Benjamin Hepp

import unittest

from pyramid import testing


class TestRedirectTween(unittest.TestCase):

    def setUp(self):
        self.config = testing.setUp()
        self.config.include('pyramid_redirect')

    def tearDown(self):
        testing.tearDown()

    def _makeOne(self):
        from pyramid_redirect import redirect_tween_factory
        return redirect_tween_factory(dummy_handler, self.config.registry)

    def _callFUT(self, request):
        tween = self._makeOne()
        return tween(request)

    def test_redirect_no_rules(self):
        request = testing.DummyRequest(url='http://example.com/abc')
        self._callFUT(request)
        self.assertEqual(request.path_info, r'/')

    def test_redirect_rule1(self):
        self.config.add_redirect_rule(
            r'http://example\.com/abc/qwe(?P<num>[0-9]+)/(?P<op>[a-zA-Z]+)',
            'http://example.com/%(op)s/%(num)s',
        )
        request = testing.DummyRequest(url='http://example.com/abc/qwe15/get')
        result = self._callFUT(request)
        self.assertEqual(result.status_code, 302)
        self.assertEqual(result.location, r'http://example.com/get/15')

    def test_redirect_rule2(self):
        self.config.add_redirect_rule(
            r'http://example\.com/(?P<user>[a-zA-Z0-9_]+)/(?P<what>[a-zA-Z0-9_]+)/(?P<op>[a-zA-Z]+)',  # noqa
            'http://example.com/%(op)s(%(user)s.%(what)s)',
            permanent=False,
        )
        request = testing.DummyRequest(url='http://example.com/root/foo/get')
        result = self._callFUT(request)
        self.assertEqual(result.status_code, 302)
        self.assertEqual(result.location, r'http://example.com/get(root.foo)')

    def test_redirect_rule3(self):
        self.config.add_redirect_rule(
            r'http://example\.com/favicon\.ico',
            'http://example.com/static/favicon.ico',
            permanent=True
        )
        request = testing.DummyRequest(url='http://example.com/favicon.ico')
        result = self._callFUT(request)
        self.assertEqual(result.status_code, 301)
        self.assertEqual(result.location, r'http://example.com/static/favicon.ico')  # noqa

    def test_redirect_rule4(self):
        self.config.add_redirect_rule(
            r'http://example\.com/favicon\.ico',
            'http://example.com/static/favicon.ico')
        request = testing.DummyRequest(url='http://example.com/favicon.icon')
        result = self._callFUT(request)
        self.assertIsNone(result)  # no redirect


def dummy_handler(request):
    return None
