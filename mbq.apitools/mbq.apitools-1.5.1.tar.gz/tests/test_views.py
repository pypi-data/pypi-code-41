import json
from unittest.mock import Mock

from django.http import QueryDict
from django.test import SimpleTestCase

from mbq.api_tools import fields, permissions
from mbq.api_tools.responses import (
    ClientErrorResponse,
    DetailResponse,
    MethodNotAllowedResponse,
    UnauthorizedResponse,
)
from mbq.api_tools.views import View, view


class TruePermissionStub:
    def has_permission(self, request, view):
        return True


class FalsePermissionStub:
    def has_permission(self, request, view):
        return False


class FalsePermissionWithMessageStub:
    message = "Ah ah ah! You didn't say the magic word!"

    def has_permission(self, request, view):
        return False


def view_func(request):
    return DetailResponse()


class ViewFunctionTests(SimpleTestCase):
    def setUp(self):
        super().setUp()
        self.request = Mock(body="", method="GET", GET=QueryDict())

    def test_permissions_required(self):
        with self.assertRaises(TypeError):
            view(permissions=[])(view_func)

        response = view(permissions=[permissions.NoAuthorization])(view_func)(
            self.request
        )
        self.assertTrue(isinstance(response, DetailResponse))

    def test_perform_authorization_drf_class(self):
        self.assertTrue(
            isinstance(
                view(permissions=[TruePermissionStub])(view_func)(self.request),
                DetailResponse,
            )
        )

        response = view(permissions=[FalsePermissionStub])(view_func)(self.request)

        self.assertTrue(isinstance(response, UnauthorizedResponse))
        self.assertTrue(response.data["detail"], "Authorization Failed")

        response = view(permissions=[FalsePermissionWithMessageStub])(view_func)(
            self.request
        )

        self.assertTrue(isinstance(response, UnauthorizedResponse))
        self.assertTrue(
            response.data["detail"], "Ah ah ah! You didn't say the magic word!"
        )

        self.assertTrue(
            isinstance(
                view(permissions=[FalsePermissionStub, TruePermissionStub])(view_func)(
                    self.request
                ),
                UnauthorizedResponse,
            )
        )

    def test_perform_authorization_function(self):
        wrapped_view = view(permissions=[lambda x: True])(view_func)
        response = wrapped_view(self.request)
        self.assertTrue(isinstance(response, DetailResponse))

        wrapped_view = view(permissions=[lambda x: False])(view_func)
        response = wrapped_view(self.request)
        self.assertTrue(isinstance(response, UnauthorizedResponse))

    def test_method_not_allowed(self):
        self.assertTrue(
            isinstance(
                view("POST", permissions=[TruePermissionStub], payload={})(view_func)(
                    self.request
                ),
                MethodNotAllowedResponse,
            )
        )
        self.assertTrue(
            isinstance(
                view("GET", permissions=[TruePermissionStub])(view_func)(self.request),
                DetailResponse,
            )
        )

    def test_params(self):
        request = Mock(body="", GET=QueryDict("foo=bar&fizz=1"), method="GET")

        def view_func(request):
            return DetailResponse(request.params.as_dict())

        param_schema = {"foo": fields.String(), "fizz": fields.Int()}

        decorated_view = view(permissions=[TruePermissionStub], params=param_schema)(
            view_func
        )

        response = decorated_view(request)

        self.assertEqual(response.data, {"foo": "bar", "fizz": 1})

        request.GET = QueryDict("foo=1")
        response = decorated_view(request)
        self.assertTrue(isinstance(response, ClientErrorResponse))

    def test_payload(self):
        payload = {"foo": "bar", "fizz": 1}

        request = Mock(
            body=json.dumps(payload).encode("utf-8"), GET=QueryDict(), method="POST"
        )

        def view_func(request):
            return DetailResponse(request.payload.as_dict())

        param_schema = {"foo": fields.String(), "fizz": fields.Int()}

        decorated_view = view(
            "POST", permissions=[TruePermissionStub], payload=param_schema
        )(view_func)

        response = decorated_view(request)

        self.assertEqual(response.data, {"foo": "bar", "fizz": 1})

        request.body = json.dumps({"foo": 1}).encode("utf-8")
        response = decorated_view(request)
        self.assertTrue(isinstance(response, ClientErrorResponse))


class TestView(View):
    @view.method("POST", permissions=[TruePermissionStub], payload={})
    def get(self, request):
        return DetailResponse()


class ViewTests(SimpleTestCase):
    def test_method_not_allowed(self):
        request = Mock(method="GET", body="", GET=QueryDict())

        self.assertTrue(
            isinstance(TestView.as_view()(request), MethodNotAllowedResponse)
        )

        request.method = "POST"

        self.assertTrue(isinstance(TestView.as_view()(request), DetailResponse))

    def test_method_must_be_decorated(self):
        class TestView(View):
            def get(self, request):
                return DetailResponse()

        with self.assertRaises(TypeError):
            TestView.as_view()
