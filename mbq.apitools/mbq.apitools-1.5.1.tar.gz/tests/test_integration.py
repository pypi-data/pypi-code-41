import json

from django.test import RequestFactory, SimpleTestCase

from mbq.api_tools import fields, responses
from mbq.api_tools.exceptions import ImmediateResponseError
from mbq.api_tools.views import view


class TruePermission:
    def has_permission(self, *args, **kwargs):
        return True


class ErrorHandlingTests(SimpleTestCase):
    status_codes_to_responses = {
        400: responses.ClientErrorResponse,
        403: responses.UnauthorizedResponse,
        404: responses.NotFoundResponse,
        405: responses.MethodNotAllowedResponse,
        422: responses.ServerValidationErrorResponse,
        500: responses.ServerErrorResponse,
    }

    def test_error_responses(self):
        @view(permissions=[TruePermission], params={"status_code": fields.Int()})
        def view_func(request):
            response_class = self.status_codes_to_responses[request.params.status_code]

            return response_class("unique_error_code", "here are the details")

        for status_code in self.status_codes_to_responses:
            request = RequestFactory().get("/some-url", {"status_code": status_code})

            response = view_func(request)

            self.assertEqual(response.status_code, status_code)
            self.assertEqual(response.data["error_code"], "unique_error_code")
            self.assertEqual(response.data["detail"], "here are the details")

    def test_immediate_response_exception(self):
        @view(permissions=[TruePermission])
        def view_func(request):
            raise ImmediateResponseError(
                responses.ClientErrorResponse(
                    "unique_error_code", "here are the details"
                )
            )

        request = RequestFactory().get("/some-url")
        response = view_func(request)

        self.assertEqual(response.status_code, 400)
        self.assertEqual(response.data["error_code"], "unique_error_code")
        self.assertEqual(response.data["detail"], "here are the details")


class MediaTypeTests(SimpleTestCase):
    def test_bad_json(self):
        @view("POST", permissions=[TruePermission], payload={"foo": fields.String})
        def view_func(request):
            return responses.DetailResponse()

        request = RequestFactory().post("/some-url", "}---f", content_type="text")
        response = view_func(request)

        self.assertEqual(response.status_code, 415)

        request = RequestFactory().post(
            "/some-url", "}---f", content_type="application/json"
        )
        response = view_func(request)

        self.assertEqual(response.status_code, 415)


class UnknownFieldsTests(SimpleTestCase):
    def test_unknown_payload_field_settings(self):
        @view(
            "POST",
            permissions=[TruePermission],
            payload={"foo": fields.String(default=None)},
        )
        def view_func(request):
            return responses.DetailResponse()

        factory = RequestFactory()

        request = factory.post(
            "/some-url", json.dumps({"bar": "fizz"}), content_type="application/json"
        )

        with self.settings(API_TOOLS={}):
            response = view_func(request)

        self.assertEqual(response.status_code, 400)

        with self.settings(API_TOOLS={"UNKNOWN_PAYLOAD_FIELDS": "exclude"}):
            response = view_func(request)

        self.assertEqual(response.status_code, 200)

    def test_unknown_param_field_settings(self):
        @view(permissions=[TruePermission], params={"foo": fields.String(default=None)})
        def view_func(request):
            return responses.DetailResponse()

        factory = RequestFactory()

        request = factory.get(
            "/some-url", {"bar": "fizz"}, content_type="application/json"
        )

        with self.settings(API_TOOLS={}):
            response = view_func(request)

        self.assertEqual(response.status_code, 400)

        with self.settings(API_TOOLS={"UNKNOWN_PARAM_FIELDS": "exclude"}):
            response = view_func(request)

        self.assertEqual(response.status_code, 200)

    def test_unknown_override(self):
        @view(
            permissions=[TruePermission],
            params={"foo": fields.String(default=None)},
            on_unknown_field="exclude",
        )
        def view_func(request):
            return responses.DetailResponse()

        factory = RequestFactory()

        request = factory.get(
            "/some-url", {"bar": "fizz"}, content_type="application/json"
        )

        with self.settings(API_TOOLS={"UNKNOWN_PARAM_FIELDS": "raise"}):
            response = view_func(request)

        self.assertEqual(response.status_code, 200)
