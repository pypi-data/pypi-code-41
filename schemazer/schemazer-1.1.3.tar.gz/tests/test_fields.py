import unittest

from flask import Flask, request, json
from werkzeug.exceptions import HTTPException

from schemazer import Query, RequestValidator
from schemazer.commons.errors import RequestErrors
from tests import TestSchema


class TestRequestValidator(unittest.TestCase):
    def get_abort_response_data(self, abort_response):
        self.assertTrue(hasattr(abort_response, 'response'))
        return json.loads(abort_response.response.get_data())

    def setUp(self):
        self.validator = RequestValidator()
        self.schema = TestSchema()
        self.app = Flask(__name__)

    def test_missing_required_parameter(self):
        """
        Request with missing required parameter.
        """
        with self.app.test_request_context():
            request.query = Query()
            try:
                self.validator.process(
                    self.schema.test.test_method.parameters)
            except HTTPException as abort_response:
                error = self.get_abort_response_data(abort_response)
                assert error
                self.assertIn('error', error.keys())
                error = error['error']
                assert error.get('code')
                assert RequestErrors.BadRequest.code == error['code']
                assert error.get('failure_param')

    def test_wrong_format_parameter(self):
        """
        Request with wrong parameters.
        """
        with self.app.test_request_context():
            request.query = Query()
            request.query.args = {'email': 'wrong'}
            try:
                self.validator.process(
                    self.schema.test.test_method.parameters)
            except HTTPException as abort_response:
                error = self.get_abort_response_data(abort_response)
                assert error
                self.assertIn('error', error.keys())
                error = error['error']
                assert error.get('code')
                assert RequestErrors.BadRequest.code == error['code']
                assert error.get('failure_param')


if __name__ == '__main__':
    unittest.main()
